"""Build a branded website-audit report (one self-contained HTML file) for one audit folder.

Usage:  python3 build_report.py --audit <audit-dir> [--only overview,sales,quickfix,fixlist,appendix,closing]
Reads:  <audit>/audit.json            brand, tokens, fonts, logo, images, screenshots, section roles, speed numbers
        <audit>/copy/report-copy.json the report copy (English)
        <audit>/copy/ui-labels.json   the short labels
        <audit>/data/keywords-report.json  optional, from build_keywords.py (search tables + appendix)
        icons from this kit (assets/icons), report.css from this kit
Writes: <audit>/outputs/<output_name>.html
"""
import argparse, base64, html, io, json, math, re, sys
from pathlib import Path
from PIL import Image

KIT = Path(__file__).resolve().parent
ap = argparse.ArgumentParser()
ap.add_argument("--audit", required=True, help="audit folder that holds audit.json")
ap.add_argument("--only", help="comma-separated part ids to build (cover and nav are always built)")
ARGS = ap.parse_args()
ROOT = Path(ARGS.audit).expanduser().resolve()
ONLY = set(ARGS.only.split(",")) if ARGS.only else None


def die(msg):
    sys.exit(f"build_report: {msg}")


def load_json(rel):
    p = ROOT / rel
    if not p.exists():
        die(f"missing {p}")
    return json.loads(p.read_text(encoding="utf-8"))


CFG = load_json("audit.json")
COPY = load_json("copy/report-copy.json")
UI = load_json("copy/ui-labels.json")
KW = load_json("data/keywords-report.json") if (ROOT / "data/keywords-report.json").exists() else None

REQUIRED_TOKENS = ["--accent", "--ink", "--ink-2", "--muted", "--line", "--line-2", "--panel", "--paper",
                   "--axis", "--on-dark", "--font", "--cond", "--display"]
missing = [t for t in REQUIRED_TOKENS if t not in CFG.get("tokens", {})]
if missing:
    die(f"audit.json tokens missing: {', '.join(missing)}")
# Token values go into a <style> block: colours must be hex, fonts plain font stacks (no markup can get in).
for name, value in CFG["tokens"].items():
    if not re.fullmatch(r"--[a-z0-9-]+", name):
        die(f"audit.json token name {name!r} must look like --accent")
    font = name in ("--font", "--cond", "--display")
    if not re.fullmatch(r"[\w\s,'\"().-]+" if font else r"#[0-9A-Fa-f]{6}", str(value)):
        die(f"audit.json token {name} must be {'a plain font stack' if font else 'a 6-digit hex colour'}: {value!r}")
for key in ("output_name", "brand", "fonts"):
    if key not in CFG:
        die(f"audit.json has no '{key}'")

ROLES = CFG.get("sections", {})
GRADE_ORDER = ROLES.get("grade_order", [])


def e(text):
    """Escape for HTML and keep a number and its unit ('8.5 s', '30 €', '2 MB') from breaking across lines."""
    t = html.escape(str(text))
    t = re.sub(r"(\d) (€|%|s\b|h\b|min\b|KB\b|MB\b|px\b|ms\b)", "\\1\u00a0\\2", t)
    return t


# ---------- assets ----------
def img_data(path, max_w, quality=80):
    if not path.exists():
        die(f"missing image {path}")
    im = Image.open(path).convert("RGB")
    if im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=quality, optimize=True, progressive=True)
    return f"data:image/jpeg;base64,{base64.b64encode(buf.getvalue()).decode()}", im.width, im.height


def logo_data(path):
    """SVG and PNG logos are embedded as they are (keeps transparency); other formats become JPEG."""
    if not path.exists():
        die(f"missing logo {path}")
    mime = {".svg": "image/svg+xml", ".png": "image/png"}.get(path.suffix.lower())
    if mime:
        return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()
    return img_data(path, 600, 90)[0]


def icon(name, cls="ico"):
    svg = (KIT / f"assets/icons/{name}.svg").read_text()
    return svg.replace("<svg ", f'<svg class="{cls}" aria-hidden="true" ', 1)


