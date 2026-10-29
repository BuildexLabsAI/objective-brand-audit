# Decisions

Choices that neither the code nor the git log shows, newest first. One line each:
`YYYY-MM-DD: the decision, and why.`

- 2026-10-29: The skill is a public, cleaned copy of the owner's private audit skill, named Objective Brand Audit, so that The Ex-Designer's README links only to skills anyone can install; the private skill stays as it is and is not linked to this repository.
- 2026-10-29: Reports are English only, because English needs no translation tables and every visible string except the kit's fixed labels already comes from the copy JSON (the owner chose English over English and Finnish).
- 2026-10-29: The copy route is tiered: Codex CLI, then the OpenAI API with `$OPENAI_API_KEY`, then Claude with the copywriting skill, because a public user may have neither GPT route; the fact check runs on every route (the owner's choice).
- 2026-10-29: Consumer-law checks use EU sources (Directive 2011/83/EU, CJEU C-249/21, Directive (EU) 2023/2673) instead of one country's authority, so the checks fit any EU shop; outside the EU the legal part uses that country's law or is left out.
- 2026-10-29: The keyword files have their own documented English CSV columns (`references/keyword-files.md`) instead of one tool's export format, so any keyword tool can feed them.
- 2026-10-29: The sample audit, its test site and every domain in it are invented under the reserved `.example` top-level domain, and its report copy was written by GPT from the same briefs a real audit uses, so the tests also prove the briefs work.
- 2026-10-29: The repository starts from one fresh commit, so no history from the private skill can name a client.
- 2026-10-29: MIT licence, copyright BuildexLabsAI; the report icons are Phosphor Icons (MIT), with their licence next to them.
