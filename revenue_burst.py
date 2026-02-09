#!/usr/bin/env python3
"""
🚀 Revenue Content Burst Generator
Generates X/Twitter content for ALL landing pages.
Uses Kimi AI to create viral threads promoting each product.
"""

import asyncio
import json
import os
import aiohttp
from datetime import datetime

KIMI_API_KEY = os.getenv("MOONSHOT_API_KEY", "sk-e57Q5aDfcpXpHkYfgeWCU3xjuqf2ZPoYxhuRH0kEZXGBeoMF")
OUTPUT_DIR = "x_content"
os.makedirs(OUTPUT_DIR, exist_ok=True)

PRODUCTS = [
    {
        "name": "BMA Consulting",
        "url": "https://mauricepfeifer-ctrl.github.io/photonic-schrodinger/consulting/",
        "hook": "BMA-Planung ohne Normen-Check = russisches Roulette mit deinem Budget.",
        "topic": "Brandmeldeanlagen, DIN 14675, Normprüfung, Bauabnahme",
        "price": "ab €197"
    },
    {
        "name": "AI Consulting",
        "url": "https://mauricepfeifer-ctrl.github.io/photonic-schrodinger/ai-consulting/",
        "hook": "Dein Unternehmen bezahlt 3 Mitarbeiter für Aufgaben, die eine KI in 5 Minuten erledigt.",
        "topic": "KI-Automatisierung, Geschäftsprozesse, AI Agents, Produktivität",
        "price": "ab €297"
    },
    {
        "name": "File Cleaner Pro",
        "url": "https://mauricepfeifer-ctrl.github.io/photonic-schrodinger/file-cleaner/",
        "hook": "Du hast 10.000+ Dateien und findest nichts? Meine KI räumt das in 30 Minuten auf.",
        "topic": "Datei-Organisation, Digitales Aufräumen, KI-Sortierung, Produktivität",
        "price": "ab €47"
    }
]

CONTENT_MODES = [
    {
        "mode": "viral_thread",
        "prompt": """Write a 5-tweet viral thread in GERMAN. Rules:
- First tweet is a HOOK that stops scrolling. Bold claim. No hashtags.
- Use short, punchy sentences. Max 280 chars per tweet.
- Include specific numbers and pain points.
- Last tweet is a CTA with the link.
- Output ONLY valid JSON: {{"tweets": ["tweet1", "tweet2", ...]}}"""
    },
    {
        "mode": "single_banger",
        "prompt": """Write ONE single high-engagement tweet in GERMAN. Rules:
- Max 280 characters
- Controversial or bold statement
- Include a CTA at the end with the link
- No hashtags
- Output ONLY valid JSON: {{"tweets": ["the single tweet"]}}"""
    },
    {
        "mode": "pain_agitation",
        "prompt": """Write a 3-tweet thread in GERMAN using Pain-Agitation-Solution framework. Rules:
- Tweet 1: Describe a specific PAIN the target audience feels
- Tweet 2: AGITATE — make it worse, show the cost of inaction
- Tweet 3: SOLUTION with CTA and link
- Max 280 chars per tweet. No hashtags.
- Output ONLY valid JSON: {{"tweets": ["pain", "agitation", "solution"]}}"""
    }
]


async def generate_content(session, product, mode_config):
    """Generate one piece of content via Kimi."""
    prompt = f"""
{mode_config['prompt']}

PRODUCT: {product['name']}
PRICE: {product['price']}
LINK: {product['url']}
HOOK INSPIRATION: {product['hook']}
TOPIC KEYWORDS: {product['topic']}
"""
    try:
        async with session.post(
            "https://api.moonshot.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {KIMI_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "moonshot-v1-8k",
                "messages": [
                    {"role": "system", "content": "Du bist ein Top-Tier X/Twitter Ghostwriter. Du schreibst auf Deutsch. Dein Content geht viral. Du verstehst Engagement-Algorithmen. Antworte NUR mit validem JSON."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.85
            }
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                content = data["choices"][0]["message"]["content"]
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                return json.loads(content.strip())
            else:
                print(f"  ❌ Kimi Error {resp.status}: {await resp.text()}")
                return None
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None


async def main():
    print("🚀 REVENUE CONTENT BURST — Generating for all products...")
    print("=" * 60)

    all_content = []

    async with aiohttp.ClientSession() as session:
        for product in PRODUCTS:
            print(f"\n📦 {product['name']} ({product['price']})")
            print(f"   🔗 {product['url']}")

            for mode_config in CONTENT_MODES:
                print(f"   🎯 Mode: {mode_config['mode']}...", end=" ")
                result = await generate_content(session, product, mode_config)

                if result:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    slug = product["name"].lower().replace(" ", "_")
                    filename = f"{OUTPUT_DIR}/{timestamp}_{slug}_{mode_config['mode']}.json"

                    output = {
                        "product": product["name"],
                        "url": product["url"],
                        "mode": mode_config["mode"],
                        "tweets": result.get("tweets", []),
                        "generated_at": timestamp
                    }

                    with open(filename, "w") as f:
                        json.dump(output, f, indent=2, ensure_ascii=False)

                    all_content.append(output)
                    tweet_count = len(result.get("tweets", []))
                    print(f"✅ {tweet_count} tweets → {filename}")
                else:
                    print("❌ Failed")

                await asyncio.sleep(1)  # Rate limit

    print(f"\n{'=' * 60}")
    print(f"🎯 TOTAL: {len(all_content)} content pieces generated")
    print(f"📁 Output: {OUTPUT_DIR}/")

    # Summary
    for item in all_content:
        print(f"\n--- {item['product']} / {item['mode']} ---")
        for i, tweet in enumerate(item.get("tweets", []), 1):
            preview = tweet[:100] + "..." if len(tweet) > 100 else tweet
            print(f"  Tweet {i}: {preview}")


if __name__ == "__main__":
    asyncio.run(main())