def font_faces():
    f = CFG["fonts"]
    fdir = ROOT / f.get("dir", "media/assets/fonts")
    want = {(fam, str(w)) for fam, w in f["include"]}
    subsets = set(f.get("subsets", ["latin"]))
    out, found = [], set()
    for line in (fdir / f.get("manifest", "manifest.txt")).read_text().splitlines():
        fam, w, subset, fn, ur = line.split("|")
        if subset not in subsets or (fam, w) not in want:
            continue
        found.add((fam, w))
        b64 = base64.b64encode((fdir / fn).read_bytes()).decode()
        out.append(f"@font-face{{font-family:'{fam}';font-style:normal;font-weight:{w};font-display:swap;"
                   f"src:url(data:font/woff2;base64,{b64}) format('woff2');unicode-range:{ur};}}")
    if want - found:
        die(f"fonts not in manifest: {sorted(want - found)}")
    return "\n".join(out)


def brand_image(key):
    spec = CFG["brand"].get(key)
    if not spec:
        return None
    return img_data(ROOT / spec["path"], spec.get("max_w", 1600), spec.get("quality", 80))[0]


BRAND = CFG["brand"]["name"]
LOGO = logo_data(ROOT / CFG["brand"]["logo"])
COVER_IMG = brand_image("cover_image")
BAR_IMG = brand_image("bar_image")
BAR_STYLE = f" style=\"background-image:url('{BAR_IMG}')\"" if BAR_IMG else ""

# finding id -> [[file, "d"|"m"], ...]; d = desktop browser frame, m = phone frame
SHOTS = CFG.get("shots", {})
SHOTS_DIR = ROOT / CFG.get("shots_dir", "media/shots")
_shot_cache = {}


def shot(fn, kind):
    if fn not in _shot_cache:
        _shot_cache[fn] = img_data(SHOTS_DIR / fn, 800 if kind == "d" else 560, 78)
    return _shot_cache[fn]


# ---------- small helpers ----------
# Worst to best; the two worst are drawn as bad.
GRADES = ["Poor", "Needs work", "Good", "Excellent"]
BAD_GRADES = GRADES[:2]


def grade_meter(grade):
    i = GRADES.index(grade) if grade in GRADES else -1
    cells = "".join(f'<span class="gm-cell{" on" if k == i else ""}{" bad" if k == i and k < 2 else ""}"></span>'
                    for k in range(4))
    return f'<span class="gm" role="img" aria-label="{e(UI["grade_aria"])}: {e(grade)}">{cells}</span>'


def owner_chip(owner):
    return f'<span class="meta-chip">{icon("storefront")}{e(owner)}</span>' if owner else ""


def effort_chip(effort):
    return f'<span class="meta-chip">{icon("clock")}{e(effort)}</span>' if effort else ""


def fmt_int(n):
    return f"{n:,}"


def num1(x):
    return f"{x:.1f}"


def num_range(lo, hi, unit):
    return f"{num1(lo)}\u00a0{unit}" if lo == hi else f"{num1(lo)}–{num1(hi)}\u00a0{unit}"


# ---------- sections ----------
def cover():
    c = COPY["cover"]
    meta = "".join(f"<li>{e(m)}</li>" for m in c["meta"])
    photo = f'\n    <div class="cover-photo"><img src="{COVER_IMG}" alt=""></div>' if COVER_IMG else ""
    return f"""
<header class="cover" id="cover">
  <div class="cover-bar"{BAR_STYLE}>
    <img class="cover-logo" src="{LOGO}" alt="{e(BRAND)}">
    <span class="cover-kicker">{e(c['kicker'])}</span>
  </div>
  <div class="cover-main">{photo}
    <div class="cover-body">
      <h1 class="cover-title">{e(c['title'])}</h1>
      <p class="cover-sub">{e(c['subtitle'])}</p>
      <ul class="cover-meta">{meta}</ul>
    </div>
  </div>
</header>"""


def nav():
    links = ([("overview", UI["nav_overview"])] + [(s["id"], s["nav"]) for s in COPY["sections"]]
             + [("fix-first", COPY["quickfix"]["nav"]), ("fix-list", UI["nav_fixlist"])])
    items = "".join(f'<a href="#{i}">{e(t)}</a>' for i, t in links)
    return f'<nav class="topnav" aria-label="{e(UI["nav_aria"])}"><img src="{LOGO}" alt="" class="nav-logo"><div class="nav-links">{items}</div></nav>'


