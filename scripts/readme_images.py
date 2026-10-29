"""Make the README pictures from the sample report that tests/run_all.py builds.

Usage:  python3 tests/run_all.py && python3 scripts/readme_images.py
Writes: docs/images/sample-report-desktop.png (the first screen at 1440 px).
"""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "tests/out/sample-audit/outputs/harborpine-audit.html"
OUT = ROOT / "docs/images"
if not HTML.exists():
    raise SystemExit(f"readme_images: missing {HTML}; run python3 tests/run_all.py first")
OUT.mkdir(parents=True, exist_ok=True)


def chrome(p):
    """$CHROME (a path) wins, as in render_pdf.sh; else the installed Google Chrome."""
    if os.environ.get("CHROME"):
        return p.chromium.launch(executable_path=os.environ["CHROME"], headless=True)
    return p.chromium.launch(channel="chrome", headless=True)


with sync_playwright() as p:
    browser = chrome(p)
    for name, w, h in (("desktop", 1440, 900),):
        page = browser.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
        page.goto(HTML.as_uri(), wait_until="load")
        page.wait_for_timeout(300)
        page.screenshot(path=OUT / f"sample-report-{name}.png")
        page.close()
    browser.close()
print(f"wrote {sorted(p.name for p in OUT.glob('sample-report-*.png'))}")
