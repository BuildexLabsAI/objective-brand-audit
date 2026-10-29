"""Lab performance test (mobile, throttled like Google Lighthouse's default mobile profile).

Usage:  python3 perf.py --audit <audit-dir>
Reads:  audit.json "perf_urls" {"home": url, "category": url, "product": url}
Writes: <audit>/data/perf.json and prints FCP/LCP/CLS/TTFB/weight per page.
The user agent is Lighthouse's own mobile emulation string. Do not change it to get past a block:
if the site refuses this test, stop and report it (see SKILL.md, Landmines).
Label results in the report as our own lab test, not Google field data.
"""
import argparse, json, os
from pathlib import Path
from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument("--audit", required=True)
ROOT = Path(ap.parse_args().audit).expanduser().resolve()
URLS = json.loads((ROOT / "audit.json").read_text(encoding="utf-8"))["perf_urls"]

OBSERVER = """
window.__lcp = 0; window.__cls = 0;
new PerformanceObserver(l => { for (const e of l.getEntries()) window.__lcp = e.startTime; })
  .observe({type: 'largest-contentful-paint', buffered: true});
// CLS = the largest session window: shifts less than 1 s apart, a window at most 5 s long (web.dev/articles/cls)
let win = 0, first = 0, last = 0;
new PerformanceObserver(l => { for (const e of l.getEntries()) {
  if (e.hadRecentInput) continue;
  if (win && e.startTime - last < 1000 && e.startTime - first < 5000) { win += e.value; }
  else { win = e.value; first = e.startTime; }
  last = e.startTime; window.__cls = Math.max(window.__cls, win);
} }).observe({type: 'layout-shift', buffered: true});
"""

def run(p, name, url):
    # $CHROME (a path) wins, as in render_pdf.sh; else the installed Google Chrome
    browser = (p.chromium.launch(executable_path=os.environ["CHROME"], headless=True) if os.environ.get("CHROME")
               else p.chromium.launch(channel="chrome", headless=True))
    ctx = browser.new_context(viewport={"width": 412, "height": 823}, device_scale_factor=1.75,
                              is_mobile=True, has_touch=True,
                              user_agent="Mozilla/5.0 (Linux; Android 11; moto g power (2022)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0 Mobile Safari/537.36")
    page = ctx.new_page()
    cdp = ctx.new_cdp_session(page)
    cdp.send("Network.enable")
    cdp.send("Network.emulateNetworkConditions", {"offline": False, "latency": 150,
             "downloadThroughput": 1.6 * 1024 * 1024 / 8, "uploadThroughput": 750 * 1024 / 8})
    cdp.send("Emulation.setCPUThrottlingRate", {"rate": 4})
    page.add_init_script(OBSERVER)
    sizes = {"total": 0, "script": 0, "image": 0, "count": 0}
    def on_resp(r):
        try:
            b = len(r.body())
        except Exception:
            return
        sizes["total"] += b; sizes["count"] += 1
        rt = r.request.resource_type
        if rt in ("script", "image"):
            sizes[rt] += b
    page.on("response", on_resp)
    resp = page.goto(url, wait_until="load", timeout=120000)
    if resp is None or resp.status >= 400:
        browser.close()
        raise SystemExit(f"perf: {name} {url} answered {resp.status if resp else 'nothing'}; the site refuses the lab test, report it and stop")
    page.wait_for_timeout(6000)
    m = page.evaluate("""() => {
      const fcp = performance.getEntriesByName('first-contentful-paint')[0];
      const nav = performance.getEntriesByType('navigation')[0];
      return {fcp: fcp ? fcp.startTime : null, lcp: window.__lcp, cls: window.__cls,
              ttfb: nav.responseStart, load: nav.loadEventEnd};
    }""")
    browser.close()
    m.update({k: round(v / 1024) if k != "count" else v for k, v in sizes.items()})
    return m

with sync_playwright() as p:
    out = {}
    for name, url in URLS.items():
        out[name] = run(p, name, url)
        r = out[name]
        s = lambda ms: "none" if not ms else f"{ms / 1000:.1f}s"  # a page that paints nothing has no FCP/LCP
        print(f"{name}: FCP {s(r['fcp'])}  LCP {s(r['lcp'])}  CLS {r['cls']:.3f}  TTFB {r['ttfb']:.0f}ms  "
              f"load {r['load']/1000:.1f}s  weight {r['total']} KB (JS {r['script']} KB, img {r['image']} KB, {r['count']} requests)")
    dest = ROOT / "data/perf.json"
    dest.parent.mkdir(exist_ok=True)
    json.dump(out, open(dest, "w"), indent=1)
    print(f"wrote {dest}; copy the FCP/LCP ranges (s) and JS size (MB) into audit.json 'speed' after checking them")
