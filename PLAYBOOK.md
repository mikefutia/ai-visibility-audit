# Setup — get your Apify token (one time, ~2 min)

This skill queries the AI engines through Apify. You need one thing: an Apify API token.

1. Sign in (or sign up free) at **[apify.com](https://apify.com)**.
2. Go to **Settings → Integrations** ([console.apify.com/settings/integrations](https://console.apify.com/settings/integrations)).
3. Copy your **Personal API token**.

## Save it
Create a file named **`.env`** with this line:
```
APIFY_TOKEN=your_token_here
```
Put `.env` in **this skill's folder** (set once) or in the **folder you're working in**. Don't paste the token into chat.

## Then just say
> **run the ai visibility audit**

It asks for your brand + website and your category, then checks whether AI recommends you.

## Cost & notes
- Uses `apify/google-search-scraper` with the AI add-ons. ~12 queries across 3 AI engines ≈ **$0.30–0.60** per audit.
- **Runs take a few minutes** — the AI engines (ChatGPT/Perplexity) are slow to answer. That's normal.
- Requires **Python 3** (preinstalled on macOS).
- Want it faster/cheaper? Run `--engines aioverview,chatgpt` (drops Perplexity).
