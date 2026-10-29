# Brief — English copy for the <Brand> website audit report

<!-- Template. Claude replaces every <…>, deletes lines that do not apply (e.g. legal parts for a non-shop,
     closing for a friend), and keeps the voice rules unchanged. Save as <audit>/copy/brief.md. -->

## Your job
Write all reader-facing English text for a branded website audit report about <domain>. Claude will place your text into a designed HTML/PDF report in <Brand>'s own brand look. You write the words only. Return ONE JSON object that matches the schema below. No markdown, no commentary outside the JSON.
The keyword section (search_extra) comes later in a separate brief; leave it out of this answer.

## Sources (the only facts you may use)
1. `data/findings.md` — verified audit findings. Every claim, number, date, URL and name in the report must come from here.
2. `data/keywords/<prefix>-seo-plan.md` — the user's keyword notes, for context on seasons and competitors only. Do not copy its sentences. (Delete this line if there is no such file.)
Do not invent numbers, customer quotes, sales figures, prices, money estimates, growth percentages or anything else not in these files. If a number is missing, write without it.

## Reader
<Who owns and runs the business, what they know well, what they are not (e.g. "not web developers"). Who they may forward the report to (e.g. their platform provider <provider>). How they read it (e.g. on a phone, a PDF sent by message).>

## Goal
After reading, the reader knows (1) what is costing them <sales | bookings | enquiries> right now, (2) what to fix first and who does it (<Brand> itself, the platform provider <provider>, or a lawyer), and (3) <the timely reason to act now, e.g. the gift season>. The report should feel fair: every area credits what already works.

## Author and voice
- Author: <the byline name>. First person singular where natural ("I went through the site…", "I measured…"). Address the reader as "you".
- Short sentences, active voice, direct, no filler. Name weaknesses plainly. No flattery, no hype. Polished English, not formal.
- Plain language. Explain every technical term in plain words the first time it appears (e.g. search engine, meta description, H1, LCP, JavaScript, server-side rendering, Search Console). The glossary in the schema lists them again.
- Concrete analogies are welcome when they make a technical point clear to this reader (<e.g. a shop door, a shop window, a checkout queue>), at most one per section. Keep them short.
- No exclamation marks. No "Hi"/"Welcome" openers. No buzzwords (optimize, leverage, seamless, innovative, solution, potential, synergy, "take it to the next level"). No em dashes; use a comma, a colon or a new sentence. En dash only in number ranges (5.2–5.7 s). Do not open every paragraph with "But".
- Number formats: decimal point (7.95 €, 8.5 s), comma as thousands separator (3,200), "searches a month".
- Refer to the business by its brand name or its domain (<domain>), never by a family surname that reads as a person.
- Grades use a four-step scale: Excellent, Good, Needs work, Poor. Grades are fixed in findings.md; do not change them and use these exact words.
- Legal points (L…): state what the sources say and recommend a lawyer check. Say clearly that the report is not legal advice. Do not say the company is "breaking the law"; say the current wording "does not meet" or "conflicts with" what the law or the court says, as findings.md states.
- Respectful of the company: problems are fixable, mostly small. Do not soften the important ones: <list the top issues from findings.md>.

## Structure rule
The report gives the full picture first: for every area, everything that is wrong, how to fix it and everything that already works. Only after all areas comes a separate part "what to fix first". The overview and the section leads must NOT say where to start or what to fix first; priorities appear only in quickfix and fixlist.

## JSON schema
{
  "cover": {
    "kicker": "max 4 words, what kind of document",
    "title": "max 9 words, the report's main message, not just 'Audit'",
    "subtitle": "1 sentence, max 22 words",
    "meta": ["Prepared by: <the byline name>", "date line <D Month YYYY>", "scope line max 8 words"]
  },
  "overview": {
    "title": "max 8 words",
    "lead": "max 60 words: the overall state, what is good and what is wrong; no priorities, no 'start here'",
    "structure_note": "max 40 words: how the report is organised (each area: what is wrong, how to fix it, what works; then 'what to fix first', the full fix list<, and the keyword appendix>)",
    "grades_title": "max 4 words",
    "grades_note": "1 sentence explaining the four-step scale",
    "grades": [ {"area": "exact area name from findings", "grade": "exact grade", "reason": "max 16 words"} ]  // same order as findings.md
  },
  "sections": [
    {
      "id": "<section ids exactly: sales | design | search | speed | trust>",
      "nav": "max 2 words, for the menu",
      "title": "max 8 words",
      "lead": "2–3 sentences, max 55 words: what this section covers; no priorities",
      "findings": [
        {
          "id": "S1 etc. exactly as in findings.md",
          "title": "max 9 words, says the problem in plain words",
          "seen": "what I saw, 1–3 sentences, max 55 words, with the exact numbers",
          "why": "why it costs sales or trust, 1–2 sentences, max 35 words",
          "fix": "what to do, 1–2 sentences, max 40 words",
          "effort": "short, e.g. '15 min', '1–2 h', 'half a day'",
          "owner": "<Brand> | <provider> | <Brand> + <provider> | <Brand> + lawyer",
          "shot_caption": "max 14 words, only if the finding lists a screenshot in brackets, else empty string"
        }
      ],
      "works_title": "max 4 words, the same wording in every section is fine",
      "works": [ {"title": "max 6 words", "body": "1–2 sentences, max 30 words"} ]  // 2–4 items from findings.md "What works, per section"
    }
  ],
  // Sections and findings to include: <section id: finding ids, e.g. sales: S1–S6 … >
  "quickfix": {
    "nav": "max 2 words",
    "title": "max 8 words",
    "lead": "max 45 words: these are the fastest and most important changes picked from the findings above",
    "top5_title": "max 7 words",
    "top5": [ {"title": "max 7 words", "body": "2 sentences, max 40 words", "effort": "short, from findings", "owner": "same owner values"} ],  // the 5 in findings order
    "quick_title": "max 6 words",
    "quick": [ "max 14 words each" ]  // the 5-minute fixes listed in findings
  },
  "speed_extra": {
    "analogy": "1–2 sentences, plain analogy for why the measured problem makes the phone wait",
    "metrics_caption": "1 sentence, how the speed test was done, from findings T1 (say if it is our own lab test)"
  },
  "legal_extra": {
    "disclaimer": "1–2 sentences: not legal advice, name the sources used (e.g. the EU Consumer Rights Directive, the EU Court of Justice), check with a lawyer"
  },
  "fixlist": {
    "title": "max 5 words",
    "lead": "max 40 words: the complete list of every finding as a task, grouped by urgency, with effort and who does it",
    "groups": [ {"label": "max 4 words, e.g. 'This week'", "items": [ {"id": "finding id", "action": "max 14 words, imperative", "effort": "short", "owner": "same owner values"} ] } ]  // 3–4 groups by urgency; every finding id appears exactly once
  },
  "method": {
    "title": "max 5 words",
    "body": "max 110 words, plain account of what was checked and how, from the Method section; mention no order was placed and no personal data was entered"
  },
  "glossary": [ {"term": "term", "def": "max 18 words"} ],  // 8–12 terms used in the report
  "closing": {  // only for a client report (the user decides); delete for a friend
    "title": "max 6 words",
    "body": "2 sentences, max 40 words; offer to go through the report together; no sales pitch, no exclamation marks",
    "contact": "<the byline name>"
  }
}

## Checks before you answer
- Every number matches findings.md exactly (<list the key numbers: prices, counts, seconds, dates>).
- No exclamation marks, no em dashes, no invented facts, no priorities in overview or section leads.
- Valid JSON (double quotes, no trailing commas, no comments).
