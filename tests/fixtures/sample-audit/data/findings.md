# harborpine.example audit — verified findings (source of truth for the report)

INVENTED TEST DATA. Harbor & Pine, harborpine.example and every competitor domain are made up; the "site" is the two
local pages in tests/fixtures/site/. Nothing here describes a real company.

Audit date: 2026-10-29. Auditor: Alex Sample. Scope: sales/purchase path, design (audit only), search (technical + on-page), plus keyword research from an invented keyword tool (2026-10-29).
Every finding below was checked on the test site. Screenshot files are in `media/shots/`.
Owner = who does the fix (Harbor & Pine | ShopBuilder, the platform provider | lawyer).

## Context
- Company: Harbor & Pine, a small tea shop that sells loose leaf tea and gift boxes online, in the EU.
- What the site is: a web shop with 3 teas on the home page (Sea Fog Green 12.90 €, Harbor Black 9.50 €, Lighthouse Chai 11.00 €).
- Platform: ShopBuilder (named in the page footer of the live shop). Platform-level fixes → ask ShopBuilder.
- Catalogue: 3 products, 1 category, 1 checkout page.

## Grades (Excellent / Good / Needs work / Poor)
- Sales and purchase path: Needs work (a fee appears only at checkout)
- Design: Good
- Search visibility: Needs work
- Speed: Poor (main content after 4.4–5.1 s on a phone)
- Trust and consumer law: Needs work

## What already works (keep)
- W1 The home page says what the shop sells in one line ("Small-batch tea from the coast") and shows prices on every product card. [d-01-home.jpg]
- W2 Free shipping over 40 € is stated in the first screen of the home page. [d-01-home.jpg]
- W3 The checkout lists each line, shipping (6.90 €) and the total on one screen. [d-02-checkout.jpg]
- W4 The brand colour (#1F5C4A) is used the same way on every page: header and main button.
- W5 The site ranks 3rd for "pine needle tea" (320 searches a month).

## Sales and purchase path
- S1 A small-order fee of 3.00 € for orders under 15 € is first mentioned at checkout, under the total; the cart link and product cards do not mention it. [m-02-checkout.jpg, d-02-checkout.jpg]
  Fix: show the fee and its 15 € limit on product pages and in the cart. Effort: 1–2 h. Owner: Harbor & Pine + ShopBuilder.
- S2 The checkout total (19.80 €) does not include the 3.00 € small-order fee, although the order (12.90 €) is under 15 €.
  Fix: add the fee to the total, or remove the fee text. Effort: platform request. Owner: ShopBuilder.
- S3 There is one product card per tea and no gift section on the home page, although "tea gift box" is the shop's best P1 search (position 7 in Google, 880 searches a month).
  Fix: add a gift box section to the home page that links to /gifts/. Effort: half a day. Owner: Harbor & Pine.

## Design (audit only)
- D1 On a 375 px phone the menu is hidden and there is no menu button, so the cart link cannot be reached from the home page. [m-01-home.jpg]
  Fix: add a menu button that opens the same links. Effort: 1–2 h. Owner: ShopBuilder.
- D2 The product images are flat colour placeholders, not photos of the tea.
  Fix: add one real photo per product. Effort: half a day. Owner: Harbor & Pine.

## Search visibility — technical and on-page
- H1 "green tea online" (1,300 searches a month) is not in Google's top 10 (checked in Google 2026-10-29); leafandcup.example is first.
  Fix: give the green tea page a title and text that use the words people search for. Effort: 1–2 h. Owner: Harbor & Pine.
- H2 "chai tea" (1,900 searches a month) is at position 22 in the keyword tool; spicebox.example is at position 3.
  Fix: write a chai page with brewing steps and the spices named. Effort: half a day. Owner: Harbor & Pine.

## Speed (lab measurement)
- T1 Our own lab test (perf.py, Lighthouse mobile profile, 3 runs): first content 2.1–2.6 s, main content (LCP) 4.4–5.1 s, 1.8 MB of JavaScript. Not Google field data; Search Console Core Web Vitals has the real-user numbers. Google's "good" LCP limit is 2.5 s, "poor" above 4 s.
  Fix: load the review widget script only on product pages. Effort: platform request. Owner: ShopBuilder.

## Trust and consumer law (each point with a primary source URL read on the audit date)
- L1 The final button says "Send order". Directive 2011/83/EU Art. 8(2) asks for words that show the order creates an obligation to pay, and the EU Court of Justice (C-249/21, 7.4.2022) said only the words on the button count. Source: https://eur-lex.europa.eu/eli/dir/2011/83/oj (read 2026-10-29).
  Fix: change the button to "Order with obligation to pay" or "Buy now". Effort: 15 min. Owner: Harbor & Pine + ShopBuilder.
- L2 The cookie banner says "By using this site you accept all cookies" and has no button to decline. [d-01-home.jpg] Source: https://eur-lex.europa.eu/eli/dir/2002/58/oj (read 2026-10-29).
  Fix: add "Accept" and "Decline" buttons of the same size. Effort: 1–2 h. Owner: ShopBuilder.
Not legal advice; recommend a lawyer check.

## Top 5 if you do only five things (ranked by money now + risk)
1. Change the order button text (L1).
2. Show the small-order fee before checkout and in the total (S1, S2).
3. Add a menu button on phones (D1).
4. Add the gift box section before the gift season (S3).
5. Make the main content load faster on phones (T1).
Quick 5-minute fixes on top: change "Send order" to "Buy now" (L1).

## Method
- Desktop 1440×900 and mobile 375×812 in a real browser; purchase path home → checkout up to the order button. No order placed, no personal data entered.
- Speed: Playwright + Google Chrome, throttled mobile profile (see T1).
- Keywords: invented keyword tool, 2026-10-29 (files in data/keywords/); KD is the tool's keyword difficulty score from 0 to 100. 2 Google spot checks 2026-10-29 (data/google-checks.json).
- Consumer law: Directive 2011/83/EU and Directive 2002/58/EC on EUR-Lex, read 2026-10-29. Not legal advice.

## What works, per section (for the "What already works" box at the end of each section)
- Sales and purchase path: W1, W2, W3
- Design: W4
- Search visibility: W5
- Speed: (none)
- Trust and consumer law: W3

## Report structure
First the full picture per area: what is wrong, how to fix it, what works. Only after all areas: "what to fix first" (top 5 + 5-minute fixes), then the full fix list, then the keyword appendix.
