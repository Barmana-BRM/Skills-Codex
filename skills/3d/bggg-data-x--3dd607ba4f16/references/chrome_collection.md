# Chrome collection loop

Read this file when executing an X collection run.

## 1. Browser setup

Use the Chrome plugin's own control skill and browser-client runtime. Select `extension` because the user explicitly wants the logged-in Chrome session. Read the complete browser documentation before the first interaction and reuse the same browser binding.

Open one task tab, navigate with `tab.goto(task.search_url)`, wait for the search timeline, and confirm the `Latest` or `Top` tab matches the plan. A visible profile link and search timeline indicate that the session is signed in. Do not inspect cookies or storage.

## 2. Validate selectors

Before a batch, evaluate this read-only check:

```javascript
await tab.playwright.evaluate(() => {
  const cards = [...document.querySelectorAll('article[data-testid="tweet"]')];
  const first = cards[0];
  return {
    cards: cards.length,
    firstHasText: Boolean(first?.querySelector('[data-testid="tweetText"]')),
    firstHasUser: Boolean(first?.querySelector('[data-testid="User-Name"]')),
    firstStatusHref:
      first?.querySelector('time[datetime]')?.closest('a[href*="/status/"]')
        ?.getAttribute('href') || null,
    firstDatetime:
      first?.querySelector('time[datetime]')?.getAttribute('datetime') || null,
    firstEngagement:
      first?.querySelector('[role="group"][aria-label]')
        ?.getAttribute('aria-label') || null,
  };
});
```

If the visible timeline has posts but `cards` or `firstHasText` is zero, inspect the current rendered DOM and update the contract before collecting.

## 3. Extract the current viewport

Run this in page context. Add `query`, `lang_hint`, and the task collection timestamp in the Node-side caller so every observation remains attributable.

```javascript
await tab.playwright.evaluate(() => {
  return [...document.querySelectorAll('article[data-testid="tweet"]')]
    .map((card) => {
      const textNode = card.querySelector('[data-testid="tweetText"]');
      const userNode = card.querySelector('[data-testid="User-Name"]');
      const timeNode = card.querySelector('time[datetime]');
      const statusAnchor =
        timeNode?.closest('a[href*="/status/"]') ||
        [...card.querySelectorAll('a[href*="/status/"]')].find((anchor) =>
          /\/status\/\d+$/.test(new URL(anchor.href).pathname)
        );
      const path = statusAnchor?.getAttribute('href') || '';
      const idMatch = path.match(/\/status\/(\d+)/);
      const handle =
        [...(userNode?.querySelectorAll('a') || [])]
          .map((anchor) => (anchor.textContent || '').trim())
          .find((value) => value.startsWith('@')) || null;
      const engagementNode = card.querySelector('[role="group"][aria-label]');
      return {
        platform: 'X',
        native_id: idMatch?.[1] || null,
        url: statusAnchor?.href || null,
        date: timeNode?.getAttribute('datetime') || null,
        text_raw: textNode?.innerText || '',
        text_lang_attr: textNode?.getAttribute('lang') || null,
        author_handle: handle,
        author_display_raw: userNode?.innerText || '',
        engagement_raw: engagementNode?.getAttribute('aria-label') || '',
        card_text_raw: card.innerText || '',
        collected_at: new Date().toISOString(),
      };
    })
    .filter((row) => row.native_id && row.text_raw);
});
```

The time link is preferred because generic status selectors may also match photo or analytics links.

## 4. Accumulate and scroll

Use a Node-side `Map` keyed by `native_id`.

```javascript
const byId = new Map();
let stale = 0;
let scrolls = 0;

while (byId.size < task.max_rows && stale < 6 && scrolls < 180) {
  const batch = await extractCurrentViewport();
  const before = byId.size;
  for (const row of batch) byId.set(row.native_id, row);
  stale = byId.size === before ? stale + 1 : 0;
  scrolls += 1;
  await tab.playwright.evaluate(() => window.scrollBy(0, 1500));
  await tab.playwright.waitForTimeout(1000);
}
```

Vary the wait within 850–1,500 ms when running a long series. Keep queries sequential in one tab.

## 5. Save immediately

Create one source package per query:

```json
{
  "method": "chrome_dom",
  "collected_at": "2026-07-26T00:00:00Z",
  "query": "sample-ingredient lang:en",
  "lang": "EN",
  "round": 1,
  "sort": "latest",
  "search_url": "https://x.com/search?...",
  "max_rows": 250,
  "stop_reason": "stale_scroll_limit",
  "scrolls": 42,
  "rows": []
}
```

Use the Node filesystem API available to the execution environment to write the JSON package and update the request-plan task status after every query. Never overwrite a successful package with an empty retry; use an attempt suffix.

## 6. Failure handling

- Sign-in wall: ask the user to sign in in Chrome.
- Challenge or suspicious-login page: stop; never automate the challenge.
- Blank timeline: retry the same URL once after a conservative wait, then log failure.
- Selector drift: save a DOM snapshot for diagnosis, but do not save credentials or private messages.
- Rate limiting: stop the batch, retain completed packages, and report the last successful task.
- Task completion: finalize every tab opened by the task.

