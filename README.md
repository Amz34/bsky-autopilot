# 🦋 Bluesky Autopilot

**Your Bluesky feed on autopilot — AI-crafted posts, published from your terminal.**
Local-first, free, no SaaS fees, no lock-in.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue) ![License](https://img.shields.io/badge/License-MIT-green) ![Status](https://img.shields.io/badge/Status-Production--tested-success)

## Why

Posting consistently is the #1 growth lever on any platform — and the #1 thing people skip.
Bluesky Autopilot removes the friction: write a prompt, get an on-brand post, publish it.
No dashboard to log into. No subscription. Just a CLI and your feed growing.

## Features

- ✍️ **AI mode** — DeepSeek writes the post for you (`--ai --topic "KSA facility management"`)
- 🖼️ **Image support** — attach any PNG/JPG/WebP/GIF
- 🔗 **Link cards** — URLs auto-detect into rich link cards
- 🔐 **App-password auth** — your main password never touches disk
- 🆓 **$0/month** — no SaaS, no API fees for posting (Bluesky API is free)

## Quickstart (5 minutes)

### 1. Get a Bluesky app password

1. [bsky.app/settings/app-password](https://bsky.app/settings/app-password) → **Add App Password**
2. Name it `hermes-bot` — you get a `xxxx-xxxx-xxxx-xxxx` key
3. ⚠️ Never use your main password

### 2. Configure

```bash
cp .env.example .env
```

```ini
BSKY_HANDLE=yourname.bsky.social
BSKY_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
DEEPSEEK_API_KEY=sk-...        # for AI mode
DEEPSEEK_MODEL=deepseek-v4-flash
```

### 3. Post

```bash
# Manual post
python tweet.py "Hello Bluesky!"

# Post with image
python tweet.py "Hello!" --image photo.jpg

# AI-generated post
python tweet.py --ai --topic "facility management KSA"

# Share a link (auto link-card)
python tweet.py "My new tool: https://github.com/Amz34/linkedin-autopilot"
```

## Files

| File | Purpose |
|---|---|
| `tweet.py` | Manual + AI + image posting |
| `.env` | Credentials — **never commit or share** |

## Security

- `.env` must never be committed or pasted into chat
- Something looks off? Delete the app password in Bluesky settings and mint a new one — instant rotation, zero code changes

## License

MIT — free to use, fork, and ship.
