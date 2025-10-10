import os
import json
from functools import partial
from concurrent.futures import ThreadPoolExecutor

import tornado.ioloop
import tornado.web

from app.db import create_pool, init_schema, upsert_ohlc_bars, fetch_ohlc_bars
from app.mt5_client import client as mt5_client


EXECUTOR = ThreadPoolExecutor(max_workers=2)


class MainHandler(tornado.web.RequestHandler):
    async def get(self):
        self.render("index.html")


class FetchHandler(tornado.web.RequestHandler):
    def initialize(self, pool):
        self.pool = pool

    async def get(self):
        symbol = self.get_argument("symbol", default="XAUUSD")
        timeframe = self.get_argument("tf", default="H1").upper()
        count = int(self.get_argument("count", default="500"))

        loop = tornado.ioloop.IOLoop.current()
        fetch_fn = partial(mt5_client.fetch_bars, symbol, timeframe, count)
        try:
            bars = await loop.run_in_executor(EXECUTOR, fetch_fn)
        except Exception as e:
            self.set_status(500)
            self.finish({"ok": False, "error": str(e)})
            return

        inserted = await upsert_ohlc_bars(self.pool, bars)
        self.finish({"ok": True, "symbol": symbol, "timeframe": timeframe, "inserted": inserted})


class DataHandler(tornado.web.RequestHandler):
    def initialize(self, pool):
        self.pool = pool

    async def get(self):
        symbol = self.get_argument("symbol", default="XAUUSD")
        timeframe = self.get_argument("tf", default="H1").upper()
        limit = int(self.get_argument("limit", default="500"))
        rows = await fetch_ohlc_bars(self.pool, symbol, timeframe, limit)
        self.set_header("Content-Type", "application/json")
        self.finish(json.dumps({"symbol": symbol, "timeframe": timeframe, "rows": rows}))


async def make_app():
    pool = await create_pool()
    await init_schema(pool)

    settings = dict(
        debug=True,
        template_path=os.path.join(os.path.dirname(__file__), "..", "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "..", "static"),
    )
    return tornado.web.Application(
        [
            (r"/", MainHandler),
            (r"/api/fetch", FetchHandler, dict(pool=pool)),
            (r"/api/data", DataHandler, dict(pool=pool)),
        ],
        **settings,
    )


def main():
    port = int(os.getenv("PORT", "8888"))
    loop = tornado.ioloop.IOLoop.current()

    async def start():
        app = await make_app()
        app.listen(port)
        print(f"Tornado running on http://localhost:{port}")

    loop.run_sync(start)
    loop.start()


if __name__ == "__main__":
    main()

