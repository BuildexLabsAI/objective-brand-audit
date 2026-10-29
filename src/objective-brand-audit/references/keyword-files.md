# Keyword files

The keyword part of the report is optional. It needs three CSV files (comma-separated, UTF-8, a header row) and
may have one notes file, all in `<audit>/data/keywords/` and all named with the same prefix
(`keywords.file_prefix` in audit.json). Build them from the exports of any keyword tool (Ahrefs, Semrush, Google
Search Console, Keyword Planner). An empty cell means "no data", never zero.

## `<prefix>-keyword-research.csv` — the keywords the site should win

| Column | Meaning |
|---|---|
| `keyword` | The search, as typed |
| `volume` | Searches per month in the target country (the tool's estimate) |
| `kd` | Keyword difficulty 0–100 from the tool; empty when unknown |
| `priority` | `P1` (report table), `P2` or `P3` (appendix); any other value is left out of the report |
| `cluster` | Topic group; every cluster of a P1–P3 row needs a key in `keywords.clusters` |
| `position` | The site's position in the tool; empty when the tool has no data |
| `competitor` | The best-placed competitor domain; may be empty |
| `competitor_position` | Its position; may be empty |

## `<prefix>-current-rankings.csv` — what the site ranks for now

| Column | Meaning |
|---|---|
| `keyword` | The search |
| `volume` | Searches per month |
| `best_position` | The site's best position |
| `best_position_url` | The page that ranks (full URL; the site's origin is stripped in the report) |
| `sum_traffic` | Estimated visits per month from this search |

## `<prefix>-seasonality.csv` — searches per month

| Column | Meaning |
|---|---|
| `keyword` | The search (use the ones named in `season_keywords`) |
| `month` | `YYYY-MM` |
| `volume` | Searches that month |

## `<prefix>-seo-plan.md` (optional)

The user's own keyword notes or plan. The copy briefs name it as context only: the writer never copies its
sentences.

## Google checks override the tool

`data/google-checks.json` (method in `checks.md` §4) wins over the tool's position for each keyword it holds. Only
those keywords can show "not in Google's top 10"; a keyword with no data shows "no data".
