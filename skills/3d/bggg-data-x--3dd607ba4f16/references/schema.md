# Data contracts

## Query plan

Each `tasks[]` entry contains:

```json
{
  "task_id": "001",
  "query": "sample-ingredient lang:en",
  "lang": "EN",
  "round": 1,
  "max_rows": 250,
  "sort": "latest",
  "search_url": "https://x.com/search?q=...",
  "source_file": "001_EN.json",
  "status": "pending"
}
```

## Per-query source package

Required package fields:

- `method`: `chrome_dom`
- `collected_at`: ISO timestamp
- `query`: exact X query
- `lang`: research language hint
- `round`: keyword-iteration round
- `sort`: `latest` or `top`
- `search_url`: exact URL used
- `max_rows`: requested cap
- `stop_reason`: `max_rows`, `stale_scroll_limit`, `hard_scroll_limit`, or failure label
- `scrolls`: completed scroll count
- `rows`: exact visible-DOM observations

Required row fields:

- `native_id`: numeric Tweet ID
- `url`: canonical `https://x.com/{handle}/status/{id}` URL
- `date`: `time[datetime]`
- `text_raw`: exact rendered post text
- `text_lang_attr`: DOM language attribute when present
- `author_handle`
- `author_display_raw`
- `engagement_raw`: accessible engagement label
- `card_text_raw`: complete rendered card text for auditing
- `collected_at`

## Normalized JSONL

Each line contains:

```json
{
  "platform": "X",
  "lang": "EN",
  "source_id": "24-character SHA-256 prefix",
  "native_id": "2080094527549817095",
  "date": "2026-07-23T00:55:56.000Z",
  "text_raw": "Exact original text",
  "engagement": {
    "raw": "2 replies, 2 likes, 41 views",
    "replies": 2,
    "reposts": 0,
    "likes": 2,
    "bookmarks": 0,
    "views": 41
  },
  "context": {
    "content_type": "post",
    "author_handle": "@example",
    "author_display_raw": "display block",
    "url": "https://x.com/example/status/123",
    "queries": ["query one", "query two"],
    "query_langs": ["EN"],
    "text_lang_attr": "en",
    "source_route": "chrome_dom_visible_ui",
    "card_text_raw": "full card text",
    "collected_at": "ISO timestamp",
    "source_files": ["work/x/source_json/001_EN.json"]
  },
  "keyword_hit": ["sample-ingredient"],
  "round": 1
}
```

## Audit expectations

The normalization summary must report:

- source files and invalid source files;
- total observations and unique rows;
- duplicate observations;
- missing text, identity, URL, and date;
- invalid Tweet IDs and dates;
- query and language counts;
- earliest and latest dates.

