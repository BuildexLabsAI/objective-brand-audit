# Brief, round 2: keyword section for the Harbor & Pine audit report

Read copy/brief.md for the reader, the voice rules and the fact rules (they all still apply: plain English, "you", no exclamation marks, no em dashes, en dash only in number ranges, every fact from data/findings.md or data/keywords-report.json, no invented numbers).
The rest of the report is approved (copy/report-copy.json). Write ONLY the keyword part. Return ONE JSON object {"search_extra": {...}, "glossary_add": [...]} and nothing else.

## Sources
- data/keywords-report.json: Claude builds every table and chart from it. You write the titles, labels, captions and the text around them.
- data/findings.md: H-findings and Method (Google checks, dates).

## What the keyword part shows (in this order, inside the search section)
1. Totals: 6 keywords where harborpine.example shows in Google, 2 of them in positions 1–3, ~150 visits a month (invented keyword tool estimate).
2. Current strengths: the 5 searches that bring the most estimated visits now. This is the good news.
3. Seasonality: monthly searches November 2025 – October 2026 for "tea gift box" and "chai tea".
4. All 4 P1 keywords (highest priority in the keyword research), grouped by topic, with monthly searches, KD, harborpine.example's position, the best competitor and the page on harborpine.example that should win the search.
5. The order to do the search work in.
6. Appendix (end of report): the other 5 keywords (P2 and P3), grouped by topic.

## Schema
{
  "search_extra": {
    "totals_caption": "1 sentence describing the totals above (keyword tool estimate, date)",
    "strengths_title": "max 7 words",
    "strengths_lead": "max 45 words",
    "strengths_cols": {"kw": "Search", "vol": "max 2 words", "pos": "max 2 words", "page": "max 2 words", "traffic": "max 3 words (estimated visits per month)"},
    "strengths_note": "1–2 sentences: positions and visits are keyword tool estimates 29 October 2026; the shop's own name is left out because people who search for it already know the shop",
    "season_title": "max 8 words",
    "season_caption": "2 sentences, max 45 words: when the peak is and why act now",
    "p1_title": "max 8 words",
    "p1_lead": "max 70 words: what the table shows and how to read it",
    "kd_note": "1–2 sentences: KD = keyword difficulty 0–100, how hard it is to reach the top 10; a missing KD is not zero",
    "p1_group_titles": {"tea": "max 3 words (tea in general)", "chai": "max 3 words (chai)", "gifts": "max 3 words (gift boxes and calendars)"},
    "col_labels": {"kw": "Search", "vol": "max 2 words", "kd": "KD", "pos": "max 3 words", "comp": "max 3 words", "target": "max 4 words (the page that should win the search)"},
    "target_labels": {"tea": "max 5 words (the tea category, /tea/)", "chai": "max 5 words (the chai product page)", "gifts": "max 5 words (the gifts page, /gifts/)"},
    "not_top10_label": "max 3 words, shown when the site is not in Google's top 10 (Google-checked keywords only)",
    "no_data_label": "max 3 words, shown when the keyword tool has no position",
    "table_note": "1–2 sentences: volumes are keyword tool estimates for the target country; 'not in top 10' is shown only for searches checked in Google 29 October 2026; missing tool data is not proof of not ranking",
    "order_title": "max 6 words",
    "order": ["max 18 words each, 5–7 steps, the order to do the search work in"],
    "appendix_title": "max 6 words",
    "appendix_lead": "max 45 words: the remaining keywords (P2 and P3), grouped by topic; the shop's own name is left out",
    "appendix_group_titles": {"tea": "max 4 words (tea in general)", "gifts": "max 4 words (gift boxes and calendars)", "chai": "max 4 words (chai)", "guides": "max 4 words (brewing guides)"},
    "prio_label": "max 2 words, column label for priority"
  },
  "glossary_add": [ {"term": "KD", "def": "max 18 words"}, {"term": "P1, P2 and P3", "def": "max 18 words"} ]
}

## Checks before you answer
- Every number matches keywords-report.json or findings.md exactly.
- Every cluster key and target key above has a label; no extra keys.
- Valid JSON.
