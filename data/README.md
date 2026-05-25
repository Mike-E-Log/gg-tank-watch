# data/

Reusable seed data for the dashboard. Files here are checked into the repo (unlike `status.json` which is a runtime artifact and gitignored).

## news_seed.json

A curated set of news entries (videos + articles) covering the GG MMA tank incident, selected for:

- **Recency** — most entries published within 72 hours of curation
- **Coverage depth** — outlets with reporters at scene + ongoing live blogs
- **Format mix** — YouTube videos (with auto-derived thumbnails), TV-news website articles (some with thumbnails), live-blog running pages

To pipe into the dashboard writer:

```powershell
type data\news_seed.json | python scripts\update_status.py
```

(On macOS/Linux: `cat data/news_seed.json | python scripts/update_status.py`)

The writer treats `videos` as a list of mixed video / article entries:

| Field | Required | Notes |
|---|---|---|
| `outlet` | yes | Display name, e.g., "ABC7 Los Angeles" |
| `title` | yes | The headline |
| `url` | yes | Link the card opens on click |
| `published_iso` | recommended | Used for sort order (newest first) |
| `youtube_id` | optional | If present, writer auto-derives `thumbnail_url` from `https://img.youtube.com/vi/{id}/hqdefault.jpg` |
| `thumbnail_url` | optional | Direct image URL (overrides YouTube auto-derive) |
| `is_video` | optional | Set `true` for non-YouTube videos to get the play-button overlay |

If `youtube_id` is absent and `is_video` is unset, the dashboard renders the entry as an article (📰 icon, no play overlay).

If no `thumbnail_url` is provided, the dashboard shows a typed placeholder (play-icon for videos, document-icon for articles) plus the outlet name as a small bottom-left chip.

## Refresh cadence

This seed is hand-curated. The live `/loop` job (every 30 min) is where fresh content lands automatically — see `scripts/update_status.py`. Use this seed only when:

- Bootstrapping a fresh `git clone` of the dashboard
- Restoring after wiping `status.json`
- Demonstrating the dashboard for a portfolio review