def top5_html(items):
    return "".join(f"""
      <li class="top-item">
        <span class="top-num" aria-hidden="true">{n}</span>
        <div class="top-text">
          <h3>{e(t['title'])}</h3>
          <p>{e(t['body'])}</p>
          <div class="meta-row">{effort_chip(t.get('effort'))}{owner_chip(t.get('owner'))}</div>
        </div>
      </li>""" for n, t in enumerate(items, 1))


def works_html(title, items):
    if not items:
        return ""
    lis = "".join(f"<li>{icon('check-circle', 'ico ok')}<div><h4>{e(w['title'])}</h4><p>{e(w['body'])}</p></div></li>"
                  for w in items)
    return f'<div class="works"><h3 class="block-title">{e(title)}</h3><ul class="works-list">{lis}</ul></div>'


def overview():
    o = COPY["overview"]
    grades = "".join(f"""
      <li class="grade-row">
        <span class="grade-area">{e(g['area'])}</span>
        {grade_meter(g['grade'])}
        <span class="grade-word{' bad' if g['grade'] in BAD_GRADES else ''}">{e(g['grade'])}</span>
        <span class="grade-reason">{e(g['reason'])}</span>
      </li>""" for g in o["grades"])
    return f"""
<section class="page overview" id="overview">
  <h2 class="sec-title">{e(o['title'])}</h2>
  <p class="lead">{e(o['lead'])}</p>
  <div class="grades">
    <h3 class="block-title">{e(o['grades_title'])}</h3>
    <ul class="grade-list">{grades}</ul>
    <p class="note">{e(o['grades_note'])}</p>
  </div>
  <p class="structure">{icon('list-checks')}{e(o['structure_note'])}</p>
</section>"""


def quickfix():
    q = COPY["quickfix"]
    quick = "".join(f"<li>{icon('timer')}<span>{e(x)}</span></li>" for x in q["quick"])
    return f"""
<section class="page quickfix" id="fix-first">
  <h2 class="sec-title">{e(q['title'])}</h2>
  <p class="lead">{e(q['lead'])}</p>
  <div class="top5">
    <h3 class="block-title big">{e(q['top5_title'])}</h3>
    <ol class="top-list">{top5_html(q['top5'])}</ol>
  </div>
  <div class="quick">
    <h3 class="block-title">{e(q['quick_title'])}</h3>
    <ul class="quick-list">{quick}</ul>
  </div>
</section>"""


def figure(fid, caption):
    items = SHOTS.get(fid, [])
    if not items:
        return ""
    figs = []
    for fn, kind in items:
        src, w, h = shot(fn, kind)
        cls = "phone" if kind == "m" else "browser"
        figs.append(f'<div class="frame {cls}"><img src="{src}" width="{w}" height="{h}" alt="{e(caption)}" loading="lazy"></div>')
    cap = f"<figcaption>{e(caption)}</figcaption>" if caption else ""
    kinds = "".join(k for _, k in items)
    return f'<figure class="shots shots-{kinds}">{"".join(figs)}{cap}</figure>'


def finding(f):
    fig = figure(f["id"], f.get("shot_caption", ""))
    kinds = {k for _, k in SHOTS.get(f["id"], [])}
    has = (" has-fig" if fig else "") + (" mixed" if kinds == {"d", "m"} else "")
    return f"""
  <article class="finding{has}" id="f-{e(f['id'].lower())}">
    <div class="f-text">
      <span class="f-id">{e(f['id'])}</span>
      <h3>{e(f['title'])}</h3>
      <dl>
        <dt>{e(UI["seen"])}</dt><dd>{e(f['seen'])}</dd>
        <dt>{e(UI["why"])}</dt><dd>{e(f['why'])}</dd>
        <dt>{e(UI["fix"])}</dt><dd>{e(f['fix'])}</dd>
      </dl>
      <div class="meta-row">{effort_chip(f.get('effort'))}{owner_chip(f.get('owner'))}</div>
    </div>
    {fig}
  </article>"""


def grade_for(sec_id):
    g = COPY["overview"]["grades"]
    i = GRADE_ORDER.index(sec_id) if sec_id in GRADE_ORDER else None
    return g[i]["grade"] if i is not None and i < len(g) else None


