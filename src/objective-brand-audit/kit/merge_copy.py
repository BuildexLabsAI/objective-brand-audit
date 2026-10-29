"""Merge a GPT answer into <audit>/copy/report-copy.json.

Usage:  python3 merge_copy.py --audit <audit-dir> <answer.json>
Top-level keys in the answer replace the same keys in report-copy.json (e.g. "search_extra" from round 2).
"glossary_add" items are appended to "glossary" (a term that already exists is skipped).
Keeps a copy of the previous file as copy/report-copy.prev.json until the merge is checked.
"""
import argparse, json, shutil
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--audit", required=True)
ap.add_argument("answer")
a = ap.parse_args()
root = Path(a.audit).expanduser().resolve()
target = root / "copy/report-copy.json"
answer_path = Path(a.answer) if Path(a.answer).is_absolute() else root / a.answer
raw = answer_path.read_text(encoding="utf-8").strip()
if raw.startswith("```"):  # GPT sometimes wraps JSON in a code fence
    raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
ans = json.loads(raw)
copy = json.loads(target.read_text(encoding="utf-8"))
shutil.copy(target, root / "copy/report-copy.prev.json")
for k, v in ans.items():
    if k == "glossary_add":
        have = {g["term"] for g in copy.get("glossary", [])}
        for g in v:
            if g["term"] not in have:
                copy.setdefault("glossary", []).append(g)
                have.add(g["term"])
    else:
        copy[k] = v
target.write_text(json.dumps(copy, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"merged {sorted(ans)} into {target}")
