"""List every number in the GPT copy that does not appear in the sources (a helper, not a verdict).

Usage:  python3 factcheck.py --audit <audit-dir> [copy/report-copy.json copy/ui-labels.json]
Sources: data/findings.md, data/keywords-report.json, data/google-checks.json, audit.json.
Numbers are compared as values ("3,200" = "3200", "7.50" = "7.5"); a comma is a thousands separator. Each flagged number must be checked by hand:
either it is derived correctly (say how) or it goes back to GPT in a corrections file. Unflagged numbers can still
be used in the wrong place, so read the claims too.
"""
import argparse, json, re
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--audit", required=True)
ap.add_argument("files", nargs="*", default=["copy/report-copy.json", "copy/ui-labels.json"])
a = ap.parse_args()
root = Path(a.audit).expanduser().resolve()
# A minus sign counts unless a letter, digit or point stands before it: "-3.00", ":-3", "[-3" are negative,
# a range ("2.1-2.6") is not.
NUM = re.compile(r"(?:(?<![\w.])[-−])?(?:(?<![\w.,])\d{1,3}(?:,\d{3})+(?:\.\d+)?(?![\d,])|(?<![\w])\d+(?:\.\d+)?)")


def values(text):
    out = set()
    for m in NUM.findall(text):
        try:
            out.add(float(m.replace(",", "").replace("−", "-")))
        except ValueError:
            pass
    return out


src = ""
for rel in ("data/findings.md", "data/keywords-report.json", "data/google-checks.json", "audit.json"):
    p = root / rel
    if p.exists():
        src += p.read_text(encoding="utf-8") + "\n"
known = values(src)


def strings(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from strings(v, f"{path}.{k}" if path else k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from strings(v, f"{path}[{i}]")
    elif isinstance(o, str):
        yield path, o


flags = 0
for rel in a.files:
    for path, text in strings(json.loads((root / rel).read_text(encoding="utf-8"))):
        bad = sorted(v for v in values(text) if v not in known)
        if bad:
            flags += 1
            print(f"{rel}:{path}: {', '.join(f'{v:g}' for v in bad)}\n    {text[:160]}")
print(f"{flags} field(s) with numbers not found in the sources")