def section(s):
    gr = grade_for(s["id"])
    badge = f'<div class="sec-grade">{grade_meter(gr)}<span class="grade-word{" bad" if gr in BAD_GRADES else ""}">{e(gr)}</span></div>' if gr else ""
    extra = ""
    if s["id"] == ROLES.get("search") and KW:
        extra = search_extra()
    if s["id"] == ROLES.get("speed"):
        extra = speed_extra()
    if s["id"] == ROLES.get("legal"):
        extra = f'<p class="disclaimer">{icon("gavel")}{e(COPY["legal_extra"]["disclaimer"])}</p>'
    findings = "".join(finding(f) for f in s["findings"])
    pos = "before" if s["id"] in (ROLES.get("search"), ROLES.get("speed")) else "after"
    return f"""
<section class="page section sec-{e(s['id'])}" id="{e(s['id'])}">
  <div class="sec-head">
    <h2 class="sec-title">{e(s['title'])}</h2>
    {badge}
  </div>
  <p class="lead">{e(s['lead'])}</p>
  {extra if pos == 'before' else ''}
  <div class="findings">{findings}</div>
  {extra if pos == 'after' else ''}
  {works_html(s.get('works_title', ''), s.get('works', []))}
</section>"""


# ---------- search: tables + small multiples ----------
def pos_cell(r):
    se = COPY["search_extra"]
    if r["pos"] is not None:
        return f'<span class="pos good">{r["pos"]}.</span>'
    if r["pos_src"] == "google":
        return f'<span class="pos miss">{icon("warning-circle")}{e(se["not_top10_label"])}</span>'
    return f'<span class="pos nodata">{e(se["no_data_label"])}</span>'


def comp_cell(r):
    if not r.get("competitor"):
        return '<span class="dim">-</span>'
    if r.get("competitor_pos") is None:
        return f'<span>{e(r["competitor"])}</span>'
    return f'<span>{e(r["competitor"])} <span class="cpos">{r["competitor_pos"]}.</span></span>'


def vol_cell(v, vmax, label=""):
    """A bar and the number; None (no data) shows a dash, never 0."""
    w = 0 if not v else max(2, round(100 * v / vmax))
    num = '<span class="dim">-</span>' if v is None else fmt_int(v)
    return f'<td class="vol" data-label="{e(label)}"><span class="bar" style="width:{w}%"></span><span class="num">{num}</span></td>'


def vol_max(rows):
    return max((r["vol"] or 0) for r in rows) or 1


def p1_tables():
    se = COPY["search_extra"]
    lab = se["col_labels"]
    tl = se["target_labels"]
    out = []
    for g in KW["p1_order"]:
        rows = KW["p1"].get(g, [])
        if not rows:
            continue
        vmax = vol_max(rows)
        single = len({r["target"] for r in rows}) == 1
        if single:
            body = "".join(f"""<tr>
          <th scope="row">{e(r['kw'])}</th>{vol_cell(r['vol'], vmax, lab['vol'])}
          <td class="kd" data-label="{e(lab['kd'])}">{r['kd'] if r['kd'] is not None else '<span class="dim">-</span>'}</td>
          <td class="pos-cell" data-label="{e(lab['pos'])}">{pos_cell(r)}</td>
          <td class="comp" data-label="{e(lab['comp'])}">{comp_cell(r)}</td></tr>""" for r in rows)
            out.append(f"""
  <div class="kw-group">
    <h4>{e(se['p1_group_titles'][g])} <span class="count">{len(rows)}</span></h4>
    <p class="group-target"><span>{e(lab['target'])}:</span> {e(tl[rows[0]['target']])}</p>
    <table class="kw kw-p1 one-target">
      <thead><tr><th scope="col">{e(lab['kw'])}</th><th scope="col">{e(lab['vol'])}</th><th scope="col">{e(lab['kd'])}</th><th scope="col">{e(lab['pos'])}</th><th scope="col">{e(lab['comp'])}</th></tr></thead>
      <tbody>{body}</tbody>
    </table>
  </div>""")
            continue
        body = "".join(f"""<tr>
          <th scope="row">{e(r['kw'])}</th>{vol_cell(r['vol'], vmax, lab['vol'])}
          <td class="kd" data-label="{e(lab['kd'])}">{r['kd'] if r['kd'] is not None else '<span class="dim">-</span>'}</td>
          <td class="pos-cell" data-label="{e(lab['pos'])}">{pos_cell(r)}</td>
          <td class="comp" data-label="{e(lab['comp'])}">{comp_cell(r)}</td>
          <td class="target" data-label="{e(lab['target'])}">{e(tl[r['target']])}</td></tr>""" for r in rows)
        out.append(f"""
  <div class="kw-group">
    <h4>{e(se['p1_group_titles'][g])} <span class="count">{len(rows)}</span></h4>
    <table class="kw kw-p1">
      <thead><tr><th scope="col">{e(lab['kw'])}</th><th scope="col">{e(lab['vol'])}</th><th scope="col">{e(lab['kd'])}</th><th scope="col">{e(lab['pos'])}</th><th scope="col">{e(lab['comp'])}</th><th scope="col">{e(lab['target'])}</th></tr></thead>
      <tbody>{body}</tbody>
    </table>
  </div>""")
    return "".join(out)


