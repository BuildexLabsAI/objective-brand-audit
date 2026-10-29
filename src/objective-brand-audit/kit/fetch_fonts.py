"""Download a brand's web fonts from Google Fonts into <audit>/media/assets/fonts and write manifest.txt.

Usage:  python3 fetch_fonts.py --audit <audit-dir> "Fira Sans:400,500,600,700" "Fira Sans Condensed:600,700"
manifest.txt lines: family|weight|subset|file|unicode-range (read by build_report.py).
If the brand font is not on Google Fonts (commercial font), pick the closest Google font and say so in findings.md.
"""
import argparse, re, urllib.parse, urllib.request
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--audit", required=True)
ap.add_argument("families", nargs="+", help='"Family Name:400,700"')
a = ap.parse_args()
out = Path(a.audit).expanduser().resolve() / "media/assets/fonts"
out.mkdir(parents=True, exist_ok=True)
q = "&".join("family=" + urllib.parse.quote_plus(f.split(":")[0]) + ":wght@" + ";".join(f.split(":")[1].split(","))
             for f in a.families)
# Google serves woff2 only to modern browsers, so the request names one (this is Google's documented behaviour).
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
req = urllib.request.Request(f"https://fonts.googleapis.com/css2?{q}&display=swap", headers={"User-Agent": UA})
css = urllib.request.urlopen(req, timeout=60).read().decode()
(out / "fonts.css").write_text(css)
keep = []
for subset, body in re.findall(r"/\* ([a-z-]+) \*/\s*@font-face \{(.*?)\}", css, re.S):
    if subset not in ("latin", "latin-ext"):
        continue
    fam = re.search(r"font-family: '([^']+)'", body).group(1)
    w = re.search(r"font-weight: (\d+)", body).group(1)
    url = re.search(r"url\((https[^)]+)\)", body).group(1)
    ur = re.search(r"unicode-range: ([^;]+);", body).group(1)
    fn = f"{fam.replace(' ', '')}-{w}-{subset}.woff2"
    urllib.request.urlretrieve(url, out / fn)
    keep.append((fam, w, subset, fn, ur))
if not keep:
    raise SystemExit("fetch_fonts: Google returned no latin font files; check the family names")
(out / "manifest.txt").write_text("\n".join("|".join(k) for k in keep))
print(f"{len(keep)} font files, {sum((out / k[3]).stat().st_size for k in keep) // 1024} KB -> {out}")
