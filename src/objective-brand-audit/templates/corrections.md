# Corrections to copy/report-copy.json (round <N>)

<!-- Template. One numbered item per problem Claude found while fact-checking, or per change the user asked for.
     Claude never rewrites the text itself: it names the place, quotes the current text, and gives the reason
     and the fact. Save as copy/corrections-<N>.md. -->

Claude checked every claim against the sources<, and data/findings.md was updated (<which findings>)>. Apply ONLY the corrections below. Keep every other field word for word. Return the complete corrected JSON object (same schema as copy/brief.md), nothing else. Voice rules: copy/brief.md.

1. <Short name of the problem>.
   Where: <JSON path, e.g. sections[search].findings[H2].seen>
   Now: "<the current text, quoted exactly>"
   Why: <what is wrong and the correct fact with its source, e.g. "data/findings.md H2: … (Google check 2026-10-29)">.
   <Optional limit: "Max 55 words for the whole field.">

2. …

<!-- For a change that touches only one or two fields, ask for just those fields to save tokens:
     'Return ONLY this JSON: {"sales_lead": "...", "search_lead": "..."}' and merge them in with a small script. -->