def short_path(path):
    """'/shop/x/p/6420616880430/' -> '/shop/x/' (drop product/category id segments)."""
    return re.sub(r"/[pc]/[^/]+/?$", "/", path)


def strengths_table():
    se = COPY["search_extra"]
    lab = se["strengths_cols"]
    rows = KW["strengths"]
    if not rows:
        return ""
    vmax = vol_max(rows)
    body = "".join(f"""<tr>
      <th scope="row">{e(r['kw'])}</th>{vol_cell(r['vol'], vmax, lab['vol'])}
      <td class="pos-cell" data-label="{e(lab['pos'])}"><span class="pos good">{r['pos']}.</span></td>
      <td class="path" data-label="{e(lab['page'])}">{e(short_path(r['path']))}</td>
      <td class="traffic" data-label="{e(lab['traffic'])}">{'<span class="dim">-</span>' if r['traffic'] is None else fmt_int(round(r['traffic']))}</td></tr>""" for r in rows)
    return f"""
  <div class="strengths">
    <h3 class="block-title">{e(se['strengths_title'])}</h3>
    <p>{e(se['strengths_lead'])}</p>
    <table class="kw kw-str">
      <thead><tr><th scope="col">{e(lab['kw'])}</th><th scope="col">{e(lab['vol'])}</th><th scope="col">{e(lab['pos'])}</th><th scope="col">{e(lab['page'])}</th><th scope="col">{e(lab['traffic'])}</th></tr></thead>
      <tbody>{body}</tbody>
    </table>
    <p class="note">{e(se['strengths_note'])}</p>
  </div>"""


def appendix():
    se = COPY["search_extra"]
    lab = se["col_labels"]
    groups = []
    for g in KW["appendix_order"]:
        rows = KW["appendix"].get(g, [])
        if not rows:
            continue
        vmax = vol_max(rows)
        body = "".join(f"""<tr>
          <th scope="row">{e(r['kw'])}</th>{vol_cell(r['vol'], vmax, lab['vol'])}
          <td class="kd" data-label="{e(lab['kd'])}">{r['kd'] if r['kd'] is not None else '<span class="dim">-</span>'}</td>
          <td class="prio" data-label="{e(se['prio_label'])}">{e(r['prio'])}</td>
          <td class="pos-cell" data-label="{e(lab['pos'])}">{pos_cell(r)}</td>
          <td class="comp" data-label="{e(lab['comp'])}">{comp_cell(r)}</td></tr>""" for r in rows)
        groups.append(f"""
  <div class="kw-group">
    <h4>{e(se['appendix_group_titles'][g])} <span class="count">{len(rows)}</span></h4>
    <table class="kw kw-app">
      <thead><tr><th scope="col">{e(lab['kw'])}</th><th scope="col">{e(lab['vol'])}</th><th scope="col">{e(lab['kd'])}</th><th scope="col">{e(se['prio_label'])}</th><th scope="col">{e(lab['pos'])}</th><th scope="col">{e(lab['comp'])}</th></tr></thead>
      <tbody>{body}</tbody>
    </table>
  </div>""")
    return f"""
<section class="page appendix" id="appendix">
  <h2 class="sec-title">{e(se['appendix_title'])}</h2>
  <p class="lead">{e(se['appendix_lead'])}</p>
  <div class="kw-grid">{''.join(groups)}</div>
  <p class="note">{e(se['table_note'])}</p>
</section>"""


MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def nice_axis(peak, steps=3):
    """Shared y-axis for the small multiples: 0 plus `steps` round gridlines that cover the peak."""
    peak = max(peak, steps)
    mag = 10 ** math.floor(math.log10(peak / steps))
    step = next(m * mag for m in (1, 2, 2.5, 5, 10) if m * mag * steps >= peak)
    step = int(step) if float(step).is_integer() else step
    return step * steps, [step * i for i in range(steps + 1)]


def small_multiple(name, series, ymax, yticks):
    W, H, L, R, T, B = 300, 150, 34, 10, 14, 26
    pw, ph = W - L - R, H - T - B
    n = len(series)
    # x by calendar month, so a month with no data leaves a gap instead of squeezing the axis
    mi = [int(ym[:4]) * 12 + int(ym[5:7]) for ym, _ in series]
    span = mi[-1] - mi[0]
    xs = [L + pw * (m - mi[0]) / span for m in mi] if span else [L + pw / 2]
    ys = [T + ph * (1 - v / ymax) for _, v in series]
    line = " ".join(f"{'M' if i == 0 else 'L'}{x:.1f},{y:.1f}" for i, (x, y) in enumerate(zip(xs, ys)))
    area = line + f" L{xs[-1]:.1f},{T + ph:.1f} L{xs[0]:.1f},{T + ph:.1f} Z"
    grid = ""
    for v in yticks:
        y = T + ph * (1 - v / ymax)
        grid += f'<line x1="{L}" x2="{W - R}" y1="{y:.1f}" y2="{y:.1f}" class="{"axis" if v == 0 else "grid"}"/>'
        grid += f'<text x="{L - 6}" y="{y + 3.5:.1f}" class="tick" text-anchor="end">{fmt_int(v) if v else 0}</text>'
    ticks = ""
    for i, (ym, v) in enumerate(series):
        m = int(ym[5:7])
        if i % 3 == 0:
            ticks += f'<text x="{xs[i]:.1f}" y="{H - 8}" class="tick" text-anchor="middle">{MONTHS[m - 1]} ’{ym[2:4]}</text>'
    pts = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" class="hit"><title>{MONTHS[int(ym[5:7]) - 1]} {ym[:4]}: {fmt_int(v)} {e(UI["searches_unit"])}</title></circle>'
                  for x, y, (ym, v) in zip(xs, ys, series))
    pk = max(range(n), key=lambda i: series[i][1])
    peak = (f'<circle cx="{xs[pk]:.1f}" cy="{ys[pk]:.1f}" r="4" class="peak"/>'
            f'<text x="{xs[pk] + 7:.1f}" y="{ys[pk] + 4:.1f}" class="lbl">{fmt_int(series[pk][1])}</text>')
    return f"""<figure class="sm"><figcaption>{e(name)}</figcaption>
      <svg viewBox="0 0 {W} {H}" role="img" aria-label="{e(name)}: {e(UI["season_aria"])} {fmt_int(series[pk][1])}">
        {grid}<path d="{area}" class="area"/><path d="{line}" class="line"/>{peak}{pts}{ticks}
      </svg></figure>"""


def round_visits(n):
    """An estimate shown as ~N: hundreds from 1,000 up, tens from 100 up, else as it is (49 stays 49, never ~0)."""
    return round(n, -2) if n >= 1000 else round(n, -1) if n >= 100 else round(n)


