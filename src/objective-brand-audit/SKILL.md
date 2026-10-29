---
name: objective-brand-audit
description: Use when the user asks for a website or web-shop audit report in the audited brand's own look (logo, colours, fonts), such as "objective brand audit", "audit <domain>", "website audit report" or "brand audit of <domain>": a fact-checked HTML report and A4 PDF covering the sales path, design, search visibility, keywords, speed and consumer law. Also use when another skill asks for this skill's phases 1–4 (intake, recon, plan, audit → data/findings.md), and when continuing an audit folder that holds audit.json and data/findings.md.
---

# Objective Brand Audit

## Overview
Produces a fact-checked English audit report of one website in the audited brand's own look (logo, colours, fonts,
photos): a self-contained HTML file and an A4 PDF that reads well on a phone. Every claim is checked on the live site
and every number has a unit, a source and a date. The user approves at four checkpoints.
**Nothing is ever sent to the site's owner or anyone else. The user decides who gets what, and how.**

Talk to the user in their language, plain words, one question per message (intake is one message).
Everything written to files is English.

Other skills can call phases 1–4 alone (intake, recon, plan with the user's yes, audit). Their output is
`data/findings.md` in the audit folder; the copy and PDF phases run only when the user wants the full report.

## Where things live
| What | Path |
|---|---|
| One audit | `<audits folder the user picks>/<slug>-<YYYY-MM-DD>/` (e.g. `harborpine-2026-10-29`) |
| Report kit (scripts, CSS, icons) | `kit/` in this skill's folder (= `KIT`) |
| Templates (audit.json, findings, briefs, corrections) | `templates/` in this skill's folder |
| Exact check methods (bots, API, law, Google, speed, tokens) | `references/checks.md` |
| Keyword file formats | `references/keyword-files.md` |
| Worked example of every file (an invented shop) | `tests/fixtures/sample-audit/` in the skill's repository |

Audit folder layout: `audit.json`, `handoff.md`, `data/` (findings.md, keywords/, google-checks.json, perf.json,
keywords-report.json), `copy/` (briefs, corrections, report-copy.json, ui-labels.json), `media/` (logo, brand/,
shots/, assets/fonts/), `outputs/` (`<slug>-audit.html` + `.pdf`).

Needs: Python 3 with Pillow (`pip install pillow`), Google Chrome (or `CHROME=<path>`), and for the speed test
Playwright (`pip install playwright`). `pdfinfo`/`pdftoppm` (poppler) for the page check.

## Phases and checkpoints

### 1. Intake — CHECKPOINT (the user answers)
One message, numbered; skip any item the user already gave:
1. The site URL.
2. Who receives the report: a friend or the user's own team (no closing block, `include_closing_cta: false`) or a client (closing block with an offer to go through it together, `include_closing_cta: true`).
3. The name for the byline ("Prepared by: <name>") and the folder where audits live.
4. Keyword files, if any, in the format of `references/keyword-files.md`. No files → no keyword part.
5. Logo file, or permission to take it from the site.

Files the user gives are copied into the audit folder after the plan is approved. Audit folder name: brand name in
lower-case ASCII + audit date, e.g. `harborpine-2026-10-29`.

### 2. Recon (read-only, short)
In a real browser (the Claude app's browser pane, Claude in Chrome, or another browser tool you have), first visit
in a fresh tab: screenshot the cookie banner and any popups before closing anything (they are often a finding),
then decline non-essential cookies. Then: what the site sells and to whom, platform (footer, checkout, HTML), shop
or not, catalogue size (sitemap), robots.txt, the purchase path pages, the country it sells to (which consumer law
applies), the season or deadline that makes the report timely.

### 3. Plan — CHECKPOINT (wait for a clear yes)
Numbered steps, each with `→ verify:`. State: sections and their ids, pages on the purchase path, whether the
e-commerce checks run (catalogue API, consumer law and for which country), keyword part yes/no, what gets downloaded
(logo, 1–2 brand photos, a header texture, Google fonts), deliverables, and "done =".
The approved plan is one sprint. If the context grows heavy, stop at a checkpoint, update the audit's `handoff.md`
and offer to continue in a new session.

### 4. Audit (Claude)
1. Create the audit folder; copy `templates/audit.json` and `templates/findings.md` into it.
2. Audit the live site for the sales path, the design (audit only, no code changes) and search (technical and
   on-page). Use the matching skills when they are installed (for example **page-cro**, **seo-audit**,
   **redesign-existing-projects** in audit-only mode); otherwise do the same checks by hand.
3. Screenshots in the browser: desktop 1440×900 and mobile 375×812. Walk home → category → product → cart → checkout up to the order button. Never place an order or type personal data; remove the test item from the cart. Save each screenshot you use as `media/shots/d-NN-<what>.jpg` / `m-NN-<what>.jpg` straight away (the Claude desktop app keeps browser-pane screenshots under `~/.claude/projects/<session-dir>/<session-id>/tool-results/`).
4. Speed, bots/AI crawlers/link previews, catalogue API (e-commerce), consumer law (e-commerce), Google spot checks: exact methods in `references/checks.md`.
5. Keywords (only with keyword files): files into `data/keywords/`, fill the `keywords` block of audit.json, then `python3 KIT/build_keywords.py --audit <audit>`.
6. Write `data/findings.md` from the template: the single source of truth. Every claim checked on the live site, every number with unit, source and date, every screenshot named in [brackets], Fix + Effort + owner on each finding, grades on the four-step scale (Excellent / Good / Needs work / Poor), "What works, per section", Top 5, quick fixes, Method.

### 5. Copy — a writer that is not the checker
The report copy is written from the briefs by a separate writer, and Claude checks it. Fill
`templates/brief-copy.md` → `copy/brief.md` and `templates/brief-ui.md` → `copy/brief-ui.md`. With keyword files,
after the first copy is checked: `templates/brief-round2-keywords.md` → `copy/brief-round2.md`.
Pick the first route that works, and tell the user which one ran:
1. **Codex CLI** (`codex` on the PATH; run it in the background, it takes minutes):
   ```bash
   cd "<audit>" && codex exec --skip-git-repo-check -s read-only -C "<audit>" -c model_reasoning_effort="high" -o copy/report-copy.raw.txt "Read copy/brief.md and follow it exactly. Your sources are data/findings.md and the files the brief names. Return only the single JSON object the brief specifies." < /dev/null > copy/codex-run.log 2>&1
   ```
   Same for `brief-ui.md` → `copy/ui-labels.raw.txt`, and round 2 → `copy/round2.raw.txt` (merge it with `python3 KIT/merge_copy.py --audit <audit> copy/round2.raw.txt`).
2. **OpenAI API** (no Codex, or its quota is closed, and `$OPENAI_API_KEY` is set): `python3 KIT/gpt_api.py --audit <audit> --out copy/<name>.raw.txt copy/brief.md data/findings.md`. Report the cost from the printed usage.
3. **Claude** (neither of the above): write the JSON from the brief yourself, with the **copywriting** skill if it is installed (for example from `coreyhaines31/marketingskills`). Tell the user that writer and checker are now the same model, so the fact check below matters even more.

Save the answers as `copy/report-copy.json` and `copy/ui-labels.json` (without a code fence around the JSON).
Fact check, every route: `python3 KIT/factcheck.py --audit <audit>` lists numbers that are not in the sources;
then read every claim, name and date against findings.md. With route 1 or 2, every problem goes back to the writer
as `copy/corrections-<N>.md` (template: Where / Now / Why with the fact) and Claude never edits the wording itself;
put the corrected text into the JSON files. Repeat until clean.

### 6. Build and self-check (Claude)
1. Fill audit.json: brand tokens from the site's computed styles, fonts (`KIT/fetch_fonts.py`), logo, cover photo, header texture, screenshot map per finding id, section roles, speed numbers. Field reference below.
2. `python3 KIT/build_report.py --audit <audit>` → `bash KIT/render_pdf.sh <audit>`.
3. Look at the whole result yourself before the user sees it: the HTML at 1440 px and 375 px (in the browser), and every PDF page (`pdftoppm -r 60 -png` and read each image). Check edges, tables on mobile, page breaks, label overlap in the speed chart.

### 7. Full report to the user — CHECKPOINT
Send the complete HTML and PDF (as files the user can open). Never a partial preview as the main deliverable. The
user approves content and design. Copy changes go back to the writer (corrections file); layout changes go into
audit.json or the kit.

### 8. Final review, before the user sends anything
- Every number, name and date in the final PDF traced to findings.md (factcheck.py clean + manual read).
- Legal findings: primary source URLs present, "not legal advice" in the report.
- No e-mail address the user did not ask for: `grep -o "[^ \"<>]*@[^ \"<>]*" outputs/*.html | sort -u`, check each hit.
- Page 1 of the final PDF looked at (see Landmines).
- Clean up superseded drafts (`*.raw.txt` once merged, `*.log`, `report-copy.prev.json`, old PDFs, unused screenshots) and report each deletion to the user in the same turn.
- Update the audit's `handoff.md`.

## Report structure (fixed)
cover → overview (grades only, no priorities) → one section per area, each with findings (what I saw / why it matters / what to do / effort / owner, screenshots) and "What already works" → "Fix first" (top 5 + 5-minute fixes) → full fix list (every finding once, grouped by urgency) → keyword appendix → method + glossary → closing block only for clients.

Keyword part (inside the search section, from keywords-report.json): totals (keywords, top 3, ~visits/month) → 25 current strengths → seasonality small multiples (`season_keywords`, shared y-axis) → all P1 keywords with KD and the page that should win each search → the order of the search work. Appendix: all P2/P3 keywords by topic.

## audit.json fields
| Field | Meaning |
|---|---|
| `output_name`, `lang`, `audit_date`, `recipient` | File name of HTML/PDF; `en`; date; `friend` or `client` |
| `include_closing_cta` | `true` only for a client report (renders `copy.closing`) |
| `brand.name`, `brand.site` | Logo alt text; origin stripped from the keyword tool's URLs |
| `brand.logo` | SVG or PNG kept as is; other formats become JPEG |
| `brand.cover_image`, `brand.bar_image` | Cover photo and header/closing texture (`path`, `max_w`, `quality`); both optional |
| `tokens` | Required: `--accent --ink --ink-2 --muted --line --line-2 --panel --paper --axis --on-dark` (6-digit hex) and `--font --cond --display` (font stacks) |
| `fonts` | `dir`, `manifest`, `subsets`, `include` [[family, weight], …] — every pair must exist in manifest.txt; `include: []` with an empty manifest uses the font stacks only |
| `sections` | `grade_order` (section ids in grade order) and which id is `search`, `speed`, `legal` |
| `shots` | finding id → [[file, "d" or "m"], …] |
| `speed` | `fcp_s` [lo, hi], `lcp_s` [lo, hi], `js_mb` — from findings T1 |
| `perf_urls`, `season_keywords`, `keywords` | perf.py pages; seasonality charts; build_keywords config (see the sample audit) |

## Kit commands
| Step | Command (`KIT` = this skill's `kit/` folder) |
|---|---|
| Fonts | `python3 KIT/fetch_fonts.py --audit A "Family:400,700"` |
| Speed lab test | `python3 KIT/perf.py --audit A` |
| Keyword data | `python3 KIT/build_keywords.py --audit A` |
| Merge a writer's answer | `python3 KIT/merge_copy.py --audit A copy/<answer>` |
| Number check | `python3 KIT/factcheck.py --audit A` |
| HTML | `python3 KIT/build_report.py --audit A [--only overview,search]` |
| PDF | `bash KIT/render_pdf.sh A` |

## Landmines
- **Headless Chrome gets 403 on many shops** (they block the "HeadlessChrome" user agent). Never pretend to be a normal visitor's browser to get past a block. Screenshots and page checks go through a real browser tool. Two scripted checks are allowed and they are not disguises: the bot check in checks.md sends each crawler's own published user agent to see what that crawler gets, and perf.py uses Lighthouse's standard mobile test profile. If either is refused, stop and report it.
- **PageSpeed API quota** runs out fast. Fallback is `perf.py`, and the report must call it our own lab test, not Google field data.
- **"No data" in a keyword tool ≠ not ranking.** Sites often rank #1 for searches the tool has no data for. Say "not in Google's top 10" only for keywords checked in Google on the audit date (google-checks.json).
- **The writer writes every visible string**, UI labels included. Claude only places text and builds tables from data, and checks every number against findings.md.
- **Legal findings** need a primary source read on the audit day (the law, a court judgment, the national consumer authority), and the report says "not legal advice".
- **A family surname is not the brand.** Make the brief say: refer to the business by brand name or domain.
- **Numbers must not break across lines.** The build keeps a number and its unit together ("8.5 s", "2.1 MB"); an en dash in a number range (5.2–5.7 s) is correct.
- **render_pdf.sh has printed a different cover page** once in about 26 runs. Cause unknown; always look at page 1 of the final PDF.
- **`codex exec` in the background waits for input forever** unless its input is closed: keep `< /dev/null` in the command.
- **Clean up** superseded drafts and report every deletion in the same turn.
