import os
import json
import traceback
import hashlib
from datetime import datetime
from pathlib import Path
import tempfile
import types

try:
    import pygame  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    stub = types.SimpleNamespace()
    music = types.SimpleNamespace(
        load=lambda *_args, **_kwargs: None,
        play=lambda *_args, **_kwargs: None,
        get_busy=lambda: False,
        stop=lambda: None,
    )
    stub.mixer = types.SimpleNamespace(init=lambda *_args, **_kwargs: None, music=music)
    stub.time = types.SimpleNamespace(wait=lambda *_args, **_kwargs: None)
    pygame = stub  # type: ignore
from openai import OpenAI


class JSONValidationError(Exception):
    def __init__(self, message, json_string=None):
        super().__init__(message)
        self.message = message
        self.json_string = json_string


class JSONParsingError(Exception):
    def __init__(self, message, json_string, text):
        super().__init__(message)
        print("The failed JSON string: \n\n")
        print(json_string)
        self.message = message
        self.json_string = json_string
        self.text = text


class OpenAIRequestJSONBase:
    def __init__(self, use_cache=True, max_retries=3, cache_dir='cache'):
        self.client = OpenAI()  # Assume correct initialization with API key
        self.max_retries = max_retries
        self.use_cache = use_cache
        self.cache_dir = cache_dir
        self.audio_cache_dir = os.path.join(cache_dir, 'audio')
        self.ensure_dir_exists(self.cache_dir)
        self.ensure_dir_exists(self.audio_cache_dir)
        
        # Initialize pygame mixer for audio playback
        try:
            pygame.mixer.init()
        except:
            print("Warning: pygame mixer initialization failed. Audio playback may not work.")

    def ensure_dir_exists(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    def get_cache_file_path(self, prompt, filename=None):
        if filename is None:
            filename = f"{abs(hash(prompt))}.json"
    
        cache_path = os.path.join(self.cache_dir, filename)
        print("cache_path: ", cache_path)
        cache_dir = os.path.dirname(cache_path)
        print("cache_dir: ", cache_dir)
        os.makedirs(cache_dir, exist_ok=True)
        return cache_path

    def get_audio_cache_file_path(self, text, voice, model="tts-1", instructions=""):
        """Generate cache file path for audio based on text, voice, model, and instructions"""
        cache_key = f"{text}_{voice}_{model}_{instructions}"
        file_hash = hashlib.md5(cache_key.encode()).hexdigest()
        filename = f"{file_hash}.mp3"
        cache_path = os.path.join(self.audio_cache_dir, filename)
        return cache_path

    def save_to_cache(self, prompt, response, filename=None):
        file_path = self.get_cache_file_path(prompt, filename=filename)
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump({"prompt": prompt, "response": response}, file, ensure_ascii=False, indent=4)

    def load_from_cache(self, prompt, filename=None):
        file_path = self.get_cache_file_path(prompt, filename=filename)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                cached_data = json.load(file)
                return cached_data["response"]
        return None

    def load_audio_from_cache(self, audio_path):
        if os.path.exists(audio_path):
            return audio_path
        return None

    def save_audio_to_cache(self, audio_data, audio_path):
        with open(audio_path, 'wb') as file:
            file.write(audio_data)
        return audio_path

    def text_to_speech(self, text, voice="coral", model="tts-1", instructions="", response_format="mp3", play_audio=True):
        if self.use_cache:
            audio_cache_path = self.get_audio_cache_file_path(text, voice, model, instructions)
            cached_audio = self.load_audio_from_cache(audio_cache_path)
            if cached_audio:
                print("TTS cache found.")
                if play_audio:
                    self.play_audio(cached_audio)
                return cached_audio

        retries = 0
        while retries < self.max_retries:
            try:
                print(f"Generating speech with OpenAI TTS (attempt {retries + 1})...")
                tts_params = {
                    "model": model,
                    "voice": voice,
                    "input": text,
                    "response_format": response_format
                }
                if instructions and model == "gpt-4o-mini-tts":
                    tts_params["instructions"] = instructions
                response = self.client.audio.speech.create(**tts_params)
                audio_content = response.content
                if self.use_cache:
                    audio_path = self.get_audio_cache_file_path(text, voice, model, instructions)
                    self.save_audio_to_cache(audio_content, audio_path)
                else:
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{response_format}")
                    temp_file.write(audio_content)
                    temp_file.close()
                    audio_path = temp_file.name
                if play_audio:
                    self.play_audio(audio_path)
                return audio_path
            except Exception as e:
                print(f"TTS API error: {e}")
                traceback.print_exc()
                retries += 1
                if retries >= self.max_retries:
                    raise Exception("Maximum retries reached for TTS request.")

    def text_to_speech_stream(self, text, voice="coral", model="tts-1", instructions="", response_format="mp3", play_audio=True):
        try:
            print("Generating speech with OpenAI TTS (streaming)...")
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{response_format}")
            tts_params = {
                "model": model,
                "voice": voice,
                "input": text,
                "response_format": response_format
            }
            if instructions and model == "gpt-4o-mini-tts":
                tts_params["instructions"] = instructions
            with self.client.audio.speech.with_streaming_response.create(**tts_params) as response:
                response.stream_to_file(temp_file.name)
            if play_audio:
                self.play_audio(temp_file.name)
            return temp_file.name
        except Exception as e:
            print(f"TTS streaming API error: {e}")
            traceback.print_exc()
            raise Exception(f"TTS streaming failed: {e}")

    def play_audio(self, audio_path):
        try:
            if not os.path.exists(audio_path):
                print(f"Audio file not found: {audio_path}")
                return
            print(f"Playing audio: {audio_path}")
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
        except Exception as e:
            print(f"Error playing audio: {e}")

    def stop_audio(self):
        try:
            pygame.mixer.music.stop()
        except Exception as e:
            print(f"Error stopping audio: {e}")

    def send_request_with_json_schema(self, prompt, json_schema, system_content="You are an AI.", filename=None, schema_name="response", model=None):
        retries = 0
        if model is None:
            model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt}
        ]

        print("self.use_cache: ", self.use_cache)

        if self.use_cache:
            cached_response = self.load_from_cache(prompt, filename=filename)
            if cached_response:
                print("OpenAI cache found. ")
                return cached_response

        while retries < self.max_retries:
            try:
                print(f"Querying OpenAI with structured outputs (attempt {retries + 1})...")
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    response_format={
                        "type": "json_schema",
                        "json_schema": {
                            "name": schema_name,
                            "strict": True,
                            "schema": json_schema
                        }
                    }
                )
                message = response.choices[0].message
                if message.refusal:
                    raise Exception(f"Request was refused: {message.refusal}")
                parsed_response = json.loads(message.content)
                if self.use_cache:
                    self.save_to_cache(prompt, parsed_response, filename=filename)
                return parsed_response
            except json.JSONDecodeError as e:
                error_msg = f"Failed to decode JSON response: {e}"
                print(error_msg)
                traceback.print_exc()
                retries += 1
                if retries < self.max_retries:
                    messages.append({"role": "system", "content": f"Previous response had JSON parsing error: {error_msg}. Please provide a valid JSON response."})
            except Exception as e:
                error_msg = f"OpenAI API error: {e}"
                print(error_msg)
                traceback.print_exc()
                retries += 1
                if retries < self.max_retries:
                    messages.append({"role": "system", "content": f"Previous request failed: {error_msg}. Please try again."})
        raise Exception("Maximum retries reached without success.")

    def send_simple_request(self, prompt, system_content="You are a helpful AI assistant.", model=None):
        if model is None:
            model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        cache_key = f"{system_content}_{prompt}"
        if self.use_cache:
            cached_response = self.load_from_cache(cache_key)
            if cached_response:
                print("OpenAI simple request cache found.")
                return cached_response

        retries = 0
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt}
        ]

        while retries < self.max_retries:
            try:
                print(f"Querying OpenAI with simple request (attempt {retries + 1})...")
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages
                )
                message = response.choices[0].message
                if message.refusal:
                    raise Exception(f"Request was refused: {message.refusal}")
                response_text = message.content
                if self.use_cache:
                    self.save_to_cache(cache_key, response_text)
                return response_text
            except Exception as e:
                print(f"OpenAI API error: {e}")
                traceback.print_exc()
                retries += 1
                if retries < self.max_retries:
                    messages.append({"role": "system", "content": f"Previous request failed: {error_msg}. Please try again."})
        raise Exception("Maximum retries reached without success.")

    def send_request_with_retry(self, prompt, system_content="You are an AI.", sample_json=None, filename=None):
        if sample_json is None:
            json_schema = {
                "type": "object",
                "additionalProperties": True
            }
        else:
            json_schema = self._convert_sample_to_schema(sample_json)
        return self.send_request_with_json_schema(
            prompt=prompt,
            json_schema=json_schema,
            system_content=system_content,
            filename=filename
        )

    def _convert_sample_to_schema(self, sample_json):
        def get_type_schema(value):
            if isinstance(value, str):
                return {"type": "string"}
            elif isinstance(value, int):
                return {"type": "integer"}
            elif isinstance(value, float):
                return {"type": "number"}
            elif isinstance(value, bool):
                return {"type": "boolean"}
            elif isinstance(value, list):
                if len(value) > 0:
                    return {
                        "type": "array",
                        "items": get_type_schema(value[0])
                    }
                else:
                    return {
                        "type": "array",
                        "items": {"type": "object", "additionalProperties": True}
                    }
            elif isinstance(value, dict):
                properties = {}
                required = []
                for key, val in value.items():
                    properties[key] = get_type_schema(val)
                    required.append(key)
                return {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                    "additionalProperties": False
                }
            else:
                return {"type": "string"}
        return get_type_schema(sample_json)

    def validate_json(self, json_data, sample_json):
        pass

    def parse_response(self, response):
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            raise JSONParsingError("Failed to parse JSON response", response, response)
