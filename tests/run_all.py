"""Skill tests: run the report kit on the invented sample audit and check what it makes.

Usage:  python3 tests/run_all.py
Needs:  Python 3 with Pillow and Playwright, Google Chrome (or CHROME=<path>), poppler (pdfinfo, pdftotext).
No network: the "site" is tests/fixtures/site/, opened from disk. Output goes to tests/out/ (gitignored).
Exit code 0 only when every check passes.
"""
import json, os, re, shutil, subprocess, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "src/objective-brand-audit"
KIT = SKILL / "kit"
FIX = ROOT / "tests/fixtures"
OUT = ROOT / "tests/out"
AUDIT = OUT / "sample-audit"
sys.path.insert(0, str(ROOT / "tests"))
import denylist  # noqa: E402

fails = []


def chrome(p):
    """$CHROME (a path) wins, as in render_pdf.sh; else the installed Google Chrome."""
    if os.environ.get("CHROME"):
        return p.chromium.launch(executable_path=os.environ["CHROME"], headless=True)
    return p.chromium.launch(channel="chrome", headless=True)


def check(n, ok, label, detail=""):
    print(f"{'PASS' if ok else 'FAIL'} {n:2} {label}" + (f"\n        {detail}" if detail and not ok else ""))
    if not ok:
        fails.append(n)


def run(*cmd, env=None):
    return subprocess.run([str(c) for c in cmd], capture_output=True, text=True, env=env)


def kit(script, *args, env=None):
    return run(sys.executable, KIT / script, "--audit", AUDIT, *args, env=env)


def load(rel):
    return json.loads((AUDIT / rel).read_text(encoding="utf-8"))


def save(rel, data):
    (AUDIT / rel).write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")


shutil.rmtree(OUT, ignore_errors=True)
OUT.mkdir()
shutil.copytree(FIX / "sample-audit", AUDIT)
(AUDIT / "media/shots").mkdir(parents=True)
HTML = AUDIT / "outputs/harborpine-audit.html"
PDF = AUDIT / "outputs/harborpine-audit.pdf"

# 1. The skill file names itself and says when to use it.
text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
front = text.split("---")[1] if text.startswith("---") else ""
check(1, "name: objective-brand-audit" in front and "description: Use when" in front,
      "SKILL.md frontmatter has the name and a 'Use when' description")

# 2. Screenshots of the invented site, desktop and phone, as the audit phase saves them.
with sync_playwright() as p:
    browser = chrome(p)
    for kind, size in (("d", (1440, 900)), ("m", (375, 812))):
        page = browser.new_page(viewport={"width": size[0], "height": size[1]})
        for n, name in ((1, "home"), (2, "checkout")):
            page.goto((FIX / "site" / ("index.html" if name == "home" else "checkout.html")).as_uri())
            page.screenshot(path=AUDIT / f"media/shots/{kind}-{n:02d}-{name}.jpg", type="jpeg", quality=85)
            if kind == "d" and name == "home":  # the cover photo: the shop's first screen without the cookie bar
                (AUDIT / "media/brand").mkdir(exist_ok=True)
                page.screenshot(path=AUDIT / "media/brand/cover.jpg", type="jpeg", quality=85,
                                clip={"x": 0, "y": 0, "width": 1440, "height": 640})
        page.close()
    browser.close()
check(2, len(list((AUDIT / "media/shots").glob("*.jpg"))) == 4, "4 screenshots of the invented site")

# 3. Keyword data: P1 groups, Google check wins over the tool, own brand left out of strengths.
r = kit("build_keywords.py")
kw = load("data/keywords-report.json") if r.returncode == 0 else {}
green = next((x for x in kw.get("p1", {}).get("tea", []) if x["kw"] == "green tea online"), {})
check(3, r.returncode == 0 and kw["counts"] == {"p1": 4, "appendix": 5, "strengths": 5, "all_keywords": 10}
      and green.get("pos_src") == "google" and green.get("pos") is None
      and all(s["kw"] != "harbor and pine" for s in kw["strengths"]),
      "build_keywords.py: counts, Google override, brand search excluded", r.stderr or r.stdout)

# 4. A keyword file with a missing column stops with its name.
research = AUDIT / "data/keywords/harborpine-keyword-research.csv"
good = research.read_text()
research.write_text(good.replace(",kd,", ",difficulty,", 1))
r = kit("build_keywords.py")
research.write_text(good)
check(4, r.returncode != 0 and "kd" in (r.stderr + r.stdout), "a missing CSV column stops build_keywords.py by name",
      r.stderr + r.stdout)

# 5. The fact check finds no number that is not in the sources.
r = kit("factcheck.py")
check(5, r.returncode == 0 and r.stdout.strip().endswith("0 field(s) with numbers not found in the sources"),
      "factcheck.py: every number in the sample copy is in the sources", r.stdout[-600:])

