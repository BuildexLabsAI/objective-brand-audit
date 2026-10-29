# <domain> audit — verified findings (source of truth for the report)

Audit date: <YYYY-MM-DD>. Auditor: <the byline name>. Scope: sales/purchase path, design (audit only), search (technical + on-page)<, plus keyword research from <keyword tool> (<YYYY-MM-DD>)>.
Every finding below was checked on the live site. Screenshot files are in `media/shots/`.
Rules for this file: English, facts only, every number with its unit and source, every screenshot named in [brackets],
"Fix:" and "Effort:" on each finding, owner = who does the fix (<Brand> | <platform provider> | lawyer).

## Context
- Company: legal name, place, founded, who runs it (only what the site or a public register says).
- What the site is: shop / booking / info; what it sells; physical locations; separate sites.
- Platform: <name, how identified (footer, HTML, checkout)>. Platform-level fixes → ask <provider>.
- Catalogue: <N products in sitemap/API (N available online), N categories, N other pages>.

## Grades (Excellent / Good / Needs work / Poor)
- <Area 1, e.g. Sales and purchase path>: <grade> (<one-line reason if not obvious>)
- <Area 2 … 5, same order as the report sections and audit.json sections.grade_order>

## What already works (keep)
- W1 <what works, with numbers and where>. [<screenshot>]
- W2 …

## Sales and purchase path
- S1 <what I saw, exact numbers, desktop vs mobile>. [<d-01-…>, <m-01-…>]
  Fix: <concrete change>. Effort: <15 min | 1–2 h | half a day | platform request>.
- S2 …

## Design (audit only)
- D1 …

## Search visibility — technical and on-page
- H1 <keyword claims: "not in Google's top 10" only for keywords checked in Google on the audit date; volumes per month>.
- H… Keyword tool data gaps: a missing position ≠ not ranking; Search Console is the source of truth.

## Speed (lab measurement)
- T1 <PageSpeed field data if available; otherwise our perf.py lab test: profile, FCP range, LCP range, CLS, TTFB, JS size>.
  Say which one it is. Google's "good" LCP limit is 2.5 s, "poor" above 4 s.
  Fix: <…>. Owner: <…>.

## Trust and consumer law  (e-commerce only; each point with a primary source URL read on the audit date)
- L1 Order button wording vs. obligation to pay (Directive 2011/83/EU Art. 8(2), CJEU C-249/21). Source: <url>
- L2 Withdrawal-right exceptions in the terms vs. Directive 2011/83/EU Art. 16. Source: <url>
- L3 Withdrawal function label and findability (Art. 11a, applies from 19.6.2026). Source: <url>
- L4 Product information accuracy (claims vs. ingredients, facts table).
Not legal advice; recommend a lawyer check.

## Top 5 if you do only five things (ranked by money now + risk)
1. … (<finding ids>)
Quick 5-minute fixes on top: …

## Method
- Desktop 1440×900 and mobile 375×812 in a real browser; purchase path home → category → product → cart → checkout up to the order button. No order placed, no personal data entered; test item removed from cart.
- Site's own public API read for all <N> products and <N> categories (titles, descriptions, reviews).
- What crawlers receive: tested with Googlebot, Bingbot, GPTBot, OAI-SearchBot, ChatGPT-User, PerplexityBot, ClaudeBot, Facebook and WhatsApp user agents.
- Speed: <PageSpeed Insights | Playwright + Google Chrome, throttled mobile profile (see T1)>.
- Keywords: <keyword tool>, <country>, <date> (files in data/keywords/). <N> Google spot checks <date> (data/google-checks.json).
- Consumer law: <the sources>, read <date>. Not legal advice.

## What works, per section (for the "What already works" box at the end of each section)
- <Area 1>: W…, W…
- <Area 2 … 5>: …

## Report structure
First the full picture per area: what is wrong, how to fix it, what works. Only after all areas: "what to fix first" (top 5 + 5-minute fixes), then the full fix list, then the keyword appendix.