def search_extra():
    if "search_extra" not in COPY:
        die("copy/report-copy.json has no search_extra: send the round-2 keyword brief to GPT first")
    se = COPY["search_extra"]
    t = KW["totals"]
    stats = f"""
  <div class="stats">
    <div class="stat"><span class="stat-num">{t['organic_keywords']}</span><span class="stat-lbl">{e(UI["stat_keywords"])}</span></div>
    <div class="stat"><span class="stat-num">{t['top3']}</span><span class="stat-lbl">{e(UI["stat_top3"])}</span></div>
    <div class="stat"><span class="stat-num">~{fmt_int(round_visits(t['traffic_est']))}</span><span class="stat-lbl">{e(UI["stat_traffic"])}</span></div>
  </div>
  <p class="note">{e(se['totals_caption'])}</p>"""
    order = [k for k in CFG.get("season_keywords", []) if k in KW["season"]]
    season = ""
    if order:
        ymax, yticks = nice_axis(max(v for k in order for _, v in KW["season"][k]))
        sms = "".join(small_multiple(k, KW["season"][k], ymax, yticks) for k in order)
        season = f"""
  <div class="season">
    <h3 class="block-title">{e(se['season_title'])}</h3>
    <div class="sm-grid">{sms}</div>
    <p class="note">{e(se['season_caption'])}</p>
  </div>"""
    demand = f"""
  <div class="demand">
    <h3 class="block-title">{e(se['p1_title'])}</h3>
    <p>{e(se['p1_lead'])}</p>
    <p class="note">{e(se['kd_note'])}</p>
    <div class="kw-grid">{p1_tables()}</div>
    <p class="note">{e(se['table_note'])}</p>
  </div>"""
    steps = "".join(f"<li>{e(x)}</li>" for x in se["order"])
    order_html = f'<div class="order"><h3 class="block-title">{e(se["order_title"])}</h3><ol class="steps">{steps}</ol></div>'
    return stats + strengths_table() + season + demand + order_html


def speed_extra():
    """Lab-test timeline: Google's LCP bands (good < 2.5 s, poor > 4 s) with the measured FCP and LCP ranges."""
    if "speed" not in CFG:
        die("audit.json has no 'speed' block (fcp_s, lcp_s, js_mb) for the speed section")
    sp, m = COPY["speed_extra"], CFG["speed"]
    (f_lo, f_hi), (l_lo, l_hi) = m["fcp_s"], m["lcp_s"]
    axis = max(9, math.ceil(l_hi))
    W, H, L, R = 640, 120, 20, 20
    pw = W - L - R
    x = lambda s: L + pw * s / axis
    bands = (f'<rect x="{x(0):.1f}" y="40" width="{x(2.5) - x(0):.1f}" height="26" class="band-good"/>'
             f'<rect x="{x(2.5):.1f}" y="40" width="{x(4) - x(2.5):.1f}" height="26" class="band-mid"/>'
             f'<rect x="{x(4):.1f}" y="40" width="{x(axis) - x(4):.1f}" height="26" class="band-poor"/>'
             f'<text x="{x(1.25):.1f}" y="57" class="band-lbl" text-anchor="middle">{e(UI["band_good"])}</text>'
             f'<text x="{x(3.25):.1f}" y="57" class="band-lbl" text-anchor="middle">{e(UI["band_mid"])}</text>'
             f'<text x="{x((4 + axis) / 2):.1f}" y="57" class="band-lbl" text-anchor="middle">{e(UI["band_poor"])}</text>')
    ticks = "".join(f'<line x1="{x(s):.1f}" x2="{x(s):.1f}" y1="66" y2="72" class="axis"/><text x="{x(s):.1f}" y="86" class="tick" text-anchor="middle">{s} s</text>' for s in range(0, axis + 1))
    width = lambda lo, hi: max(x(hi) - x(lo), 4)
    marks = (f'<rect x="{x(f_lo):.1f}" y="30" width="{width(f_lo, f_hi):.1f}" height="46" class="meas"/>'
             f'<text x="{x((f_lo + f_hi) / 2):.1f}" y="22" class="lbl" text-anchor="middle">{e(UI["mark_fcp"])}</text>'
             f'<rect x="{x(l_lo):.1f}" y="30" width="{width(l_lo, l_hi):.1f}" height="46" class="meas"/>'
             f'<text x="{x((l_lo + l_hi) / 2):.1f}" y="104" class="lbl" text-anchor="middle">{e(UI["mark_lcp"])}</text>'
             f'<line x1="{x(2.5):.1f}" x2="{x(2.5):.1f}" y1="34" y2="72" class="target"/>'
             f'<text x="{x(2.5):.1f}" y="104" class="lbl" text-anchor="middle">{e(UI["mark_target"])}</text>')
    svg = f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{e(UI["speed_chart_aria"])}">{bands}{ticks}{marks}</svg>'
    lcp_cls = " red" if l_hi > 4 else ""
    return f"""
  <div class="speed">
    <div class="stats">
      <div class="stat"><span class="stat-num">{num_range(f_lo, f_hi, "s")}</span><span class="stat-lbl">{e(UI["stat_fcp"])}</span></div>
      <div class="stat"><span class="stat-num{lcp_cls}">{num_range(l_lo, l_hi, "s")}</span><span class="stat-lbl">{e(UI["stat_lcp"])}</span></div>
      <div class="stat"><span class="stat-num">{num1(m["js_mb"])}\u00a0MB</span><span class="stat-lbl">{e(UI["stat_js"])}</span></div>
    </div>
    <div class="timeline">{svg}</div>
    <p class="note">{e(sp['metrics_caption'])}</p>
    <p class="analogy">{icon('lightning')}{e(sp['analogy'])}</p>
  </div>"""


