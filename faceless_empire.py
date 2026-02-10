#!/usr/bin/env python3
"""
👑 FACELESS EMPIRE — Premium Multi-Platform Content Machine
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Generates premium faceless content for ALL platforms:
  📺 YouTube (Long-form + Shorts) — Faceless, AI-narrated
  🎵 TikTok — Viral hooks, trending sounds, quick cuts
  📸 Instagram — Reels + Carousels + Stories
  🐦 X/Twitter — Threads + Single Tweets + Engagement

ALL content is:
  ✅ Faceless (no face required)
  ✅ AI-generated scripts
  ✅ Premium quality
  ✅ SEO optimized
  ✅ Cross-platform repurposed
  ✅ Scheduled for optimal times

Usage:
    python faceless_empire.py --generate 10       # Generate 10 content pieces
    python faceless_empire.py --platform tiktok    # TikTok only
    python faceless_empire.py --blitz              # Generate for ALL platforms
    python faceless_empire.py --schedule           # Generate + schedule
    python faceless_empire.py --viral              # Viral-optimized content
"""

import os
import json
import asyncio
import aiohttp
import logging
import argparse
import random
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Configuration
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("FacelessEmpire")

# API Keys
KIMI_API_KEY = os.getenv("MOONSHOT_API_KEY", "")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# Directories
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = BASE_DIR / "content_output"
YOUTUBE_DIR = OUTPUT_DIR / "youtube"
TIKTOK_DIR = OUTPUT_DIR / "tiktok"
INSTAGRAM_DIR = OUTPUT_DIR / "instagram"
TWITTER_DIR = OUTPUT_DIR / "twitter"
SCHEDULE_DIR = OUTPUT_DIR / "schedule"