# 6. The fact check flags an invented number (English formats: 3,200 and 7.95).
copy = load("copy/report-copy.json")
saved = json.dumps(copy)
copy["overview"]["lead"] += " Sales could grow by 3,217 orders and 7.93 € each, and the fee is -3.00 €."
save("copy/report-copy.json", copy)
r = kit("factcheck.py")
save("copy/report-copy.json", json.loads(saved))
check(6, "3217" in r.stdout and "7.93" in r.stdout and "-3" in r.stdout and "1 field(s)" in r.stdout,
      "factcheck.py flags invented numbers", r.stdout[-600:])

# 7. Merging a writer's answer: fenced JSON, glossary terms added once.
answer = AUDIT / "copy/answer.raw.txt"
term = json.loads(saved)["glossary"][0]["term"]
answer.write_text('```json\n{"glossary_add": [{"term": "%s", "def": "dup"}, {"term": "Test term", "def": "x"}, '
                  '{"term": "Test term", "def": "again"}]}\n```' % term)
r = kit("merge_copy.py", "copy/answer.raw.txt")
merged = load("copy/report-copy.json")
terms = [g["term"] for g in merged["glossary"]]
save("copy/report-copy.json", json.loads(saved))
answer.unlink()
check(7, r.returncode == 0 and terms.count(term) == 1 and terms.count("Test term") == 1
      and (AUDIT / "copy/report-copy.prev.json").exists(),
      "merge_copy.py strips the fence, adds new glossary terms once, keeps a .prev copy", r.stderr)
(AUDIT / "copy/report-copy.prev.json").unlink(missing_ok=True)

# 8. The report builds, in English, with every finding of the copy.
r = kit("build_report.py")
html = HTML.read_text(encoding="utf-8") if HTML.exists() else ""
ids = [f["id"] for s in json.loads(saved)["sections"] for f in s["findings"]]
check(8, r.returncode == 0 and '<html lang="en">' in html and all(f'id="f-{i.lower()}"' in html for i in ids),
      f"build_report.py: lang=en and all {len(ids)} findings in the HTML", r.stderr)

# 9. No Finnish left from the kit's past, and every anchor the menu links to exists.
finnish = re.findall(r"Huono|Korjattavaa|Oivallinen|tammi|helmi|kuu \d|\bMt\b|yleiskuva|korjauslista|liite\b", html)
anchors = set(re.findall(r'id="([^"]+)"', html))
links = set(re.findall(r'href="#([^"]+)"', html))
check(9, not finnish and links <= anchors and {"cover", "overview", "fix-first", "fix-list", "method"} <= anchors,
      "no Finnish kit labels; every menu link has its target", f"finnish={finnish} missing={links - anchors}")

# 10. Speed numbers in English format, unit kept with the number.
check(10, "4.4–5.1 s" in html and "1.8 MB" in html, "speed stats read 4.4–5.1 s and 1.8 MB, unbreakable")

# 11. Keyword part and seasonality charts are in, with English month names.
check(11, 'id="appendix"' in html and html.count('class="sm"') == 2 and "Nov ’25" in html,
      "keyword appendix and 2 seasonality charts with English months")

# 12. The phone layout has no sideways scroll, and every screenshot loaded.
with sync_playwright() as p:
    browser = chrome(p)
    res = {}
    for w in (375, 1440):
        page = browser.new_page(viewport={"width": w, "height": 900})
        page.goto(HTML.as_uri(), wait_until="load")
        res[w] = page.evaluate("""async () => {
            const imgs = [...document.images];
            imgs.forEach(i => { i.loading = 'eager'; });
            await Promise.all(imgs.map(i => i.decode().catch(() => null)));
            return {over: document.documentElement.scrollWidth - innerWidth,
                    broken: imgs.filter(i => !i.complete || !i.naturalWidth).length};
        }""")
        page.close()
    browser.close()
check(12, all(v["over"] <= 0 and v["broken"] == 0 for v in res.values()),
      "no sideways scroll at 375 px and 1440 px, no broken images", str(res))

# 13. The A4 PDF prints, and page 1 is the cover.
r = run("bash", KIT / "render_pdf.sh", AUDIT)
pages = int(re.search(r"Pages:\s+(\d+)", run("pdfinfo", PDF).stdout).group(1)) if PDF.exists() else 0
first = run("pdftotext", "-f", "1", "-l", "1", PDF, "-").stdout if PDF.exists() else ""
size = re.search(r"Page size:\s+([\d.]+) x ([\d.]+)", run("pdfinfo", PDF).stdout) if PDF.exists() else None
title = json.loads(saved)["cover"]["title"]
flat = lambda t: " ".join(re.findall(r"[a-z0-9]+", t.lower()))
a4 = size and abs(float(size.group(1)) - 595) < 3 and abs(float(size.group(2)) - 842) < 3
check(13, r.returncode == 0 and pages >= 6 and a4 and flat(title) in flat(first),
      f"render_pdf.sh: A4 PDF with {pages} pages, cover on page 1", r.stdout + r.stderr)

