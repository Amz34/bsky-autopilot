#!/usr/bin/env python3
"""
Bluesky Post Tool — post text/images with optional AI (DeepSeek) content.

Usage:
  python tweet.py "Hello Bluesky!"
  python tweet.py "Hello!" --image photo.jpg
  python tweet.py --ai [--topic "facility management"]
"""
import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
import urllib.request
import urllib.error

BASE = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE, ".env")
API = "https://bsky.social"

AI_SYSTEM = """You are a Bluesky content writer for Aamir (PME/facility management professional + self-taught developer). Write punchy, engaging Bluesky posts. Rules:
- Hook in the first line, value in the middle, ALWAYS end with a clear CTA inviting likes, replies, and follows
- MAX 280 characters (Bluesky limit is 300), short lines
- 1-2 emojis max, hashtags max 1-2 (Bluesky pe hashtags kam chalti hain)
- NEVER use em dashes (—) or en dashes (–); use commas, colons, or periods instead
- Tone: credible, helpful, developer/industry-insight
- No clickbait, no fake stats"""


def load_env():
    env = {}
    if os.path.exists(ENV_PATH):
        for line in open(ENV_PATH, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def api(method, path, token=None, body=None, raw=None, content_type="application/json"):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if raw is not None:
        data = raw
        headers["Content-Type"] = content_type
    elif body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    else:
        data = None
    req = urllib.request.Request(API + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            r = resp.read()
            return resp.status, json.loads(r) if r else {}
    except urllib.error.HTTPError as e:
        r = e.read().decode("utf-8", "replace")
        try:
            return e.code, json.loads(r)
        except Exception:
            return e.code, {"message": r[:300]}


def create_session(env):
    status, data = api("POST", "/xrpc/com.atproto.server.createSession",
                       body={"identifier": env["BSKY_HANDLE"], "password": env["BSKY_APP_PASSWORD"]})
    if status != 200:
        print(f"❌ Login fail ({status}): {data.get('message', data)}")
        sys.exit(1)
    return data  # accessJwt, refreshJwt, did, handle


def get_facets(text):
    """Convert URLs to clickable link facets (UTF-8 byte offsets)."""
    facets = []
    for m in re.finditer(r"https?://[^\s]+", text):
        url = m.group(0).rstrip(".,;:!?)]}")
        if not url:
            continue
        start = len(text[:m.start()].encode("utf-8"))
        end = len(text[:m.start() + len(url)].encode("utf-8"))
        facets.append({
            "index": {"byteStart": start, "byteEnd": end},
            "features": [{"$type": "app.bsky.richtext.facet#link", "uri": url}],
        })
    return facets


def upload_image(session, image_path):
    with open(image_path, "rb") as f:
        img = f.read()
    ctype = "image/png" if image_path.lower().endswith(".png") else "image/jpeg"
    status, data = api("POST", "/xrpc/com.atproto.repo.uploadBlob",
                       token=session["accessJwt"], raw=img, content_type=ctype)
    if status != 200:
        print(f"❌ Image upload fail ({status}): {data.get('message', data)}")
        return None
    blob = data.get("blob")
    blob["$type"] = "blob"
    return blob


def generate_post(env, topic):
    key = env.get("DEEPSEEK_API_KEY", "")
    if not key:
        print("❌ .env mein DEEPSEEK_API_KEY nahi hai — AI mode ke liye zaroori.")
        sys.exit(1)
    model = env.get("DEEPSEEK_MODEL", "deepseek-v4-flash")
    prompt = f"Write a Bluesky post about: {topic}" if topic else "Write a Bluesky post about a developer building AI automation tools."
    body = {
        "model": model,
        "messages": [{"role": "system", "content": AI_SYSTEM}, {"role": "user", "content": prompt}],
        "max_tokens": 400,
        "temperature": 0.8,
    }
    req = urllib.request.Request(
        "https://api.deepseek.com/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
    return data["choices"][0]["message"]["content"].strip()


def post(session, text, image_path=None):
    if len(text) > 300:
        print(f"⚠️ Text {len(text)} chars — Bluesky limit 300. Truncate karta hoon.")
        text = text[:297] + "..."
    record = {
        "$type": "app.bsky.feed.post",
        "text": text,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "langs": ["en"],
    }
    facets = get_facets(text)
    if facets:
        record["facets"] = facets

    first_url = None
    if facets:
        first_url = facets[0]["features"][0]["uri"]

    if image_path:
        print(f"🖼️ Image upload ho raha hai ({os.path.basename(image_path)})...")
        blob = upload_image(session, image_path)
        if blob:
            record["embed"] = {
                "$type": "app.bsky.embed.images",
                "images": [{"alt": text[:300], "image": blob}],
            }
        else:
            print("⚠️ Image upload fail — bina image ke text post karta hoon.")
    elif first_url:
        # link card (no thumb — plain card with title/description)
        host = re.sub(r"^https?://(www\.)?", "", first_url).split("/")[0]
        record["embed"] = {
            "$type": "app.bsky.embed.external",
            "external": {
                "uri": first_url,
                "title": host,
                "description": text[:200],
            },
        }

    status, data = api("POST", "/xrpc/com.atproto.repo.createRecord",
                       token=session["accessJwt"],
                       body={"repo": session["did"], "collection": "app.bsky.feed.post", "record": record})
    if status == 200:
        uri = data.get("uri", "")
        rkey = uri.rsplit("/", 1)[-1]
        print(f"✅ Post published!")
        print(f"   Dekho: https://bsky.app/profile/{session['handle']}/post/{rkey}")
        return True
    print(f"❌ Post fail ({status}): {json.dumps(data, ensure_ascii=False)[:400]}")
    return False


def main():
    parser = argparse.ArgumentParser(description="Bluesky post tool")
    parser.add_argument("--ai", action="store_true", help="Generate content with AI (DeepSeek)")
    parser.add_argument("--topic", default="", help="Topic for AI-generated post")
    parser.add_argument("--image", default="", help="Image file path (png/jpg)")
    parser.add_argument("text", nargs="?", default="", help="Manual post text")
    args = parser.parse_args()

    env = load_env()
    if "BSKY_HANDLE" not in env or "BSKY_APP_PASSWORD" not in env:
        print("❌ .env mein BSKY_HANDLE / BSKY_APP_PASSWORD nahi hai.")
        print("   Setup: https://bsky.app/settings/app-password → Add App Password")
        sys.exit(1)

    if args.ai:
        text = generate_post(env, args.topic)
        print("🤖 AI post generated:\n")
        print("---")
        print(text)
        print("---\n")
    else:
        text = args.text.strip()
        if not text:
            print('❌ Manual mode mein text do:  python tweet.py "Hello Bluesky!"')
            sys.exit(1)

    if args.image and not os.path.exists(args.image):
        print(f"❌ Image file nahi mili: {args.image}")
        sys.exit(1)

    print("🔑 Login ho raha hai...")
    session = create_session(env)
    ok = post(session, text, args.image or None)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
