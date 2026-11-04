#!/usr/bin/env python3
# readme-studio/scripts/preview.py
"""
Screenshot the generated assets the way GitHub shows them, in both themes.

Usage:
    python3 preview.py OUT_DIR [--at SECONDS]

Writes OUT_DIR/preview-dark.png and OUT_DIR/preview-light.png.
--at picks the moment of the animation to capture (default 3.3s, after the
graph has finished building). Needs Playwright plus Chrome or Chromium; exits
quietly with a note when neither is available.
"""
import glob, os, shutil, sys


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    out = os.path.abspath(sys.argv[1])
    at = float(sys.argv[sys.argv.index("--at") + 1]) if "--at" in sys.argv else 3.3
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("preview skipped: playwright is not installed (pip install playwright)")
        return
    exe = next((p for p in (shutil.which("google-chrome"), shutil.which("chromium"), shutil.which("chromium-browser")) if p), None)

    for theme, bg in (("dark", "#0D1117"), ("light", "#FFFFFF")):
        parts = []
        hero = f"{out}/assets/hero-{theme}.svg"
        if os.path.exists(hero):
            parts.append(f'<img src="file://{hero}">')
        btns = sorted(glob.glob(f"{out}/assets/btn-*-{theme}.svg"))
        if btns:
            parts.append("<p>" + "".join(f'<img src="file://{b}" style="margin-right:6px">' for b in btns) + "</p>")
        f = f"{out}/assets/stack-{theme}.svg"
        if os.path.exists(f):
            parts.append(f'<img src="file://{f}" style="display:block;margin:12px 0">')
        cards = sorted(glob.glob(f"{out}/assets/card-*-{theme}.svg"))
        if cards:
            parts.append("<p>" + "".join(f'<img src="file://{c}" style="width:49%;margin:0 1% 8px 0">' for c in cards) + "</p>")
        for name in ("timeline", "focus", "graph"):
            f = f"{out}/assets/{name}-{theme}.svg"
            if os.path.exists(f):
                parts.append(f'<img src="file://{f}" style="display:block;margin:12px 0">')
        html = f"{out}/.preview-{theme}.html"
        open(html, "w").write(f'<body style="margin:20px;background:{bg}">{"".join(parts)}</body>')
        with sync_playwright() as p:
            kw = {"args": ["--no-sandbox"]}
            if exe:
                kw["executable_path"] = exe
            try:
                b = p.chromium.launch(**kw)
            except Exception as e:  # no browser available
                print(f"preview skipped: {e.__class__.__name__}")
                return
            # tall viewport: headless Chrome pauses animations in images outside the visible area
            pg = b.new_page(viewport={"width": 940, "height": 4000})
            pg.goto(f"file://{html}")
            pg.wait_for_timeout(int(at * 1000))
            height = pg.evaluate("Math.ceil(Math.max(...[...document.images].map(i => i.getBoundingClientRect().bottom))) + 20")
            pg.screenshot(path=f"{out}/preview-{theme}.png", clip={"x": 0, "y": 0, "width": 940, "height": height})
            b.close()
        os.remove(html)
        print(f"{out}/preview-{theme}.png")


if __name__ == "__main__":
    main()
