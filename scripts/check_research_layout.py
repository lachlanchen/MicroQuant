"""Offline research-dashboard layout checks; never connects to a live backend.

Requires the existing Playwright test installation and a compatible browser.
Viewport/safe-area/text-size fixtures are not Apple device qualification.
"""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright


STAMP = 1792281600
FIXTURES = {
    "/api/status": {
        "now": STAMP, "model": "Fixture research", "broker_stale": True,
        "broker": {"status": "demo_unavailable", "demo_verified": False,
                   "observed_at": STAMP},
        "paper": {"equity": 50, "net_pnl": 0, "closed_trades": 0,
                  "status": "waiting_for_verified_demo_data"},
        "feeds": {"fixture": {"ok": True}}, "analysis": {"status": "ok"},
    },
    "/api/news": [{
        "title": "Synthetic headline · 市場の観測 · أخبار السوق · " + "LongHeadline" * 12,
        "url": "https://example.invalid/fixture", "source": "Synthetic public feed",
        "published": STAMP, "first_seen": STAMP,
    }],
    "/api/analysis": {"observed": STAMP, "payload": {
        "summary": "Synthetic research note for layout checks. " + "EvidenceReference" * 12,
        "risks": ["Long localized content must remain readable at larger text sizes."],
        "next_experiment": "No experiment or financial operation is performed by this fixture.",
    }},
    "/api/events": [{"observed": STAMP, "kind": "fixture_observation",
                     "payload": {"status": "waiting_for_verified_demo_data"}}],
}
FILES = {"/": ("dashboard.html", "text/html"),
         "/assets/dashboard.css": ("dashboard.css", "text/css"),
         "/assets/dashboard.js": ("dashboard.js", "text/javascript")}
SIZES = [(320, 568), (375, 667), (390, 844), (430, 932), (600, 800),
         (700, 700), (701, 700), (820, 1180), (1024, 768), (1366, 900),
         (1536, 960), (844, 390), (390, 300)]


def geometry(page):
    return page.evaluate("""() => ({
        width: innerWidth, scrollWidth: document.documentElement.scrollWidth,
        overflow: [...document.querySelectorAll('main *')].filter(el => {
            const r = el.getBoundingClientRect();
            return r.width && (r.right > innerWidth + 1 || r.left < -1);
        }).slice(0, 8).map(el => el.id || el.tagName),
    })""")


def run(engine, source, output):
    results, errors, unexpected = [], [], []
    with sync_playwright() as playwright:
        browser = getattr(playwright, engine).launch(headless=True)
        context = browser.new_context(service_workers="block")
        requests = []

        def route(request_route):
            request = request_route.request
            url = urlsplit(request.url)
            requests.append((request.method, url.path))
            if request.method != "GET" or url.netloc != "microquant.test":
                unexpected.append((request.method, request.url))
                request_route.abort()
            elif url.path in FILES:
                name, mime = FILES[url.path]
                request_route.fulfill(body=(source / name).read_bytes(), content_type=mime)
            elif url.path in FIXTURES:
                request_route.fulfill(json=FIXTURES[url.path])
            else:
                unexpected.append((request.method, url.path))
                request_route.fulfill(status=404)

        context.route("**/*", route)
        try:
            for width, height in SIZES:
                page = context.new_page()
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.set_viewport_size({"width": width, "height": height})
                page.goto("https://microquant.test/")
                page.locator("#news a").wait_for()
                measured = geometry(page)
                results.append({"test": f"viewport-{width}x{height}", **measured,
                                "passed": measured["scrollWidth"] <= width + 1
                                and not measured["overflow"]})
                if (width, height) in [(390, 844), (1366, 900)]:
                    page.screenshot(path=str(output / f"{engine}-{width}.png"), full_page=True)
                page.close()

            for width in [320, 390, 768, 1366]:
                page = context.new_page()
                page.set_viewport_size({"width": width, "height": 900})
                page.goto("https://microquant.test/")
                page.locator("#news a").wait_for()
                page.evaluate("""() => {
                    const sizes = [...document.querySelectorAll('body, body *')]
                        .map(el => [el, parseFloat(getComputedStyle(el).fontSize)]);
                    for (const [el, size] of sizes) el.style.fontSize = `${size * 2}px`;
                }""")
                measured = geometry(page)
                results.append({"test": f"text-200-percent-{width}", **measured,
                                "passed": measured["scrollWidth"] <= width + 1
                                and not measured["overflow"]})
                page.close()

            page = context.new_page()
            page.set_viewport_size({"width": 390, "height": 844})
            page.goto("https://microquant.test/")
            page.locator("#news a").wait_for()
            page.locator("#news a").focus()
            page.evaluate("""() => {
                window.fixtureNode = document.querySelector('#news a');
                window.fixtureText = document.querySelector('#summary').textContent;
                sessionStorage.setItem('fixture-only', 'preserved');
            }""")
            before = len(requests)
            for width, height in [(820, 1180), (1180, 820), (390, 300), (390, 844)]:
                page.set_viewport_size({"width": width, "height": height})
            retained = page.evaluate("""() => ({
                node: window.fixtureNode === document.querySelector('#news a'),
                focus: document.activeElement === window.fixtureNode,
                text: window.fixtureText === document.querySelector('#summary').textContent,
                storage: sessionStorage.getItem('fixture-only') === 'preserved'
            })""")
            results.append({"test": "resize-state-and-no-network", **retained,
                            "extra_requests": len(requests) - before,
                            "passed": all(retained.values()) and len(requests) == before})
            page.keyboard.press("Shift+Tab")
            keyboard = page.locator(".brand").evaluate("el => document.activeElement === el")
            results.append({"test": "keyboard-links", "passed": keyboard})

            page.add_style_tag(content=":root { --mq-safe-top: 37px; --mq-safe-right: 52px;"
                                       " --mq-safe-bottom: 21px; --mq-safe-left: 9px; }")
            padding = page.locator("main").evaluate("""el => {
                const s = getComputedStyle(el);
                return ['Top', 'Right', 'Bottom', 'Left'].map(x => parseFloat(s['padding' + x]));
            }""")
            measured = geometry(page)
            results.append({"test": "synthetic-asymmetric-safe-area", "padding": padding,
                            "passed": all(a >= b for a, b in zip(padding, [61, 70, 45, 27]))
                            and measured["scrollWidth"] <= 391})
            page.screenshot(path=str(output / f"{engine}-safe-area.png"), full_page=True)
            report = {"engine": engine, "browser_version": browser.version,
                      "source": str(source), "synthetic_data_only": True,
                      "device_qualification": False, "cases": results,
                      "page_errors": errors, "unexpected_requests": unexpected,
                      "passed": all(r["passed"] for r in results) and not errors and not unexpected,
                      "sha256": {name: hashlib.sha256((source / name).read_bytes()).hexdigest()
                                 for name, _ in FILES.values()}}
            (output / f"{engine}.json").write_text(json.dumps(report, indent=2) + "\n")
            print(json.dumps({"engine": engine, "passed": report["passed"],
                              "cases": len(results), "failures": [r for r in results if not r['passed']]}))
            return report["passed"]
        finally:
            context.close()
            browser.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1] / "research/static")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--engine", choices=["chromium", "webkit"], default="chromium")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    raise SystemExit(0 if run(args.engine, args.source, args.output) else 1)


if __name__ == "__main__":
    main()
