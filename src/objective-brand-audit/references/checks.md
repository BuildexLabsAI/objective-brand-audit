# Audit checks — exact methods

Run these during phase 4 (Audit). Record every result in `data/findings.md` with the date.

## 1. What crawlers, AI bots and link previews receive
Sends each bot's published user agent to the homepage and compares status, size and whether real page text
is present. This is the standard "fetch as bot" check: a handful of requests, read-only. As `TEXT`, pick a short run
of plain words that is visible on the rendered homepage and has no markup or special characters inside it in the
page source (no `&`, quotes or inline tags such as `<em>`), so the raw HTML holds it letter for letter.

```bash
U=https://www.<domain>/ ; TEXT="<sentence visible on the homepage>"; D=$(mktemp -d)
for ua in "Googlebot/2.1 (+http://www.google.com/bot.html)" \
  "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)" \
  "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; GPTBot/1.2; +https://openai.com/gptbot" \
  "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; OAI-SearchBot/1.0; +https://openai.com/searchbot" \
  "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; ChatGPT-User/1.0; +https://openai.com/bot" \
  "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; PerplexityBot/1.0; +https://perplexity.ai/perplexitybot)" \
  "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; ClaudeBot/1.0; +claudebot@anthropic.com)" \
  "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)" "WhatsApp/2.23.20.0"; do
  r=$(curl -sL -A "$ua" -o "$D/x.html" -w "%{http_code} %{size_download}" "$U"); c=$(grep -cF -- "$TEXT" "$D/x.html")
  printf "%-22s %s content=%s\n" "$(echo "$ua" | grep -oE 'Googlebot|bingbot|GPTBot|OAI-SearchBot|ChatGPT-User|PerplexityBot|ClaudeBot|facebookexternalhit|WhatsApp' | head -1)" "$r" "$c"
done; rm -rf "$D"
```
Also check: a made-up URL returns a real 404 (`curl -s -o /dev/null -w "%{http_code}" "$U/no-such-page-123/"`),
`robots.txt` (Crawl-delay, Sitemap line), the sitemap (count `<loc>`), and the raw HTML without JavaScript
(title, meta description, H1s, og:image, visible text length). An empty shell for WhatsApp = empty link previews.

## 2. Catalogue scan via the site's public API (e-commerce)
Find the API the shop itself calls (in the browser: watch the network requests while a category page loads). Read it
**from inside the browser page** with `fetch()`, so the request is the shop's own page talking to its own
API. Never call it with curl and a made-up browser user agent.

```js
(async () => { const r = await fetch('/<api path>?resultsPerPage=300', {credentials: 'include'});
  const d = await r.json(); window.__cat = d; return {status: r.status, keys: Object.keys(d).slice(0, 20)}; })()
```
Count: products, available online, categories; reviews per product; products with under 30 words of description;
missing or over-long SEO descriptions; duplicates; product codes shown as names. Store counts in findings.md
(not the raw dump).

## 3. Consumer law (EU, e-commerce) — primary sources, read on the audit day
Runs for a shop that sells to consumers in the EU. Each L-finding names its source URL and the date it was read.
Read the source on the audit day and check it still says what the table says; also read the national consumer
authority's guidance for the country the shop sells to. The report says it is not legal advice and recommends a
lawyer check. Never write "breaking the law"; write that the current wording "does not meet" or "conflicts with"
what the source says. Outside the EU: use that country's law and authority, or leave the legal part out and say so.

| Check | What to look at | Source (verify it still says this) |
|---|---|---|
| Order button | Does the final button say that ordering creates an obligation to pay ("Order with obligation to pay", "Buy now")? "Send order" does not. | Directive 2011/83/EU Art. 8(2): https://eur-lex.europa.eu/eli/dir/2011/83/oj ; CJEU C-249/21 Fuhrmann-2, judgment 7.4.2022 (only the words on the button count): https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:62021CJ0249 |
| Withdrawal exceptions | Terms that exclude whole product groups (e.g. "all food") when the products do not spoil quickly | Directive 2011/83/EU Art. 16 (the closed list of exceptions) |
| Withdrawal function | A clearly labelled, easy-to-find function to withdraw from the contract, with a confirmation step (applies from 19.6.2026). Label like "Withdraw from contract here", not "Returns form". | Directive (EU) 2023/2673, which adds Art. 11a to Directive 2011/83/EU: https://eur-lex.europa.eu/eli/dir/2023/2673/oj |
| Product claims | Name/claim vs. ingredients and the facts table on the same page ("100 %" vs. 86 %) | Directive 2005/29/EC (misleading actions): https://eur-lex.europa.eu/eli/dir/2005/29/oj ; the product page itself (screenshot) |
| Costs before checkout | Shipping, small-order surcharges and thresholds shown before the buyer commits | Directive 2011/83/EU Art. 6(1)(e); the cart and checkout (screenshot) |

## 4. Google spot checks (browser)
"No data" in a keyword tool is not proof of not ranking. Before the report says "not in Google's top 10", check that
keyword in Google and record it. Use a real browser tool (not curl):

```
navigate: https://www.google.com/search?q=<keyword>&hl=<language>&gl=<country>&num=20
javascript_exec:
({consent: /Before you continue/i.test(document.body.innerText.slice(0, 500)),
  captcha: /unusual traffic|recaptcha/i.test(document.body.innerHTML.slice(0, 20000)),
  results: [...document.querySelectorAll('#search a:has(h3)')]
    .map(a => { try { return new URL(a.href).hostname.replace('www.', '') } catch (e) { return a.href } }).slice(0, 20)})
```
Consent page (with another `hl`, match that language's consent heading too): decline non-essential cookies. CAPTCHA: stop the checks and tell the user; never solve it.
Record in `data/google-checks.json`:
```json
{"checked": "<YYYY-MM-DD>", "method": "google.com, hl=<language>, gl=<country>, organic results, top 10",
 "results": [{"q": "loose leaf tea", "position": 3, "url": "/tea/…/", "tool": 3, "top": ["competitor.example", "…"]}]}
```
`position` is null when the site is not in the top 10 (the report then shows "not in top 10" for that keyword).

## 5. Speed
1. Google PageSpeed Insights API first (lab + real-user field data):
   `curl -s "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=<url-encoded>&strategy=mobile&category=performance&locale=en"`
2. Quota error → `python3 <kit>/perf.py --audit <audit>` (own lab test, Lighthouse mobile profile). The report and
   findings.md must say it is our lab test, not Google field data, and point to Search Console Core Web Vitals.

## 6. Brand tokens for audit.json
In the browser on the site's homepage, read computed styles (button background, body text colour,
heading font, body font, borders, panel backgrounds):
```js
const s = el => el && getComputedStyle(el); const pick = q => s(document.querySelector(q));
({body: [pick('body').color, pick('body').fontFamily, pick('body').fontSize], h1: pick('h1')?.fontFamily,
  button: pick('button, .btn, [class*=button]')?.backgroundColor, header: pick('header')?.backgroundColor})
```
Convert to 6-digit hex. Fonts: `python3 <kit>/fetch_fonts.py --audit <audit> "Family:400,700"` (Google Fonts);
a commercial font with no Google version → the closest Google font, noted in findings.md Method.
