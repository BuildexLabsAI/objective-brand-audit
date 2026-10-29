# Objective Brand Audit

A Claude Code skill (skill name `objective-brand-audit`) that audits one website and writes a fact-checked English
report (HTML + A4 PDF) in the audited brand's own look. Phases 1–4 (intake, recon, plan with the user's yes,
audit → `data/findings.md`) can run alone; The Ex-Designer skill (`BuildexLabsAI/ex-designer`) calls them that way.

## Commands

- Sanity check: `bash .github/scripts/check-standard.sh`
- Skill tests: `python3 tests/run_all.py` (about 10 seconds; opens the Mac's Google Chrome headless, no network).
  All 19 checks must pass.
- Denylist hashes, after a change to the local plain list `tests/denylist.txt` (gitignored, on the owner's Mac
  only): `python3 tests/denylist.py`.
- Install the skill (once per machine), from the repository root:
  `mkdir -p ~/.claude/skills && ln -s "$PWD/src/objective-brand-audit" ~/.claude/skills/objective-brand-audit`,
  then start a new Claude Code session.

Add each command here when it exists and has run once.

## Project conventions

- **Layout.** The skill lives in `src/objective-brand-audit/` (`SKILL.md` at its root). Only that folder is linked
  into `~/.claude/skills/`; nothing else in the repository loads as part of the skill.
- **The phase 1–4 contract.** The Ex-Designer runs "phases 1–4 of the brand-audit skill" and reads
  `data/findings.md`. Keep the phase numbers, the order and that file name, or change both skills together.
- **Report language is English.** The kit's fixed labels (grades, months, units, anchors) are English; every other
  visible string comes from the copy JSON.
- **No client data here.** The repository is public. The sample audit and the test site are invented and use the
  reserved `.example` domain. A real site, client or person is never named in a file, a commit message or a pull
  request. The denylist ships only as hashes (`tests/denylist.sha256`).
- **Who writes text.** Report copy comes from a writer that is not the checker (SKILL.md phase 5). In this
  repository, the sample audit's copy was written by GPT through the Codex CLI from its briefs. Code, specs and
  these files are not copy.
- **Merging follows CI.** If a check is red or cannot run, the agent opens the pull request and gives the owner the
  link; the owner decides and merges. If every check is green and the merge is agreed, the agent squash-merges it.

<!-- buildexlabs-standard:start (copy of src/agents-block.md in BuildexLabsAI/.github; edit it there, not here) -->
## BuildexLabsAI repository standard

Every repository in the BuildexLabsAI organization follows these rules. The full version, with
the reasons, is CONTRIBUTING.md in the BuildexLabsAI/.github repository.

- **Layout.** The top level holds README.md, AGENTS.md, CLAUDE.md, DECISIONS.md, .gitignore,
  src/, tests/, docs/, scripts/, tool config files, and folders a tool requires at the root
  (such as public/ or supabase/). All code lives in src/. Inside src/ the framework's own
  convention wins: src/app/ for Next.js, src/<package>/ for Python.
- **Names.** Lowercase kebab-case (`athlete-model.md`) for the repository, the top level and
  everything in docs/. Everywhere: no spaces, no non-ASCII characters, and no two names that
  differ only by letter case. Inside src/, tests/ and scripts/, follow the language's own
  convention (`snake_case.py`, `Button.tsx`).
- **Never commit** secrets (.env files, keys, tokens). Media, documents and large files may go
  into git; GitHub itself refuses any file over 100 MiB. Small assets the app ships (icons,
  fonts, wasm) belong in src/ or public/.
- **Exceptions** go in `.github/standard-exceptions`, one path per line with its reason:
  `prisma  # Prisma reads its schema from a folder at the root`.
- **Branches.** Never commit to main directly. Name branches `feat/…`, `fix/…`, `docs/…`,
  `chore/…`, `refactor/…` or `test/…`. Agent tools' own prefixes (`claude/…`, `codex/…`) are
  accepted.
- **Commits and pull request titles** follow Conventional Commits:
  `feat(api): add athlete height endpoint`. Pull requests are squash-merged, so the title
  becomes the commit on main.
- **Decisions** that the code and git log cannot show go in DECISIONS.md, one dated line each.
- **README.md** is written with the readme-generator skill: its sections for the project type,
  plus the template's Run it locally, Deploy, Media and large files, First-time setup and Owner.
  Then the simple-english skill makes one Simplified Technical English (STE) pass over all prose,
  in its default mode. Run every command before it goes in and keep only the ones that work.
  Codex reviews it at high reasoning effort before it reaches main.
- **Check before you push:** `bash .github/scripts/check-standard.sh`. CI runs the same check
  on every pull request.
<!-- buildexlabs-standard:end -->
