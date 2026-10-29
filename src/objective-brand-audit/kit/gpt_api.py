"""Send a brief to GPT through the OpenAI API: the second copy route, used when the Codex CLI is missing or its
quota is closed.

Usage:  python3 gpt_api.py --audit <audit-dir> --out copy/report-copy.raw.txt copy/brief.md data/findings.md [more files]
The first file is the brief; the rest are its sources. The key comes from $OPENAI_API_KEY and is never printed.
Bills per token: print the usage line, and tell the user the route switched and what it cost (price per token from
OpenAI's price list). Pick the model with --model or $OPENAI_MODEL.
"""
import argparse, json, os, sys, urllib.error, urllib.request
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--audit", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--model", default=os.environ.get("OPENAI_MODEL", "gpt-5"))
ap.add_argument("files", nargs="+")
a = ap.parse_args()
root = Path(a.audit).expanduser().resolve()
key = os.environ.get("OPENAI_API_KEY") or sys.exit(
    "gpt_api: OPENAI_API_KEY is not set; the OpenAI route is down, go to the next copy route (SKILL.md phase 5)")
parts = [f"=== {f} ===\n{(root / f).read_text(encoding='utf-8')}" for f in a.files]
prompt = ("Follow the brief in the first file exactly. The other files are its only sources. "
          "Return only what the brief asks for (one JSON object), nothing else.\n\n" + "\n\n".join(parts))
body = {"model": a.model, "input": prompt, "reasoning": {"effort": "high"}}
req = urllib.request.Request("https://api.openai.com/v1/responses", data=json.dumps(body).encode(),
                             headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
try:
    r = json.load(urllib.request.urlopen(req, timeout=900))
except urllib.error.HTTPError as err:
    sys.exit(f"gpt_api: OpenAI answered {err.code}: {err.read().decode(errors='replace')[:300]}")
text = "".join(c.get("text", "") for o in r.get("output", []) if o.get("type") == "message" for c in o.get("content", []))
if not text:
    sys.exit(f"gpt_api: empty answer: {json.dumps(r)[:500]}")
(root / a.out).write_text(text, encoding="utf-8")
print(f"wrote {root / a.out} ({len(text)} chars); model {a.model}; usage {r.get('usage')}")
