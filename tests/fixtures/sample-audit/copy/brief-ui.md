# Brief — short UI labels for the Harbor & Pine audit report

Same report, same reader, same voice as copy/brief.md (read it first for voice rules: plain English, short, no exclamation marks, no em or en dashes, decimal point). Facts only from data/findings.md.

Write the short fixed labels the report layout needs. Return ONE JSON object with exactly these keys and nothing else:

{
  "html_title": "browser tab title, max 7 words, names harborpine.example and that this is a website audit",
  "nav_aria": "screen-reader name for the report's section menu, max 3 words",
  "nav_overview": "menu label for the overview section, max 2 words",
  "nav_fixlist": "menu label for the fix list section, max 2 words",
  "seen": "label above 'what I saw' text in each finding, max 3 words",
  "why": "label above 'why it matters' text, max 4 words",
  "fix": "label above 'what to do' text, max 2 words",
  "glossary_title": "title of the glossary, 1 word",
  "grade_aria": "screen-reader prefix before a grade word, 1 word",
  "stat_keywords": "label under the number 6: keywords where harborpine.example shows in Google (keyword tool estimate), max 7 words",
  "stat_top3": "label under the number 2: of those in positions 1 to 3, max 5 words",
  "stat_traffic": "label under '~150': estimated visits per month from search engines, max 6 words",
  "stat_fcp": "label under '2.1–2.6 s': time until first content appears on a phone, max 6 words",
  "stat_lcp": "label under '4.4–5.1 s': time until main content (LCP) appears; mention Google's good limit 2.5 s, max 9 words",
  "stat_js": "label under '1.8 MB': amount of JavaScript the phone runs before anything shows, max 7 words",
  "band_good": "speed chart band 0-2.5 s, 1 word (Google: good)",
  "band_mid": "speed chart band 2.5-4 s, 1-2 words (Google: needs improvement)",
  "band_poor": "speed chart band over 4 s, 1 word (Google: poor)",
  "mark_fcp": "chart marker label: first content 2.1–2.6 s, max 5 words incl. the numbers",
  "mark_lcp": "chart marker label: main content (LCP) 4.4–5.1 s, max 5 words incl. the numbers",
  "mark_target": "chart marker label: Google's limit 2.5 s, max 4 words incl. the number",
  "speed_chart_aria": "screen-reader description of the speed chart, 1 sentence",
  "searches_unit": "unit after a number in a tooltip, e.g. '5,558 ___', 1 word (searches)",
  "season_aria": "screen-reader text that continues 'tea gift box: ___ 2,100', describing monthly searches November 2025 to October 2026 and the peak, max 10 words"
}
