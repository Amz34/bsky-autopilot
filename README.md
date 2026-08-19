# Bluesky Post Tool

Bluesky pe post karne ka local tool — free, X (Twitter) ka open alternative.
Text manual likho ya AI (DeepSeek) se generate karo. Images supported.

## Setup (ek baar, 5 minute)

1. **Bluesky account banao** → https://bsky.app (free, email se)
2. **App Password banao** → https://bsky.app/settings/app-password → **Add App Password**
   - Name: `hermes-bot` (ya kuch bhi)
   - Jo password mile (format: `xxxx-xxxx-xxxx-xxxx`) use karo — **main password kabhi nahi**
3. `.env` file banao (copy karo `.env.example` ko) aur ye daalo:
   ```
   BSKY_HANDLE=aapkanaam.bsky.social
   BSKY_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
   DEEPSEEK_API_KEY=aapki deepseek key (AI mode ke liye)
   ```

## Use

```bash
# Manual post
python tweet.py "Hello Bluesky!"

# Post with image
python tweet.py "Hello!" --image photo.jpg

# AI post (topic optional)
python tweet.py --ai --topic "facility management KSA"

# Link post — URLs automatically clickable + card ban jaati hai
python tweet.py "Mera naya tool: https://github.com/Amz34/linkedin-autopilot"
```

## Files
| File | Kaam |
|---|---|
| `tweet.py` | Post karna (manual + AI + image) |
| `.env` | Credentials (KABHI share mat karo) |

## Security
- `.env` **kabhi GitHub/chat mein mat bhejo**
- App Password kisi se share mat karo — koi issue ho toh bsky settings mein delete karke naya bana lo