def fixlist():
    fl = COPY["fixlist"]
    groups = ""
    for g in fl["groups"]:
        rows = "".join(f"""<li class="fix">
            <span class="box" aria-hidden="true"></span>
            <span class="fix-id">{e(it['id'])}</span>
            <span class="fix-act">{e(it['action'])}</span>
            <span class="fix-meta">{effort_chip(it.get('effort'))}{owner_chip(it.get('owner'))}</span></li>""" for it in g["items"])
        groups += f'<div class="fix-group"><h3 class="block-title">{e(g["label"])}</h3><ul class="fix-list">{rows}</ul></div>'
    return f"""
<section class="page fixes" id="fix-list">
  <h2 class="sec-title">{e(fl['title'])}</h2>
  <p class="lead">{e(fl['lead'])}</p>
  {groups}
</section>"""


def closing_cta():
    """Sales/contact block at the very end; only for client reports (audit.json include_closing_cta)."""
    if not CFG.get("include_closing_cta"):
        return ""
    c = COPY["closing"]
    return f"""
  <div class="end"{BAR_STYLE}>
    <img class="end-logo" src="{LOGO}" alt="">
    <div>
      <h2>{e(c['title'])}</h2>
      <p>{e(c['body'])}</p>
      <p class="sign">{e(c['contact'])}</p>
    </div>
  </div>"""


def closing():
    m = COPY["method"]
    gl = "".join(f"<div><dt>{e(g['term'])}</dt><dd>{e(g['def'])}</dd></div>" for g in COPY["glossary"])
    return f"""
<section class="page closing" id="method">
  <div class="method">
    <h2 class="sec-title small">{e(m['title'])}</h2>
    <p>{e(m['body'])}</p>
  </div>
  <div class="glossary">
    <h2 class="sec-title small">{e(UI["glossary_title"])}</h2>
    <dl class="gl">{gl}</dl>
  </div>{closing_cta()}
</section>"""


CSS = (KIT / "report.css").read_text(encoding="utf-8")


def rgba(token, alpha):
    """See-through brand colour as plain rgba(): Chrome renders it exactly like a hand-written value."""
    h = CFG["tokens"][token].lstrip("#")
    if len(h) != 6:
        die(f"audit.json token {token} must be a 6-digit hex colour like #292424")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


DERIVED = {"--ink-35": rgba("--ink", ".35"), "--ink-45": rgba("--ink", ".45"),
           "--accent-18": rgba("--accent", ".18"), "--paper-96": rgba("--paper", ".96")}
TOKENS = ":root {\n" + "".join(f"  {k}: {v};\n" for k, v in {**CFG["tokens"], **DERIVED}.items()) + "}"


def build():
    if KW is None:
        print("build_report: no data/keywords-report.json, search tables and keyword appendix left out")
    parts = [cover(), nav()]
    want = lambda k: ONLY is None or k in ONLY
    if want("overview"):
        parts.append(overview())
    for s in COPY["sections"]:
        if want(s["id"]):
            parts.append(section(s))
    if want("quickfix"):
        parts.append(quickfix())
    if want("fixlist"):
        parts.append(fixlist())
    if want("appendix") and KW:
        parts.append(appendix())
    if want("closing"):
        parts.append(closing())
    doc = f"""<!doctype html>
<html lang="{CFG.get('lang', 'en')}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(UI["html_title"])}</title>
<style>{font_faces()}
{CSS}
{TOKENS}</style>
</head>
<body>
{''.join(parts)}
</body>
</html>"""
    out = ROOT / "outputs" / f"{CFG['output_name']}.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size // 1024} KB)")


build()