for d in [OUTPUT_DIR, YOUTUBE_DIR, TIKTOK_DIR, INSTAGRAM_DIR, TWITTER_DIR, SCHEDULE_DIR]:
    d.mkdir(parents=True, exist_ok=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Data Models
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class Platform(Enum):
    YOUTUBE = "youtube"
    YOUTUBE_SHORTS = "youtube_shorts"
    TIKTOK = "tiktok"
    INSTAGRAM_REELS = "instagram_reels"
    INSTAGRAM_CAROUSEL = "instagram_carousel"
    INSTAGRAM_STORY = "instagram_story"
    TWITTER_THREAD = "twitter_thread"
    TWITTER_SINGLE = "twitter_single"
    LINKEDIN = "linkedin"
    BLOG = "blog"

class ContentStyle(Enum):
    VIRAL = "viral"
    EDUCATIONAL = "educational"
    STORYTELLING = "storytelling"
    CONTROVERSIAL = "controversial"
    LISTICLE = "listicle"
    CASE_STUDY = "case_study"
    HOW_TO = "how_to"
    NEWS = "news"

class Niche(Enum):
    AI_AUTOMATION = "ai_automation"
    MONEY_MAKING = "money_making"
    TECH_REVIEWS = "tech_reviews"
    PRODUCTIVITY = "productivity"
    FUTURE_TECH = "future_tech"
    CODING = "coding"
    BUSINESS = "business"
    SIDE_HUSTLE = "side_hustle"

@dataclass
class ContentPiece:
    """A single piece of content for any platform."""
    id: str
    platform: str
    style: str
    niche: str
    title: str
    hook: str                          # First line (attention grabber)
    body: str                          # Main content
    call_to_action: str                # CTA
    hashtags: List[str]
    tags: List[str]                    # SEO tags
    thumbnail_prompt: str              # For AI image generation
    visual_notes: str                  # B-roll / visual instructions
    estimated_duration_sec: int
    optimal_post_time: str
    engagement_prediction: float       # 1-10 score
    revenue_potential_eur: float
    created_at: str = ""
    scheduled_for: str = ""
    status: str = "draft"              # draft, scheduled, posted, viral

@dataclass
class ContentBatch:
    """A batch of content across all platforms from one topic."""
    topic: str
    source_content: str                # The original long-form script
    pieces: List[ContentPiece] = field(default_factory=list)
    created_at: str = ""
    total_reach_estimate: int = 0


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Premium Topic Universe
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PREMIUM_TOPICS = {
    Niche.AI_AUTOMATION: [
        "Wie AI Agents 2026 komplette Unternehmen steuern",
        "ChatGPT vs Claude vs Gemini — Der BRUTALE Vergleich",
        "So ersetzt AI deinen kompletten Marketing-Stack",
        "Ich habe 100 Millionen AI Agents gebaut — Das passierte",
        "5 AI Tools die NIEMAND kennt (aber JEDER braucht)",
        "AI Automation: So sparst du 20 Stunden pro Woche",
        "Der ultimative n8n Tutorial — Automatisiere ALLES",
        "AI Chatbots die wirklich Geld verdienen (mit Beweis)",
        "So baust du einen AI Agent der für dich arbeitet",
        "Die Zukunft der Arbeit: AI Agents erklärt für Anfänger",
        "Warum 90% aller AI Tools NUTZLOS sind",
        "AI Automation Setup das ich JEDEM empfehle",
        "So nutzt du AI wie ein CEO (nicht wie ein User)",
        "Prompt Engineering: Die EINE Technik die alles ändert",
        "AI Tools Tier List 2026 — Von S bis F",
    ],
    Niche.MONEY_MAKING: [
        "€500/Tag mit AI — Mein komplettes Setup enthüllt",
        "5 AI Side Hustles die 2026 EXPLODIEREN werden",
        "So verdienst du €100/Stunde mit AI Freelancing",
        "AI Business von 0 auf €10.000/Monat — Der Plan",
        "Passive Income mit AI: Die WAHRHEIT",
        "Ich habe 30 Tage nur mit AI gearbeitet — So viel verdient",
        "Fiverr + AI = €3.000/Monat (Schritt für Schritt)",
        "Das €0 Budget AI Business — So startest du HEUTE",
        "AI Consulting: Wie du €5.000 pro Kunde verlangst",
        "10 Wege wie AI dein Einkommen VERDOPPELT",
    ],
    Niche.TECH_REVIEWS: [
        "Die BESTEN AI Tools 2026 — Mein ehrliches Ranking",
        "ChatGPT 5 Review: Lohnt sich das Update?",
        "Claude 4 vs GPT-5: Wer gewinnt den AI Krieg?",
        "n8n vs Zapier vs Make: Welches Automation Tool?",
        "Ollama Setup: Kostenlose AI auf deinem Mac",
        "DeepSeek R1: Das BESTE Open Source Modell?",
        "AI Coding Tools die Programmierer LIEBEN werden",
        "Die 10 unterschätztesten AI Tools 2026",
    ],
    Niche.PRODUCTIVITY: [
        "Mein KOMPLETTER AI Workflow — 4h Arbeit, 12h Ergebnis",
        "So automatisiere ich meinen GANZEN Tag mit AI",
        "AI Morning Routine: Maximale Produktivität ab 6 Uhr",
        "Second Brain mit AI: So vergisst du NIE wieder was",
        "Email Management mit AI: Von 100 auf 0 in 10 Minuten",
        "AI Meeting Notes: Nie wieder manuell Protokoll schreiben",
    ],
    Niche.SIDE_HUSTLE: [
        "YouTube Faceless Kanal: €5.000/Monat ohne Kamera",
        "AI Content Agency: So baust du sie in 7 Tagen",
        "TikTok Shop + AI = Gelddruckmaschine?",
        "Print on Demand mit AI Designs — Funktioniert es?",
        "AI Copywriting Service: €2.000/Monat als Anfänger",
        "Amazon KDP mit AI: Bücher schreiben die sich verkaufen",
    ],
}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Optimal Posting Times (German audience, UTC+1)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OPTIMAL_TIMES = {
    Platform.YOUTUBE: ["15:00", "17:00", "19:00"],          # After work
    Platform.YOUTUBE_SHORTS: ["07:00", "12:00", "18:00", "21:00"],  # Throughout day
    Platform.TIKTOK: ["07:00", "12:00", "17:00", "19:00", "21:00"],  # High frequency
    Platform.INSTAGRAM_REELS: ["08:00", "12:30", "17:30", "20:00"],
    Platform.INSTAGRAM_CAROUSEL: ["09:00", "13:00", "18:00"],
    Platform.TWITTER_THREAD: ["08:00", "12:00", "17:00"],
    Platform.TWITTER_SINGLE: ["07:00", "09:00", "12:00", "15:00", "18:00", "21:00"],
    Platform.LINKEDIN: ["08:00", "10:00", "12:00"],
}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AI Content Generator
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class AIContentGenerator:
    """Generates premium content using Kimi or local Ollama."""

    def __init__(self) -> None:
        self.session: aiohttp.ClientSession = None  # type: ignore[assignment]
        self.use_local: bool = not KIMI_API_KEY
        self.generated_count: int = 0

    async def init(self):
        self.session = aiohttp.ClientSession()

    async def close(self) -> None:
        if self.session is not None:
            await self.session.close()

    async def _call_llm(self, system_prompt: str, user_prompt: str, temperature: float = 0.85) -> str:
        """Call either Kimi or local Ollama."""
        if self.session is None:
            await self.init()

        if self.use_local:
            return await self._call_ollama(system_prompt, user_prompt, temperature)
        return await self._call_kimi(system_prompt, user_prompt, temperature)

    async def _call_kimi(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        session = self.session
        try:
            async with session.post(
                "https://api.moonshot.cn/v1/chat/completions",
                headers={"Authorization": f"Bearer {KIMI_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "moonshot-v1-8k",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": temperature
                },
                timeout=aiohttp.ClientTimeout(total=60)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return str(data["choices"][0]["message"]["content"])
                else:
                    logger.warning(f"Kimi API error {resp.status}")
                    return await self._call_ollama(system_prompt, user_prompt, temperature)
        except Exception as e:
            logger.warning(f"Kimi failed: {e}, falling back to Ollama")
            return await self._call_ollama(system_prompt, user_prompt, temperature)

    async def _call_ollama(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        session = self.session
        try:
            async with session.post(
                f"{OLLAMA_HOST}/api/chat",
                json={
                    "model": "qwen2.5-coder:14b",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "stream": False,
                    "options": {"temperature": temperature}
                },
                timeout=aiohttp.ClientTimeout(total=120)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return str(data.get("message", {}).get("content", ""))
                logger.error(f"Ollama error: {resp.status}")
                return self._generate_fallback(user_prompt)
        except Exception as e:
            logger.warning(f"Ollama unavailable: {e}")
            return self._generate_fallback(user_prompt)

    def _generate_fallback(self, prompt: str) -> str:
        """Deterministic fallback content when no LLM is available."""
        topic = prompt[:100]
        return json.dumps({
            "hook": f"🔥 Das MÜSST ihr wissen über {topic[:50]}...",
            "body": f"In diesem Beitrag zeige ich euch die 5 wichtigsten Punkte zu {topic[:50]}.\n\n"
                    "1. Punkt 1: Der wichtigste Faktor\n"
                    "2. Punkt 2: Was die meisten falsch machen\n"
                    "3. Punkt 3: Der Game-Changer\n"
                    "4. Punkt 4: Mein persönlicher Geheimtipp\n"
                    "5. Punkt 5: So startest du HEUTE",
            "cta": "💬 Was ist euer Lieblings-AI Tool? Schreibt's in die Kommentare!",
            "hashtags": ["#AI", "#Automation", "#KI", "#Tech", "#Zukunft"],
            "thumbnail_prompt": f"Futuristic dark tech visualization about {topic[:30]}, neon blue glow, premium look"
        })


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Platform-Specific Content Formatters
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class PlatformFormatter:
    """Formats content for specific platforms with premium prompts."""

    SYSTEM_PROMPTS = {
        Platform.YOUTUBE: """Du bist ein Premium YouTube Script Writer für Faceless Channels.
Du schreibst Scripts die:
- Einen UNWIDERSTEHLICHEN Hook in den ersten 5 Sekunden haben
- Storytelling-Elemente nutzen (Problem → Spannung → Lösung)
- Retention maximieren (keine langweiligen Stellen)
- CTA am Ende für Likes, Abos und Kommentare
- B-Roll Anweisungen in [ECKIGEN KLAMMERN] enthalten
- 8-12 Minuten lang sind (optimal für Monetarisierung)
- Auf Deutsch geschrieben sind, lockerer Ton, Du-Ansprache""",

        Platform.YOUTUBE_SHORTS: """Du bist ein YouTube Shorts Experte für MAXIMALE Viralität.
Regeln:
- HOOK in der ERSTEN SEKUNDE (Schock, Frage, Statement)
- Maximal 58 Sekunden Script
- Schnelle Schnitte alle 2-3 Sekunden [SCHNITT] markieren
- Kein Intro, kein Outro — direkt rein
- Letzter Satz = CTA oder Cliffhanger
- Deutsch, Gen-Z kompatibel, energetisch
- Emoji in der Beschreibung""",

        Platform.TIKTOK: """Du bist ein viraler TikTok Content Creator (Faceless).
Strategie:
- HOOK in 0.5 Sekunden (Schock-Statement oder kontroverse Frage)
- Maximal 60 Sekunden
- Text-on-Screen Anweisungen: [TEXT: "..."] 
- Trending Sound Suggestion: [SOUND: "..."]
- Transition Moments: [TRANSITION]
- Schnelllebig, punchy, keine Füllwörter
- Deutsch oder Denglisch, authentisch
- Green Screen / Screen Recording Style möglich""",

        Platform.INSTAGRAM_REELS: """Du bist ein Instagram Reels Experte (Faceless).
Format:
- 30-90 Sekunden optimal
- Visuell ansprechend — jede Sekunde Mehrwert
- Text Overlays: [OVERLAY: "..."]
- Ästhetisch, clean, premium Look
- Transition-heavy, smooth cuts
- CTA: "Speichern für später" oder "Teilen mit Freund"
- Deutsch, professionell aber nahbar""",

        Platform.INSTAGRAM_CAROUSEL: """Du bist ein Instagram Carousel Designer.
Erstelle ein 8-10 Slide Carousel mit:
- Slide 1: Aufmerksamkeits-Hook (Frage oder Statement)
- Slides 2-8: Mehrwert-Content (1 Punkt pro Slide)
- Vorletzte Slide: Zusammenfassung
- Letzte Slide: CTA (Speichern, Folgen, Link in Bio)
- Jede Slide: Titel + 2-3 Bullet Points max
- Design-Vorschlag: Dunkler Background, helle Schrift, Akzent-Farbe Gold
Output als JSON mit key "slides" (liste von {title, points, design_note})""",

        Platform.TWITTER_THREAD: """Du bist ein Top X/Twitter Ghostwriter.
Thread-Regeln:
- Tweet 1: HOOK der alles stoppt (keine Emojis im Hook)
- 5-7 Tweets, jeder steht für sich UND im Kontext
- Letzter Tweet: CTA + "Folge mir für mehr"
- Kurze Sätze, White Space, leicht zu scannen
- Keine Hashtags im Thread selbst (nur im letzten Tweet)
- Deutsch, aber international ansprechend
Output als JSON: {"tweets": ["...", "..."]}""",

        Platform.TWITTER_SINGLE: """Du bist ein Twitter/X Engagement-Experte.
Single Tweet Regeln:
- Maximal 260 Zeichen
- Provokant ODER wertvoll (nie langweilig)
- Kann Frage, Statement oder Hot Take sein
- Kein "Ich denke" — Sei direkt
- Deutsch, punchy
Output als JSON: {"tweet": "..."}""",

        Platform.LINKEDIN: """Du bist ein LinkedIn Thought Leadership Experte.
LinkedIn Post Regeln:
- Erster Satz = Hook (Problem oder kontroverse Beobachtung)
- Persönliche Story oder Case Study einbauen
- Bullet Points für Scanbarkeit
- 800-1200 Zeichen optimal
- CTA: Frage an die Community
- Professionell, aber menschlich
- 3-5 relevante Hashtags am Ende (nicht mehr!)
- Deutsch, Sie-Ansprache für LinkedIn""",
    }

    @staticmethod
    def get_user_prompt(platform: Platform, topic: str, style: ContentStyle, niche: Niche) -> str:
        """Generate the user prompt for each platform."""
        style_instructions = {
            ContentStyle.VIRAL: "Optimiere für MAXIMALE Viralität. Kontrovers aber wahr.",
            ContentStyle.EDUCATIONAL: "Fokus auf LERNWERT. Schritt für Schritt. Actionable.",
            ContentStyle.STORYTELLING: "Erzähle eine FESSELNDE Geschichte. Problem → Reise → Lösung.",
            ContentStyle.CONTROVERSIAL: "Hot Take! Provoziere Diskussion. Aber fundiert.",
            ContentStyle.LISTICLE: "Nummerierte Liste. Klar, scannbar, überraschend.",
            ContentStyle.CASE_STUDY: "Echte Zahlen, echte Ergebnisse. Vor/Nach Vergleich.",
            ContentStyle.HOW_TO: "Schritt-für-Schritt Anleitung. Sofort umsetzbar.",
            ContentStyle.NEWS: "Aktuelle Entwicklung. Einordnung + eigene Meinung.",
        }

        base_prompt = f"""
THEMA: {topic}
NISCHE: {niche.value}
STIL: {style_instructions.get(style, style_instructions[ContentStyle.VIRAL])}
PLATTFORM: {platform.value}

Erstelle den Content im JSON-Format mit diesen Keys:
- "hook": Der erste Satz / das erste was man sieht
- "body": Der Hauptinhalt
- "cta": Call to Action
- "hashtags": Liste relevanter Hashtags (5-10)
- "thumbnail_prompt": Englischer Prompt für AI Thumbnail Generation (premium, dark, futuristic)
- "visual_notes": Anweisungen für B-Roll / Visuals
- "engagement_score": Deine Einschätzung 1-10 wie viral das wird

NUR JSON output, keine Erklärung drumherum.
"""
        return base_prompt


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# The Main Engine — Faceless Empire
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class FacelessEmpire:
    """
    The main content engine. Generates premium faceless content
    across all platforms from a single topic.
    """

    def __init__(self) -> None:
        self.ai = AIContentGenerator()
        self.total_generated: int = 0
        self.by_platform: Dict[str, int] = {}
        self.revenue_potential: float = 0.0
        self.started_at: str = datetime.now().isoformat()

    async def init(self):
        await self.ai.init()

    async def close(self):
        await self.ai.close()

    def _generate_id(self, platform: str, topic: str) -> str:
        raw = f"{platform}_{topic}_{datetime.now().isoformat()}"
        return hashlib.md5(raw.encode()).hexdigest()[:12]

    def _pick_topic(self, niche: Optional[Niche] = None) -> Tuple[str, Niche]:
        if niche:
            topics = PREMIUM_TOPICS.get(niche, PREMIUM_TOPICS[Niche.AI_AUTOMATION])
            return random.choice(topics), niche
        else:
            niche = random.choice(list(PREMIUM_TOPICS.keys()))
            return random.choice(PREMIUM_TOPICS[niche]), niche

    def _parse_ai_response(self, response: str) -> Dict:
        """Parse JSON from AI response, handling markdown code blocks."""
        text = response.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {
                "hook": text[:200],
                "body": text,
                "cta": "Folge für mehr! 🚀",
                "hashtags": ["#AI", "#Automation", "#KI"],
                "thumbnail_prompt": "futuristic dark tech ai visualization premium",
                "visual_notes": "Screen recordings, tech B-roll",
                "engagement_score": 7
            }

    async def generate_for_platform(
        self, 
        platform: Platform, 
        topic: str, 
        niche: Niche,
        style: ContentStyle = ContentStyle.VIRAL
    ) -> ContentPiece:
        """Generate a single content piece for a specific platform."""
        logger.info(f"  🎬 Generating {platform.value} content: {topic[:50]}...")

        system_prompt = PlatformFormatter.SYSTEM_PROMPTS.get(
            platform, 
            PlatformFormatter.SYSTEM_PROMPTS[Platform.TIKTOK]
        )
        user_prompt = PlatformFormatter.get_user_prompt(platform, topic, style, niche)

        response = await self.ai._call_llm(system_prompt, user_prompt)
        data = self._parse_ai_response(response)

        # Duration estimates by platform
        duration_map = {
            Platform.YOUTUBE: 480,           # 8 minutes
            Platform.YOUTUBE_SHORTS: 45,     # 45 seconds
            Platform.TIKTOK: 45,             # 45 seconds
            Platform.INSTAGRAM_REELS: 60,    # 60 seconds
            Platform.INSTAGRAM_CAROUSEL: 0,  # Static
            Platform.TWITTER_THREAD: 0,      # Static
            Platform.TWITTER_SINGLE: 0,      # Static
            Platform.LINKEDIN: 0,            # Static
        }

        # Revenue estimates by platform (monthly contribution per piece)
        revenue_map = {
            Platform.YOUTUBE: 50.0,
            Platform.YOUTUBE_SHORTS: 5.0,
            Platform.TIKTOK: 10.0,
            Platform.INSTAGRAM_REELS: 8.0,
            Platform.INSTAGRAM_CAROUSEL: 3.0,
            Platform.TWITTER_THREAD: 15.0,
            Platform.TWITTER_SINGLE: 2.0,
            Platform.LINKEDIN: 25.0,
        }

        optimal_times = OPTIMAL_TIMES.get(platform, ["12:00"])
        post_time = random.choice(optimal_times)

        platform_str = str(platform.value)
        style_str = str(style.value)
        niche_str = str(niche.value)

        piece = ContentPiece(
            id=self._generate_id(platform_str, topic),
            platform=platform_str,
            style=style_str,
            niche=niche_str,
            title=topic,
            hook=str(data.get("hook", "")),
            body=str(data.get("body", "")),
            call_to_action=str(data.get("cta", "Folge für mehr!")),
            hashtags=data.get("hashtags", ["#AI", "#Automation"]),
            tags=data.get("tags", [topic.split()[0], niche_str]),
            thumbnail_prompt=str(data.get("thumbnail_prompt", "futuristic ai tech dark premium")),
            visual_notes=str(data.get("visual_notes", "Tech B-roll, screen recordings")),
            estimated_duration_sec=duration_map.get(platform, 60),
            optimal_post_time=post_time,
            engagement_prediction=float(data.get("engagement_score", 7)),
            revenue_potential_eur=revenue_map.get(platform, 5.0),
            created_at=datetime.now().isoformat(),
        )

        self.total_generated += 1
        self.by_platform[platform_str] = self.by_platform.get(platform_str, 0) + 1
        self.revenue_potential += piece.revenue_potential_eur

        return piece

    async def generate_cross_platform(
        self, 
        topic: Optional[str] = None,
        niche: Optional[Niche] = None,
        platforms: Optional[List[Platform]] = None,
        style: ContentStyle = ContentStyle.VIRAL
    ) -> ContentBatch:
        """Generate content for ALL platforms from ONE topic (1-to-many repurposing)."""
        if not topic:
            topic, niche = self._pick_topic(niche)
        if not niche:
            niche = Niche.AI_AUTOMATION

        if not platforms:
            platforms = [
                Platform.YOUTUBE_SHORTS,
                Platform.TIKTOK,
                Platform.INSTAGRAM_REELS,
                Platform.INSTAGRAM_CAROUSEL,
                Platform.TWITTER_THREAD,
                Platform.TWITTER_SINGLE,
                Platform.LINKEDIN,
            ]

        logger.info(f"\n{'━'*60}")
        logger.info(f"👑 FACELESS EMPIRE — Cross-Platform Generation")
        logger.info(f"📝 Topic: {topic}")
        logger.info(f"🎯 Niche: {niche.value}")
        logger.info(f"🎨 Style: {style.value}")
        logger.info(f"📱 Platforms: {len(platforms)}")
        logger.info(f"{'━'*60}\n")

        batch = ContentBatch(
            topic=topic,
            source_content="",
            created_at=datetime.now().isoformat()
        )

        # Generate for each platform (with small delays for rate limiting)
        for platform in platforms:
            try:
                piece = await self.generate_for_platform(platform, topic, niche, style)
                batch.pieces.append(piece)
                self._save_piece(piece)
                logger.info(f"  ✅ {platform.value}: {piece.hook[:60]}...")
                await asyncio.sleep(0.5)  # Rate limiting
            except Exception as e:
                logger.error(f"  ❌ {platform.value} failed: {e}")

        batch.total_reach_estimate = len(batch.pieces) * 5000  # Conservative estimate
        self._save_batch(batch)

        logger.info(f"\n{'━'*60}")
        logger.info(f"✅ Batch complete: {len(batch.pieces)} pieces generated")
        logger.info(f"📊 Estimated reach: {batch.total_reach_estimate:,} views")
        logger.info(f"💰 Revenue potential: €{sum(p.revenue_potential_eur for p in batch.pieces):,.2f}/month")
        logger.info(f"{'━'*60}\n")

        return batch

    async def blitz(self, count: int = 5, niche: Optional[Niche] = None) -> List[ContentBatch]:
        """
        CONTENT BLITZ — Generate cross-platform content for multiple topics.
        count = number of topics, each producing 7+ pieces.
        """
        logger.info(f"\n{'═'*60}")
        logger.info(f"⚡⚡⚡ CONTENT BLITZ MODE — {count} topics × 7+ platforms ⚡⚡⚡")
        logger.info(f"{'═'*60}\n")

        batches = []
        styles = list(ContentStyle)

        for i in range(count):
            topic, picked_niche = self._pick_topic(niche)
            style = styles[i % len(styles)]

            logger.info(f"\n🔥 [{i+1}/{count}] Generating batch for: {topic[:50]}...")
            batch = await self.generate_cross_platform(
                topic=topic, 
                niche=picked_niche, 
                style=style
            )
            batches.append(batch)

        # Final report
        total_pieces = sum(len(b.pieces) for b in batches)
        total_revenue = sum(p.revenue_potential_eur for b in batches for p in b.pieces)

        logger.info(f"\n{'═'*60}")
        logger.info(f"🏆 BLITZ COMPLETE!")
        logger.info(f"📊 Total content pieces: {total_pieces}")
        logger.info(f"📱 Platforms covered: {len(set(p.platform for b in batches for p in b.pieces))}")
        logger.info(f"💰 Total revenue potential: €{total_revenue:,.2f}/month")
        logger.info(f"📂 Content saved to: {OUTPUT_DIR}")
        logger.info(f"{'═'*60}\n")

        return batches

    def _save_piece(self, piece: ContentPiece):
        """Save a content piece to the appropriate platform directory."""
        platform_dirs = {
            "youtube": YOUTUBE_DIR,
            "youtube_shorts": YOUTUBE_DIR / "shorts",
            "tiktok": TIKTOK_DIR,
            "instagram_reels": INSTAGRAM_DIR / "reels",
            "instagram_carousel": INSTAGRAM_DIR / "carousels",
            "instagram_story": INSTAGRAM_DIR / "stories",
            "twitter_thread": TWITTER_DIR / "threads",
            "twitter_single": TWITTER_DIR / "tweets",
            "linkedin": OUTPUT_DIR / "linkedin",
            "blog": OUTPUT_DIR / "blog",
        }

        target_dir = platform_dirs.get(piece.platform, OUTPUT_DIR)
        target_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{piece.id}_{piece.platform}.json"
        filepath = target_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(asdict(piece), f, indent=2, ensure_ascii=False)

        # Also save a human-readable version
        readable_file = target_dir / f"{piece.id}_{piece.platform}.md"
        with open(readable_file, "w", encoding="utf-8") as f:
            f.write(f"# {piece.title}\n\n")
            f.write(f"**Platform**: {piece.platform}\n")
            f.write(f"**Style**: {piece.style}\n")
            f.write(f"**Optimal Post Time**: {piece.optimal_post_time}\n")
            f.write(f"**Engagement Prediction**: {piece.engagement_prediction}/10\n\n")
            f.write(f"---\n\n")
            f.write(f"## 🎣 Hook\n{piece.hook}\n\n")
            f.write(f"## 📝 Body\n{piece.body}\n\n")
            f.write(f"## 📢 Call to Action\n{piece.call_to_action}\n\n")
            f.write(f"## 🏷️ Hashtags\n{' '.join(piece.hashtags)}\n\n")
            f.write(f"## 🎨 Thumbnail Prompt\n{piece.thumbnail_prompt}\n\n")
            f.write(f"## 📹 Visual Notes\n{piece.visual_notes}\n\n")

    def _save_batch(self, batch: ContentBatch):
        """Save the batch summary."""
        filepath = SCHEDULE_DIR / f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump({
                "topic": batch.topic,
                "created_at": batch.created_at,
                "total_pieces": len(batch.pieces),
                "total_reach_estimate": batch.total_reach_estimate,
                "platforms": [p.platform for p in batch.pieces],
                "pieces": [asdict(p) for p in batch.pieces],
            }, f, indent=2, ensure_ascii=False)

    def generate_weekly_schedule(self, batches: List[ContentBatch]) -> Dict:
        """Generate a 7-day posting schedule from generated batches."""
        schedule = {}
        all_pieces = [p for b in batches for p in b.pieces]
        
        days = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
        
        for i, day in enumerate(days):
            schedule[day] = []
            # Distribute pieces across days
            day_pieces = all_pieces[i::7]
            for piece in day_pieces:
                schedule[day].append({
                    "platform": piece.platform,
                    "time": piece.optimal_post_time,
                    "title": piece.title[:50],
                    "hook": piece.hook[:80],
                    "type": piece.style,
                })

        # Save schedule
        filepath = SCHEDULE_DIR / f"weekly_schedule_{datetime.now().strftime('%Y%m%d')}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(schedule, f, indent=2, ensure_ascii=False)

        logger.info(f"📅 Weekly schedule saved to: {filepath}")
        return schedule

    def print_dashboard(self) -> None:
        """Print a premium dashboard of generated content."""
        print(f"\n{'═'*60}")
        print(f"👑  FACELESS EMPIRE — Dashboard")
        print(f"{'═'*60}")
        print(f"📊 Total Generated:    {self.total_generated}")
        print(f"💰 Revenue Potential:   €{self.revenue_potential:,.2f}/month")
        print(f"⏱️  Started:            {self.started_at[:19]}")
        print(f"{'─'*60}")
        print(f"📱 By Platform:")
        for platform, count in sorted(self.by_platform.items()):
            bar = "█" * count + "░" * (20 - min(count, 20))
            print(f"   {platform:<25} {bar} {count}")
        print(f"{'═'*60}")
        print(f"📂 Output: {OUTPUT_DIR}")
        print(f"{'═'*60}\n")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLI Interface
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def main():
    parser = argparse.ArgumentParser(
        description="👑 Faceless Empire — Premium Multi-Platform Content Machine"
    )
    parser.add_argument("--generate", type=int, default=3, help="Number of topics to generate")
    parser.add_argument("--platform", type=str, default="all", 
                       help="Platform: youtube, tiktok, instagram, twitter, all")
    parser.add_argument("--niche", type=str, default=None,
                       help="Niche: ai_automation, money_making, tech_reviews, etc.")
    parser.add_argument("--style", type=str, default="viral",
                       help="Style: viral, educational, storytelling, controversial")
    parser.add_argument("--blitz", action="store_true", help="Full blitz mode (all platforms)")
    parser.add_argument("--schedule", action="store_true", help="Generate weekly schedule")
    parser.add_argument("--topic", type=str, default=None, help="Specific topic to cover")

    args = parser.parse_args()

    empire = FacelessEmpire()
    await empire.init()

    try:
        # Map niche string to enum
        niche = None
        if args.niche:
            niche_map = {n.value: n for n in Niche}
            niche = niche_map.get(args.niche, Niche.AI_AUTOMATION)

        # Map style string to enum
        style_map = {s.value: s for s in ContentStyle}
        style = style_map.get(args.style, ContentStyle.VIRAL)

        # Map platform filter
        platform_map = {
            "youtube": [Platform.YOUTUBE, Platform.YOUTUBE_SHORTS],
            "tiktok": [Platform.TIKTOK],
            "instagram": [Platform.INSTAGRAM_REELS, Platform.INSTAGRAM_CAROUSEL],
            "twitter": [Platform.TWITTER_THREAD, Platform.TWITTER_SINGLE],
            "linkedin": [Platform.LINKEDIN],
            "all": None,  # None = all platforms
        }
        platforms = platform_map.get(args.platform, None)

        if args.blitz or args.generate > 1:
            # Full blitz mode
            batches = await empire.blitz(count=args.generate, niche=niche)
            
            if args.schedule:
                empire.generate_weekly_schedule(batches)
        else:
            # Single topic
            batch = await empire.generate_cross_platform(
                topic=args.topic,
                niche=niche,
                platforms=platforms,
                style=style
            )

        empire.print_dashboard()

    finally:
        await empire.close()


if __name__ == "__main__":
    asyncio.run(main())
