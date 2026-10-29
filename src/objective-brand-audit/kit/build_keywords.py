"""Build <audit>/data/keywords-report.json from the keyword files + our Google checks.

Usage:  python3 build_keywords.py --audit <audit-dir>
Reads:  <audit>/audit.json "keywords" block (file prefix, clusters, target rules, orders, totals)
        <audit>/data/keywords/<prefix>-keyword-research.csv, -current-rankings.csv, -seasonality.csv
        (column formats: references/keyword-files.md)
        <audit>/data/google-checks.json (optional; Google positions override the keyword tool's)

p1:        all P1 keywords grouped by cluster, with KD, position, competitor and target page key
strengths: top current rankings by estimated traffic (excluded words from audit.json)
appendix:  all P2/P3 keywords grouped by cluster
season:    monthly searches per keyword
"""
import argparse, csv, json, sys
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--audit", required=True)
ROOT = Path(ap.parse_args().audit).expanduser().resolve()
CFG = json.loads((ROOT / "audit.json").read_text(encoding="utf-8"))
K = CFG.get("keywords") or sys.exit("build_keywords: audit.json has no 'keywords' block")
D = ROOT / "data"

COLUMNS = {
    "keyword-research": ["keyword", "volume", "kd", "priority", "cluster", "position", "competitor",
                         "competitor_position"],
    "current-rankings": ["keyword", "volume", "best_position", "best_position_url", "sum_traffic"],
    "seasonality": ["keyword", "month", "volume"],
}


def read_csv(kind):
    p = D / f"keywords/{K['file_prefix']}-{kind}.csv"
    if not p.exists():
        sys.exit(f"build_keywords: missing {p}")
    rows = list(csv.DictReader(open(p, encoding="utf-8-sig", newline="")))
    missing = [c for c in COLUMNS[kind] if rows and c not in rows[0]]
    if missing:
        sys.exit(f"build_keywords: {p.name} has no column(s) {missing} (see references/keyword-files.md)")
    return rows


def opt_int(v):
    """A number, or None for an empty cell (no data is not zero)."""
    v = (v or "").strip()
    return int(float(v)) if v else None


def opt_traffic(v):
    """Estimated visits keep their fraction for sorting; the report rounds them."""
    v = (v or "").strip()
    return float(v) if v else None


ke = read_csv("keyword-research")
se = read_csv("current-rankings")
gpath = D / "google-checks.json"
google = {g["q"]: g for g in json.load(open(gpath, encoding="utf-8"))["results"]} if gpath.exists() else {}
gfield = K.get("google_position_field", "position")
se_pos = {r["keyword"]: opt_int(r["best_position"]) for r in se if opt_int(r["best_position"]) is not None}

CLUSTER_KEY = K["clusters"]
P1_PRIO = K.get("p1_priorities", ["P1"])
APP_PRIO = K.get("appendix_priorities", ["P2", "P3"])
# Only clusters that hold report keywords need a key; excluded rows (other brands, no audience) are skipped.
unknown = sorted({r["cluster"] for r in ke if r["priority"] in P1_PRIO + APP_PRIO} - set(CLUSTER_KEY))
if unknown:
    sys.exit(f"build_keywords: clusters missing from keywords.clusters: {unknown}")


def target(kw, cluster):
    """First matching rule wins: {"cluster": name} or {"contains": [substrings of the lower-case keyword]}."""
    k = kw.lower()
    for rule in K["target_rules"]:
        if rule.get("cluster") == cluster or any(w in k for w in rule.get("contains", [])):
            return rule["target"]
    return K["target_default"]


def position(kw, tool_pos):
    if kw in google:
        return google[kw][gfield], "google"
    if kw in se_pos:
        return se_pos[kw], "tool"
    if tool_pos is not None:
        return tool_pos, "tool"
    return None, "none"


def row(r, with_target):
    pos, src = position(r["keyword"], opt_int(r["position"]))
    out = {"kw": r["keyword"], "vol": opt_int(r["volume"]), "kd": opt_int(r["kd"]),
           "prio": r["priority"], "pos": pos, "pos_src": src,
           "competitor": r["competitor"] or "", "competitor_pos": opt_int(r["competitor_position"])}
    if with_target:
        out["target"] = target(r["keyword"], r["cluster"])
    return out


def grouped(rows, with_target):
    groups = {}
    for r in rows:
        groups.setdefault(CLUSTER_KEY[r["cluster"]], []).append(row(r, with_target))
    for g in groups.values():
        g.sort(key=lambda x: -(x["vol"] or 0))
    return groups


p1 = grouped([r for r in ke if r["priority"] in P1_PRIO], True)
appendix = grouped([r for r in ke if r["priority"] in APP_PRIO], False)

strengths = []
origin = CFG["brand"]["site"].rstrip("/")
for r in sorted(se, key=lambda r: -(opt_traffic(r["sum_traffic"]) or 0)):
    if any(w in r["keyword"] for w in K.get("strengths_exclude", [])):
        continue
    pos, _ = position(r["keyword"], None)  # a Google check wins over the tool here too
    if pos is None:  # no position, or not in Google's top 10 on the audit day: not a strength
        continue
    url = r["best_position_url"].replace(origin, "") or "/"
    strengths.append({"kw": r["keyword"], "vol": opt_int(r["volume"]), "pos": pos,
                      "path": url, "traffic": opt_traffic(r["sum_traffic"])})
    if len(strengths) == K.get("strengths_count", 25):
        break

season = {}
for r in read_csv("seasonality"):
    if opt_int(r["volume"]) is not None:  # a month with no data is left out, not drawn as zero
        season.setdefault(r["keyword"], []).append([r["month"], opt_int(r["volume"])])
for series in season.values():
    series.sort()

missing_order = [g for g in K["p1_order"] + K["appendix_order"] if g not in set(CLUSTER_KEY.values())]
if missing_order:
    sys.exit(f"build_keywords: p1_order/appendix_order name unknown cluster keys: {missing_order}")
left_out = sorted((set(p1) - set(K["p1_order"])) | (set(appendix) - set(K["appendix_order"])))
if left_out:
    sys.exit(f"build_keywords: groups with keywords are missing from p1_order/appendix_order: {left_out}")

out = {
    "p1": p1, "p1_order": K["p1_order"],
    "strengths": strengths,
    "appendix": appendix, "appendix_order": K["appendix_order"],
    "target_paths": K["target_paths"],
    "season": season,
    "totals": K["totals"],
    "counts": {"p1": sum(len(v) for v in p1.values()), "appendix": sum(len(v) for v in appendix.values()),
               "strengths": len(strengths), "all_keywords": len(ke)},
}
json.dump(out, open(D / "keywords-report.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(out["counts"], {k: len(v) for k, v in p1.items()}, {k: len(v) for k, v in appendix.items()})
missing_season = [k for k in CFG.get("season_keywords", []) if k not in season]
if missing_season:
    print(f"build_keywords: season_keywords not in the seasonality file: {missing_season}")
