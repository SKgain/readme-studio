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
        btns = sorted(glob.glob(f"{out}/assets/btn-*.svg"))
        if btns:
            parts.append("<p>" + "".join(f'<img src="file://{b}" style="margin-right:6px">' for b in btns) + "</p>")
        for name in ("stack", "graph"):
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
            pg = b.new_page(viewport={"width": 940, "height": 900})
            pg.goto(f"file://{html}")
            pg.wait_for_timeout(int(at * 1000))
            pg.screenshot(path=f"{out}/preview-{theme}.png", full_page=True)
            b.close()
        os.remove(html)
        print(f"{out}/preview-{theme}.png")


if __name__ == "__main__":
    main()