# 14. The closing offer appears only in a client report.
cfg = load("audit.json")
cfg["include_closing_cta"] = False
save("audit.json", cfg)
r = kit("build_report.py")
friend = HTML.read_text(encoding="utf-8")
cfg["include_closing_cta"] = True
save("audit.json", cfg)
kit("build_report.py")
check(14, 'class="end"' in html and 'class="end"' not in friend, "closing block only when include_closing_cta is true")

# 15. Without an OpenAI key the API route stops at once with the next step, and sends nothing.
env = {k: v for k, v in os.environ.items() if k != "OPENAI_API_KEY"}
r = kit("gpt_api.py", "--out", "copy/x.txt", "copy/brief.md", "data/findings.md", env=env)
check(15, r.returncode != 0 and "next copy route" in r.stderr and not (AUDIT / "copy/x.txt").exists(),
      "gpt_api.py without OPENAI_API_KEY stops and points to the next route", r.stderr)

# 16. The templates parse, and the audit.json template has every field the sample uses.
tpl = json.loads((SKILL / "templates/audit.json").read_text())
check(16, set(load("audit.json")) <= set(tpl) | {"shots_dir"} and tpl["lang"] == "en",
      "templates/audit.json parses and covers the sample's fields", str(set(load("audit.json")) - set(tpl)))

# 17. Keyword edge cases: an empty cell is no data (a dash, never 0), and a group left out of the order stops.
rank = AUDIT / "data/keywords/harborpine-current-rankings.csv"
good_rank = rank.read_text()
research.write_text(good.replace("green tea online,1300,", "green tea online,,"))
rank.write_text(good_rank.replace("organic black tea,720,18,", "organic black tea,720,,"))
r1 = kit("build_keywords.py")
kw1 = load("data/keywords-report.json") if r1.returncode == 0 else {}
green = next((x for x in kw1.get("p1", {}).get("tea", []) if x["kw"] == "green tea online"), {})
r2 = kit("build_report.py")
cell = re.search(r'green tea online</th><td class="vol"[^>]*>.*?</td>', HTML.read_text(encoding="utf-8"), re.S)
cfg = load("audit.json")
cfg["keywords"]["p1_order"] = ["chai", "gifts"]
save("audit.json", cfg)
r3 = kit("build_keywords.py")
cfg["keywords"]["p1_order"] = ["tea", "chai", "gifts"]
save("audit.json", cfg)
research.write_text(good)
rank.write_text(good_rank)
kit("build_keywords.py")
kit("build_report.py")
check(17, r1.returncode == 0 and green.get("vol") is None and r2.returncode == 0 and cell and 'class="dim">-' in cell.group(0)
      and r3.returncode != 0 and "tea" in r3.stderr + r3.stdout,
      "empty keyword cells stay 'no data'; a group missing from p1_order stops build_keywords.py",
      (r1.stderr + r2.stderr + r3.stdout)[-400:])

# 18. A brand token that is not a colour or a plain font stack stops the build (it would land in <style>).
cfg = load("audit.json")
cfg["tokens"]["--font"] = "'</style><script>alert(1)</script>', serif"
save("audit.json", cfg)
r = kit("build_report.py")
cfg["tokens"]["--font"] = json.loads((FIX / "sample-audit/audit.json").read_text())["tokens"]["--font"]
save("audit.json", cfg)
check(18, r.returncode != 0 and "--font" in r.stderr, "a token with markup stops build_report.py", r.stderr)

# 19. Nothing in the repository names a denylisted person, client or site, and no e-mail address.
hashes = denylist.load()
listed = run("git", "-C", ROOT, "ls-files", "--cached", "--others", "--exclude-standard").stdout.split("\n")
hits = []
for rel in filter(None, listed):
    p = ROOT / rel
    if not p.is_file() or p.suffix in (".jpg", ".png", ".pdf", ".woff2"):
        continue
    body = p.read_text(encoding="utf-8", errors="replace")
    hits += [f"{rel}: {t}" for t in sorted(denylist.hits(rel + " " + body, hashes))]
    hits += [f"{rel}: {m}" for m in re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", body)
             if not m.endswith((".example", "users.noreply.github.com")) and m.lstrip("+") != "claudebot@anthropic.com"]
check(19, hashes and not hits, f"no denylisted name ({len(hashes)} terms) and no e-mail address in the repository",
      "\n        ".join(hits[:20]))

print(f"\n{'ALL PASS' if not fails else 'FAILED: ' + ', '.join(map(str, fails))}")
sys.exit(1 if fails else 0)
