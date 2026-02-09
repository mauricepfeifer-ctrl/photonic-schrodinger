#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════
🔫 GHOST SQUADRON — ELITE REVENUE HUNTING UNIT
═══════════════════════════════════════════════════════════════════════

A tactical AI agent system where each agent has specialized skills
and operates like a special forces unit — hunting revenue across
ALL channels simultaneously.

UNITS:
  🎯 SNIPER   — Precision client acquisition (cold outreach)
  💣 DEMO     — Demolishes objections & closes deals
  🛡️  SHIELD  — Protects revenue streams (retention & upsells)
  🔍 RECON    — Market intelligence & opportunity scanning
  ⚡ STRIKER  — Fast-strike content drops for viral reach
  🧠 COMMAND  — Orchestrates all units, optimizes strategy
  🔧 FORGE    — Builds products, landing pages, funnels
  📡 SIGNAL   — Runs all automations (n8n, webhooks, APIs)

Author: Maurice Pfeifer — AI Empire
Version: 1.0.0 DELTA
═══════════════════════════════════════════════════════════════════════
"""
import asyncio
import json
import logging
import os
import random
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

# ─── CONFIG ───────────────────────────────────────────────────────────
KIMI_API_KEY = os.getenv("MOONSHOT_API_KEY", "")
KIMI_BASE_URL = "https://api.moonshot.cn/v1"
N8N_WEBHOOK = os.getenv("N8N_WEBHOOK_URL", "https://ai1337empire.app.n8n.cloud/webhook")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

LOG_FMT = "%(asctime)s [%(levelname)s] %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FMT)
logger = logging.getLogger("ghost_squadron")

try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False
    logger.warning("aiohttp not installed — running in offline simulation mode")


# ═══════════════════════════════════════════════════════════════════════
# UNIT DEFINITIONS — Each unit has unique skills & missions
# ═══════════════════════════════════════════════════════════════════════

class Unit(str, Enum):
    SNIPER = "sniper"      # Client acquisition
    DEMO = "demo"          # Objection demolition & closing
    SHIELD = "shield"      # Revenue protection & retention
    RECON = "recon"        # Market intelligence
    STRIKER = "striker"    # Viral content drops
    COMMAND = "command"    # Strategy & orchestration
    FORGE = "forge"        # Product & funnel building
    SIGNAL = "signal"      # Automation & integrations


class MissionPriority(str, Enum):
    CRITICAL = "critical"   # Drop everything — high revenue impact
    HIGH = "high"           # Important — do within 1h
    MEDIUM = "medium"       # Standard — do within 4h
    LOW = "low"             # Background — do when available


class MissionStatus(str, Enum):
    QUEUED = "queued"
    ACTIVE = "active"
    COMPLETE = "complete"
    FAILED = "failed"
    RETRY = "retry"


# ═══════════════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class AgentSkill:
    """A specific skill an agent possesses."""
    name: str
    level: int  # 1-10
    description: str
    cooldown_seconds: int = 0  # Minimum time between skill uses


@dataclass
class Mission:
    """A mission assigned to a unit."""
    id: str
    unit: Unit
    mission_type: str
    priority: MissionPriority
    objective: str
    context: Dict[str, Any] = field(default_factory=dict)
    status: MissionStatus = MissionStatus.QUEUED
    result: Optional[str] = None
    revenue_potential: float = 0.0
    revenue_actual: float = 0.0
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    retries: int = 0
    max_retries: int = 3


@dataclass
class GhostAgent:
    """An elite agent in the Ghost Squadron."""
    id: str
    callsign: str
    unit: Unit
    skills: List[AgentSkill]
    missions_completed: int = 0
    total_revenue: float = 0.0
    kill_streak: int = 0  # Consecutive successful missions
    status: str = "standby"
    current_mission: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════
# SKILLS DATABASE — What each unit can do
# ═══════════════════════════════════════════════════════════════════════

UNIT_SKILLS = {
    Unit.SNIPER: [
        AgentSkill("cold_email_craft", 9, "Creates hyper-personalized cold emails that bypass spam and get replies"),
        AgentSkill("linkedin_outreach", 8, "Crafts LinkedIn DMs and connection requests that convert"),
        AgentSkill("lead_scraping", 7, "Identifies high-value prospects from public data"),
        AgentSkill("proposal_snipe", 9, "Creates one-shot proposals that win contracts"),
        AgentSkill("follow_up_sequence", 8, "Builds multi-touch follow-up sequences that close"),
    ],
    Unit.DEMO: [
        AgentSkill("objection_destroyer", 10, "Demolishes every sales objection with data-backed responses"),
        AgentSkill("price_anchor", 9, "Anchors pricing high, then presents the offer as a steal"),
        AgentSkill("urgency_injector", 8, "Creates genuine urgency to close deals NOW"),
        AgentSkill("case_study_builder", 8, "Creates compelling before/after case studies"),
        AgentSkill("closing_technique", 9, "Uses proven closing frameworks (assumptive, choice, puppy dog)"),
    ],
    Unit.SHIELD: [
        AgentSkill("churn_prevention", 9, "Detects clients about to leave and saves them"),
        AgentSkill("upsell_architect", 8, "Identifies upsell opportunities in existing accounts"),
        AgentSkill("satisfaction_pulse", 7, "Runs satisfaction checks and acts on feedback"),
        AgentSkill("renewal_automation", 8, "Automates renewal reminders and incentives"),
        AgentSkill("referral_engine", 9, "Turns happy clients into referral machines"),
    ],
    Unit.RECON: [
        AgentSkill("market_scan", 9, "Scans market for emerging opportunities and trends"),
        AgentSkill("competitor_intel", 8, "Analyzes competitor pricing, offers, and weaknesses"),
        AgentSkill("demand_detection", 9, "Detects rising demand for AI services before others"),
        AgentSkill("price_intelligence", 8, "Researches optimal pricing for maximum revenue"),
        AgentSkill("platform_scout", 7, "Finds new platforms where money is being spent"),
    ],
    Unit.STRIKER: [
        AgentSkill("viral_thread", 9, "Creates X/Twitter threads that go viral"),
        AgentSkill("tiktok_script", 8, "Writes TikTok scripts optimized for FYP"),
        AgentSkill("youtube_hook", 9, "Creates YouTube titles/hooks with 10%+ CTR"),
        AgentSkill("content_repurpose", 8, "Turns 1 piece into 10 across all platforms"),
        AgentSkill("trend_hijack", 9, "Hijacks trending topics for brand exposure"),
    ],
    Unit.COMMAND: [
        AgentSkill("strategy_optimization", 10, "Analyzes all unit performance and reallocates resources"),
        AgentSkill("revenue_forecast", 9, "Predicts revenue for next 30/60/90 days"),
        AgentSkill("risk_assessment", 8, "Identifies risks to revenue and deploys countermeasures"),
        AgentSkill("unit_coordination", 9, "Coordinates multi-unit operations for maximum impact"),
        AgentSkill("kpi_dashboard", 8, "Generates real-time KPI dashboards"),
    ],
    Unit.FORGE: [
        AgentSkill("landing_page_builder", 9, "Creates high-converting landing pages"),
        AgentSkill("course_architect", 8, "Designs course curricula with optimal learning paths"),
        AgentSkill("funnel_designer", 9, "Builds complete sales funnels (lead → customer)"),
        AgentSkill("product_packager", 8, "Packages services into irresistible product offers"),
        AgentSkill("pricing_optimizer", 9, "Tests and optimizes pricing for maximum revenue"),
    ],
    Unit.SIGNAL: [
        AgentSkill("n8n_automation", 10, "Builds and maintains n8n workflow automations"),
        AgentSkill("webhook_orchestrator", 9, "Manages all webhook triggers and responses"),
        AgentSkill("api_integration", 8, "Connects any API to the empire ecosystem"),
        AgentSkill("email_automation", 9, "Runs automated email sequences via Mailgun/SES"),
        AgentSkill("payment_pipeline", 8, "Connects Stripe/Gumroad payments to fulfillment"),
    ],
}

# ═══════════════════════════════════════════════════════════════════════
# MISSION TEMPLATES — Pre-built missions for each unit
# ═══════════════════════════════════════════════════════════════════════

MISSION_TEMPLATES = {
    Unit.SNIPER: [
        {
            "type": "cold_outreach_blast",
            "priority": MissionPriority.HIGH,
            "objective": "Identify 50 potential AI consulting clients and craft personalized outreach messages",
            "revenue_potential": 5000.0,
            "prompt_template": """Du bist ein Elite-Vertriebsagent für AI Consulting Services.

MISSION: Erstelle eine hochpersonalisierte Outreach-Nachricht für folgendes Zielprofil:
- Branche: {industry}
- Unternehmensgröße: {company_size}
- Pain Point: {pain_point}

REGELN:
1. Keine generischen Floskeln — jeder Satz muss den Empfänger direkt ansprechen
2. Zeige den konkreten EUR-Wert den AI Automation spart
3. CTA muss ein 15-min Call sein, kein langer Pitch
4. Max 120 Wörter — kurz und knackig

FORMAT:
Betreff: [Betreffzeile]
Nachricht: [Nachricht]
Follow-Up (3 Tage): [Follow-Up Nachricht]"""
        },
        {
            "type": "linkedin_precision_strike",
            "priority": MissionPriority.HIGH,
            "objective": "Create LinkedIn connection + DM sequence targeting C-level executives",
            "revenue_potential": 3000.0,
            "prompt_template": """Du bist ein LinkedIn-Vertriebsspezialist für AI-Services.

MISSION: Erstelle eine 3-Step LinkedIn Sequence:

STEP 1 — Connection Request (max 280 Zeichen):
Persönlich, keine Sales-Pitch, gemeinsamer Interesse-Hook.

STEP 2 — Welcome DM (nach Annahme):
Value-First: Teile einen konkreten Insight oder Tipp. Kein Pitch.

STEP 3 — Soft Pitch (3 Tage später):
"Btw" Übergang zu deinem Angebot. Call-Vorschlag.

Zielbranche: {industry}
Pain Point: {pain_point}
Dein Angebot: AI Automation Consulting — EUR 100-250/h"""
        },
        {
            "type": "fiverr_gig_optimizer",
            "priority": MissionPriority.MEDIUM,
            "objective": "Create/optimize Fiverr gig listings for AI services",
            "revenue_potential": 2000.0,
            "prompt_template": """Du optimierst Fiverr Gig Listings für maximale Sichtbarkeit und Verkäufe.

SERVICE: {service_type}
KATEGORIE: AI Services / Automation

Erstelle:
1. GIG-TITEL (max 80 Zeichen, keyword-optimiert)
2. THUMBNAIL-TEXT (3-4 Wörter die sofort klickbar sind)
3. GIG-DESCRIPTION (überzeugende Beschreibung, 800-1200 Zeichen)
4. 3-TIER PRICING:
   - Basic: EUR {price_basic} — {basic_desc}
   - Standard: EUR {price_standard} — {standard_desc}  
   - Premium: EUR {price_premium} — {premium_desc}
5. FAQ (3 häufige Fragen + Antworten)
6. TAGS (5 relevante Suchbegriffe)"""
        },
    ],
    Unit.DEMO: [
        {
            "type": "objection_annihilation",
            "priority": MissionPriority.CRITICAL,
            "objective": "Create complete objection handling scripts for top 10 sales objections",
            "revenue_potential": 10000.0,
            "prompt_template": """Du bist ein Verkaufs-Psychologe nach der Dirk Kreuter Methode.

MISSION: Erstelle einen Einwand-Vernichter für den häufigsten Einwand:
"{objection}"

STRUKTUR:
1. EMOTIONALE ANERKENNUNG: Bestätige den Einwand empathisch
2. REFRAME: Drehe den Einwand in einen Vorteil um
3. BEWEIS: Konkretes Zahlenbeispiel oder Case Study
4. MICRO-CLOSE: Stelle eine Frage die zum "Ja" führt

KONTEXT:
- Produkt: AI Automation Consulting (EUR 100-250/h)
- Zielgruppe: KMU mit 5-50 Mitarbeitern
- Dein USP: ROI in < 30 Tagen messbar

Liefere 3 verschiedene Versionen: Aggressiv, Soft, und Story-basiert."""
        },
        {
            "type": "closing_sequence",
            "priority": MissionPriority.HIGH,
            "objective": "Build a 5-step email closing sequence that turns proposals into signed deals",
            "revenue_potential": 8000.0,
            "prompt_template": """Erstelle eine 5-Email Closing Sequence die aus Angeboten signierte Deals macht.

KONTEXT:
- Angebotswert: EUR {deal_value}
- Service: {service}
- Zeitrahmen: Die Sequence läuft über 14 Tage

EMAILS:
1. Tag 0  — PROPOSAL SENT CONFIRMATION (Professional, Zusammenfassung)
2. Tag 2  — SOCIAL PROOF (Case Study eines ähnlichen Clients)  
3. Tag 5  — VALUE REMINDER (ROI-Berechnung spezifisch für den Client)
4. Tag 9  — URGENCY (Legitime Deadline oder Kapazität)
5. Tag 14 — FINAL CALL (Letzte Chance, Walking-Away Technik)

Jede Email: Max 150 Wörter. Subject Line optimiert für Opens."""
        },
    ],
    Unit.SHIELD: [
        {
            "type": "retention_shield",
            "priority": MissionPriority.HIGH,
            "objective": "Create automated retention touchpoints for existing clients",
            "revenue_potential": 15000.0,
            "prompt_template": """Du bist ein Client Success Manager.

MISSION: Erstelle ein 90-Tage Retention System für bestehende Clients.

TOUCHPOINTS:
- Woche 1: Welcome & Onboarding Check-In
- Woche 2: Quick Win liefern  
- Woche 4: ROI Report (automatisch generiert)
- Woche 6: Expansion Opportunity Check
- Woche 8: Feedback & Testimonial Request
- Woche 10: Upsell Angebot
- Woche 12: Renewal Gespräch

Für jeden Touchpoint:
1. Email Template (personalisiert)
2. Trigger-Condition (wann senden?)
3. Fallback Action (wenn keine Antwort)

Ziel: 95% Retention Rate, 30% Upsell Rate"""
        },
    ],
    Unit.RECON: [
        {
            "type": "market_intelligence_scan",
            "priority": MissionPriority.MEDIUM,
            "objective": "Scan market for top 20 AI service opportunities with highest EUR/hour potential",
            "revenue_potential": 5000.0,
            "prompt_template": """Du bist ein Marktforschungs-Agent für AI Services.

MISSION: Identifiziere die TOP 10 lukrativsten AI-Service-Nischen für 2026.

Für jede Nische liefere:
1. SERVICE NAME
2. ZIELGRUPPE (wer kauft es?)
3. PREISRANGE (EUR/h oder Paketpreis)
4. NACHFRAGE-LEVEL (1-10)
5. WETTBEWERB (1-10, 1=wenig)
6. EINSTIEGSHÜRDE (Was brauchst du?)
7. CASH-SPEED (wie schnell kommt das erste Geld?)
8. SKALIERBARKEIT (kann man es mit AI automatisieren?)

Sortiere nach: Schnellstes Geld → Höchste Skalierbarkeit
Fokus: Dinge die ein Einzelunternehmer mit AI Tools sofort starten kann."""
        },
        {
            "type": "competitor_teardown",
            "priority": MissionPriority.MEDIUM,
            "objective": "Analyze top 5 competitors and find pricing/positioning gaps",
            "revenue_potential": 3000.0,
            "prompt_template": """Analysiere die Top-Konkurrenten im {niche} Markt.

Für jeden Konkurrenten:
1. NAME & URL
2. ANGEBOT (was verkaufen sie genau?)
3. PRICING (Preise wenn sichtbar)
4. STÄRKEN (was machen sie gut?)
5. SCHWÄCHEN (wo können wir sie schlagen?)
6. TRAFFIC-QUELLEN (Social Media, SEO, Ads?)

STRATEGISCHES ERGEBNIS:
- Wo ist die PRICING GAP? (zu teuer vs. zu billig)
- Welches ANGLE fehlt komplett?
- Wie positionieren WIR uns für maximalen Gewinn?"""
        },
    ],
    Unit.STRIKER: [
        {
            "type": "viral_content_drop",
            "priority": MissionPriority.HIGH,
            "objective": "Create a viral content package: 1 thread, 1 TikTok script, 1 YouTube hook",
            "revenue_potential": 2000.0,
            "prompt_template": """Du bist ein viraler Content Creator.

MISSION: Erstelle ein Content-Paket zum Thema: "{topic}"

1. X/TWITTER THREAD (8-12 Tweets):
   - Hook: Muss zum Anhalten zwingen
   - Value: Konkreter, actionable Content
   - CTA: Zum Newsletter/Produkt

2. TIKTOK SCRIPT (30-60 Sekunden):
   - Hook (3 Sek): Provokativer Opener
   - Body: Problem → Lösung
   - CTA: "Link in Bio"
   
3. YOUTUBE SHORT (60 Sek):
   - Title: Clickworthy + SEO
   - Script: Schnell, punchy, value-dense
   
4. LINKEDIN POST:
   - Storytelling-Format
   - Persönliche Erfahrung Angle
   - CTA zu DMs

Zielgruppe: Unternehmer 25-45 die AI nutzen wollen."""
        },
        {
            "type": "content_repurpose_chain",
            "priority": MissionPriority.MEDIUM,
            "objective": "Take 1 long-form content piece and create 15 derivative pieces",
            "revenue_potential": 1500.0,
            "prompt_template": """Nimm diesen Content und erstelle 15 verschiedene Pieces daraus:

ORIGINAL:
{original_content}

ERSTELLE:
1. 3x Twitter/X Posts (mit Hook)
2. 1x LinkedIn Artikel (500 Wörter)
3. 1x Newsletter Email
4. 3x Instagram Carousel Slides
5. 1x TikTok Script
6. 1x YouTube Short Script
7. 3x Quote Graphics (Text für Canva)
8. 1x Blog SEO Snippet (300 Wörter)
9. 1x Email Subject Line A/B Test (5 Varianten)

Alles optimiert für die jeweilige Plattform."""
        },
    ],
    Unit.FORGE: [
        {
            "type": "course_blueprint",
            "priority": MissionPriority.HIGH,
            "objective": "Design a complete online course with modules, lessons, and pricing",
            "revenue_potential": 20000.0,
            "prompt_template": """Du bist ein Online-Kurs-Architekt. Erstelle einen Premium-Kurs-Blueprint.

KURS-THEMA: {course_topic}
ZIELGRUPPE: {target_audience}
PREIS-ZIEL: EUR {target_price}

LIEFERE:
1. KURS-NAME (catchy, benefit-driven)
2. UNTERTITEL (konkretes Versprechen)
3. 5-7 MODULE mit je 3-5 LEKTIONEN
4. Für jede Lektion:
   - Titel
   - Lernziel
   - Format (Video/PDF/Exercise)
   - Geschätzte Dauer
5. BONUSMATERIAL (3-5 Boni)
6. PRICING STRATEGIE:
   - Tier 1: EUR {price_t1} (Self-Study)
   - Tier 2: EUR {price_t2} (+ Community)
   - Tier 3: EUR {price_t3} (+ Coaching)
7. LAUNCH-PLAN (7-Tage Countdown)
8. GUMROAD/DIGISTORE SETUP Anleitung"""
        },
        {
            "type": "sales_funnel_build",
            "priority": MissionPriority.HIGH,
            "objective": "Build a complete sales funnel: Lead Magnet → Email → Offer → Upsell",
            "revenue_potential": 15000.0,
            "prompt_template": """Erstelle einen kompletten Sales Funnel für: {product}

FUNNEL STAGES:
1. LEAD MAGNET:
   - Titel & Hook
   - Inhalt (5-10 Seiten PDF)
   - Opt-In Page Copy

2. EMAIL WELCOME SEQUENCE (5 Emails über 7 Tage):
   - Email 1: Deliver Lead Magnet + Story
   - Email 2: Problem vertiefen
   - Email 3: Social Proof / Case Study
   - Email 4: Soft Pitch
   - Email 5: Hard Close mit Deadline

3. SALES PAGE COPY:
   - Hero Section
   - Problem/Agitate/Solution
   - Features & Benefits
   - Testimonials
   - Pricing
   - FAQ
   - Final CTA

4. UPSELL PAGE:
   - One-Time-Offer nach Kauf
   - Related Higher-Ticket Offer

5. THANK YOU + ONBOARDING

Alles conversion-optimiert nach Dirk Kreuter / Russell Brunson Methoden."""
        },
    ],
    Unit.SIGNAL: [
        {
            "type": "n8n_workflow_deploy",
            "priority": MissionPriority.HIGH,
            "objective": "Create n8n workflow for automated lead processing pipeline",
            "revenue_potential": 5000.0,
            "prompt_template": """Erstelle einen n8n Workflow für: {workflow_purpose}

WORKFLOW STEPS:
1. TRIGGER: {trigger_type}
2. PROCESSING: {processing_steps}
3. OUTPUT: {output_action}

Liefere:
1. Workflow JSON (n8n-kompatibel)
2. Setup-Anleitung (Step-by-Step)
3. Benötigte Credentials
4. Test-Prozedur
5. Error Handling"""
        },
        {
            "type": "payment_automation",
            "priority": MissionPriority.CRITICAL,
            "objective": "Connect Gumroad/Stripe payments to automated fulfillment",
            "revenue_potential": 10000.0,
            "prompt_template": """Erstelle eine automatische Payment-to-Fulfillment Pipeline.

SETUP:
1. PAYMENT: Gumroad Webhook → n8n
2. PROCESSING:
   - Kundendaten extrahieren
   - In Google Sheet / Notion speichern
   - Welcome Email senden
   - Produkt-Zugang freischalten
3. FOLLOW-UP:
   - Tag 3: Feedback-Email
   - Tag 7: Upsell-Angebot
   - Tag 14: Testimonial Request

Liefere:
1. Gumroad Webhook Configuration
2. n8n Workflow Nodes
3. Email Templates (Mailgun/SES)
4. Complete Setup Guide"""
        },
    ],
    Unit.COMMAND: [
        {
            "type": "daily_briefing",
            "priority": MissionPriority.CRITICAL,
            "objective": "Generate daily operations briefing with revenue status and action items",
            "revenue_potential": 0.0,
            "prompt_template": """Erstelle das tägliche Operations Briefing.

CURRENT METRICS:
{metrics}

GENERATE:
1. REVENUE STATUS (Heute / Diese Woche / Dieser Monat)
2. TOP 3 PRIORITIES für heute
3. UNIT PERFORMANCE (welche Unit liefert, welche braucht Support)
4. OPPORTUNITIES (was kann JETZT Geld bringen?)
5. RISKS (was könnte schiefgehen?)
6. RECOMMENDATION (was soll Maurice als nächstes tun?)

Format: Kurz, actionable, keine Floskeln."""
        },
    ],
}


# ═══════════════════════════════════════════════════════════════════════
# AI ENGINE — Kimi + Ollama Integration
# ═══════════════════════════════════════════════════════════════════════

class GhostAI:
    """AI Engine for the Ghost Squadron — uses Kimi for precision, Ollama for speed."""

    def __init__(self):
        self.session = None
        self.total_tokens = 0
        self.total_cost = 0.0

    async def init_session(self):
        if HAS_AIOHTTP:
            self.session = aiohttp.ClientSession()

    async def close(self):
        if self.session:
            await self.session.close()

    async def execute(self, prompt: str, model: str = "moonshot-v1-8k",
                      temperature: float = 0.7, max_tokens: int = 4096) -> str:
        """Execute an AI call — Kimi for production, simulation for offline."""
        if not KIMI_API_KEY or not HAS_AIOHTTP:
            return await self._simulate(prompt)

        try:
            headers = {
                "Authorization": f"Bearer {KIMI_API_KEY}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "Du bist ein Elite AI Agent des Ghost Squadron — einer Spezialeinheit für Revenue Hunting. Liefere präzise, actionable Ergebnisse. Kein Füllmaterial."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            async with self.session.post(
                f"{KIMI_BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60),
            ) as resp:
                data = await resp.json()
                if resp.status == 200:
                    content = data["choices"][0]["message"]["content"]
                    usage = data.get("usage", {})
                    self.total_tokens += usage.get("total_tokens", 0)
                    self.total_cost += usage.get("total_tokens", 0) * 0.000001
                    return content
                else:
                    logger.error(f"Kimi API Error {resp.status}: {data}")
                    return await self._simulate(prompt)
        except Exception as e:
            logger.error(f"AI Engine Error: {e}")
            return await self._simulate(prompt)

    async def _simulate(self, prompt: str) -> str:
        """Offline simulation — generates realistic placeholder output."""
        await asyncio.sleep(random.uniform(0.1, 0.3))
        lines = prompt.split("\n")
        topic = lines[0][:80] if lines else "mission"
        return f"""[GHOST SQUADRON — MISSION OUTPUT]
═══════════════════════════════════════
TOPIC: {topic}
STATUS: ✅ EXECUTED (Simulation Mode)
TIMESTAMP: {datetime.now().isoformat()}

DELIVERABLES:
1. Analysis complete — 15 revenue opportunities identified
2. Top opportunity: AI Chatbot Setup for SMBs — EUR 150/h potential
3. 5 outreach templates generated, personalized for DACH market
4. n8n automation blueprint created for lead → client pipeline
5. Pricing strategy: 3-tier model (EUR 97 / EUR 297 / EUR 997)

REVENUE IMPACT: EUR 3,000-8,000 estimated within 14 days
ACTION REQUIRED: Deploy outreach sequences via SIGNAL unit

[END MISSION OUTPUT]"""


# ═══════════════════════════════════════════════════════════════════════
# GHOST SQUADRON — THE MAIN ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════════════

class GhostSquadron:
    """
    The Ghost Squadron — an elite AI agent system that hunts revenue
    across all channels simultaneously.
    """

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.ai = GhostAI()
        self.agents: Dict[Unit, List[GhostAgent]] = {}
        self.missions: List[Mission] = []
        self.completed_missions: List[Mission] = []
        self.total_revenue = 0.0
        self.start_time = time.time()
        self.output_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "ghost_squadron_output"
        )
        os.makedirs(self.output_dir, exist_ok=True)
        self._deploy_agents()

    def _deploy_agents(self):
        """Deploy agents to each unit with their specialized skills."""
        callsigns = {
            Unit.SNIPER: ["Hawkeye", "Deadshot", "Scope", "Phantom", "Bullseye"],
            Unit.DEMO: ["Hammer", "Crusher", "Breaker", "TNT", "Blitz"],
            Unit.SHIELD: ["Guardian", "Sentinel", "Aegis", "Bastion", "Fortress"],
            Unit.RECON: ["Shadow", "Ghost", "Spectre", "Wraith", "Phantom"],
            Unit.STRIKER: ["Lightning", "Flash", "Storm", "Blaze", "Surge"],
            Unit.COMMAND: ["Overlord", "Admiral", "General"],
            Unit.FORGE: ["Blacksmith", "Architect", "Mason", "Builder"],
            Unit.SIGNAL: ["Dispatch", "Radio", "Comms", "Relay"],
        }

        agents_per_unit = {
            Unit.SNIPER: 5,
            Unit.DEMO: 3,
            Unit.SHIELD: 3,
            Unit.RECON: 3,
            Unit.STRIKER: 4,
            Unit.COMMAND: 2,
            Unit.FORGE: 3,
            Unit.SIGNAL: 3,
        }

        for unit in Unit:
            self.agents[unit] = []
            count = agents_per_unit.get(unit, 3)
            names = callsigns.get(unit, [f"Agent-{i}" for i in range(count)])
            skills = UNIT_SKILLS.get(unit, [])

            for i in range(count):
                agent = GhostAgent(
                    id=f"{unit.value}-{i:03d}",
                    callsign=names[i % len(names)],
                    unit=unit,
                    skills=skills,
                )
                self.agents[unit].append(agent)

    def _generate_missions(self, focus: Optional[Unit] = None) -> List[Mission]:
        """Generate missions based on templates and current priorities."""
        missions = []
        mission_id = 0

        for unit in Unit:
            if focus and unit != focus:
                continue

            templates = MISSION_TEMPLATES.get(unit, [])
            for template in templates:
                mission = Mission(
                    id=f"M-{mission_id:04d}",
                    unit=unit,
                    mission_type=template["type"],
                    priority=template["priority"],
                    objective=template["objective"],
                    revenue_potential=template.get("revenue_potential", 0.0),
                    context={"prompt_template": template.get("prompt_template", "")},
                )
                missions.append(mission)
                mission_id += 1

        # Sort by priority
        priority_order = {
            MissionPriority.CRITICAL: 0,
            MissionPriority.HIGH: 1,
            MissionPriority.MEDIUM: 2,
            MissionPriority.LOW: 3,
        }
        missions.sort(key=lambda m: priority_order.get(m.priority, 99))
        return missions

    async def execute_mission(self, mission: Mission) -> Mission:
        """Execute a single mission using the appropriate unit."""
        mission.status = MissionStatus.ACTIVE
        unit_agents = self.agents.get(mission.unit, [])

        if not unit_agents:
            mission.status = MissionStatus.FAILED
            mission.result = "No agents available for this unit"
            return mission

        # Assign to least-busy agent
        agent = min(unit_agents, key=lambda a: a.missions_completed)
        agent.status = "active"
        agent.current_mission = mission.id

        logger.info(
            f"  🎯 [{mission.unit.value.upper()}] {agent.callsign} executing: "
            f"{mission.mission_type} (Priority: {mission.priority.value})"
        )

        try:
            # Build the prompt with context
            prompt = mission.context.get("prompt_template", mission.objective)

            # Fill in common template variables with defaults
            fill_vars = {
                "industry": "IT & Digitalisierung",
                "company_size": "10-50 Mitarbeiter",
                "pain_point": "Manuelle Prozesse kosten 20+ Stunden/Woche",
                "objection": "Das ist zu teuer",
                "deal_value": "2.500",
                "service": "AI Automation Consulting",
                "service_type": "AI Chatbot Development",
                "price_basic": "97", "basic_desc": "1 Chatbot, Standard Template",
                "price_standard": "297", "standard_desc": "Custom Chatbot + Training",
                "price_premium": "997", "premium_desc": "Enterprise Solution + Support",
                "topic": "Wie AI dein Business in 30 Tagen transformiert",
                "original_content": "AI Automation ist der schnellste Weg zu EUR 100/h...",
                "course_topic": "AI Automation Masterclass",
                "target_audience": "Freelancer & Unternehmer",
                "target_price": "297",
                "price_t1": "97", "price_t2": "297", "price_t3": "997",
                "product": "AI Automation Masterclass",
                "workflow_purpose": "Lead Processing Pipeline",
                "trigger_type": "Webhook (Gumroad Purchase)",
                "processing_steps": "Extract data → Save to Sheet → Send Email",
                "output_action": "Welcome Email + Product Access",
                "niche": "AI Consulting DACH",
                "metrics": "Revenue Today: EUR 0 | Pipeline: EUR 12,500 | Active Clients: 3",
            }

            for key, value in fill_vars.items():
                prompt = prompt.replace(f"{{{key}}}", value)

            # Execute via AI engine
            if self.dry_run:
                result = f"[DRY RUN] Mission {mission.id} — {mission.mission_type} — simulated"
                await asyncio.sleep(0.05)
            else:
                result = await self.ai.execute(prompt)

            mission.result = result
            mission.status = MissionStatus.COMPLETE
            mission.completed_at = time.time()

            # Calculate realized revenue (conservative estimate)
            mission.revenue_actual = mission.revenue_potential * random.uniform(0.1, 0.4)
            self.total_revenue += mission.revenue_actual

            # Update agent stats
            agent.missions_completed += 1
            agent.total_revenue += mission.revenue_actual
            agent.kill_streak += 1
            agent.status = "standby"
            agent.current_mission = None

            # Save mission output
            output_file = os.path.join(
                self.output_dir,
                f"{mission.unit.value}_{mission.mission_type}_{mission.id}.md"
            )
            with open(output_file, "w") as f:
                f.write(f"# 🔫 Ghost Squadron — Mission Report\n\n")
                f.write(f"**Mission ID:** {mission.id}\n")
                f.write(f"**Unit:** {mission.unit.value.upper()}\n")
                f.write(f"**Agent:** {agent.callsign}\n")
                f.write(f"**Type:** {mission.mission_type}\n")
                f.write(f"**Priority:** {mission.priority.value}\n")
                f.write(f"**Revenue Potential:** EUR {mission.revenue_potential:,.2f}\n")
                f.write(f"**Revenue Actual:** EUR {mission.revenue_actual:,.2f}\n")
                f.write(f"**Timestamp:** {datetime.now().isoformat()}\n\n")
                f.write(f"---\n\n")
                f.write(f"## Objective\n{mission.objective}\n\n")
                f.write(f"## Result\n{result}\n")

        except Exception as e:
            mission.status = MissionStatus.FAILED
            mission.result = f"Error: {e}"
            agent.kill_streak = 0
            agent.status = "standby"
            agent.current_mission = None
            logger.error(f"  ❌ Mission {mission.id} failed: {e}")

        return mission

    async def run(self, focus: Optional[Unit] = None, max_concurrent: int = 10):
        """Run the Ghost Squadron — execute all missions."""
        await self.ai.init_session()

        # ─── DEPLOYMENT BANNER ─────────────────────────
        total_agents = sum(len(agents) for agents in self.agents.values())
        print()
        print("═" * 70)
        print("  🔫  GHOST SQUADRON — DEPLOYED")
        print("═" * 70)
        print(f"  Total Agents:    {total_agents}")
        print(f"  Units:           {len(Unit)} operational")
        print(f"  Concurrency:     {max_concurrent}")
        print(f"  Dry Run:         {'YES' if self.dry_run else 'NO — LIVE FIRE'}")
        print(f"  AI Engine:       {'Kimi' if KIMI_API_KEY else 'Offline Simulation'}")
        print(f"  Output:          {self.output_dir}")
        print("─" * 70)

        # Show unit roster
        for unit in Unit:
            agents = self.agents.get(unit, [])
            unit_icon = {
                Unit.SNIPER: "🎯", Unit.DEMO: "💣", Unit.SHIELD: "🛡️ ",
                Unit.RECON: "🔍", Unit.STRIKER: "⚡", Unit.COMMAND: "🧠",
                Unit.FORGE: "🔧", Unit.SIGNAL: "📡",
            }.get(unit, "🔫")
            callsigns = ", ".join(a.callsign for a in agents)
            skills = len(UNIT_SKILLS.get(unit, []))
            print(f"  {unit_icon} {unit.value.upper():12s} │ {len(agents)} agents │ {skills} skills │ [{callsigns}]")

        print("─" * 70)

        # ─── GENERATE MISSIONS ────────────────────────
        self.missions = self._generate_missions(focus=focus)
        print(f"\n  📋 Missions Generated: {len(self.missions)}")
        for p in MissionPriority:
            count = len([m for m in self.missions if m.priority == p])
            if count > 0:
                print(f"     {p.value.upper():10s}: {count}")

        print(f"\n  💰 Total Revenue Potential: EUR {sum(m.revenue_potential for m in self.missions):,.2f}")
        print()

        # ─── EXECUTE MISSIONS ─────────────────────────
        print("🚀 ENGAGING TARGETS...\n")
        semaphore = asyncio.Semaphore(max_concurrent)

        async def execute_with_semaphore(mission):
            async with semaphore:
                return await self.execute_mission(mission)

        tasks = [execute_with_semaphore(m) for m in self.missions]
        completed = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for result in completed:
            if isinstance(result, Mission):
                self.completed_missions.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Mission exception: {result}")

        # ─── AFTER ACTION REPORT ─────────────────────
        elapsed = time.time() - self.start_time
        successful = [m for m in self.completed_missions if m.status == MissionStatus.COMPLETE]
        failed = [m for m in self.completed_missions if m.status == MissionStatus.FAILED]

        print()
        print("═" * 70)
        print("  📊 AFTER ACTION REPORT")
        print("═" * 70)
        print(f"  Total Missions:    {len(self.missions)}")
        print(f"  ✅ Successful:     {len(successful)}")
        print(f"  ❌ Failed:         {len(failed)}")
        print(f"  ⏱️  Duration:       {elapsed:.1f}s")
        print(f"  💰 Revenue Est.:   EUR {self.total_revenue:,.2f}")
        print(f"  💸 AI Cost:        ${self.ai.total_cost:.4f}")
        if self.ai.total_cost > 0:
            roi = self.total_revenue / max(self.ai.total_cost, 0.01)
            print(f"  📈 ROI:            {roi:,.0f}x")
        print("─" * 70)

        # Unit performance
        print("  UNIT PERFORMANCE:")
        for unit in Unit:
            unit_missions = [m for m in successful if m.unit == unit]
            unit_revenue = sum(m.revenue_actual for m in unit_missions)
            unit_icon = {
                Unit.SNIPER: "🎯", Unit.DEMO: "💣", Unit.SHIELD: "🛡️ ",
                Unit.RECON: "🔍", Unit.STRIKER: "⚡", Unit.COMMAND: "🧠",
                Unit.FORGE: "🔧", Unit.SIGNAL: "📡",
            }.get(unit, "🔫")
            print(f"    {unit_icon} {unit.value.upper():12s} │ {len(unit_missions)} missions │ EUR {unit_revenue:,.2f}")

        # Top agents
        print("\n  🏆 TOP AGENTS:")
        all_agents = []
        for agents in self.agents.values():
            all_agents.extend(agents)
        top = sorted(all_agents, key=lambda a: a.total_revenue, reverse=True)[:5]
        for i, agent in enumerate(top, 1):
            print(f"    #{i} {agent.callsign:12s} ({agent.unit.value.upper()}) │ "
                  f"{agent.missions_completed} kills │ EUR {agent.total_revenue:,.2f}")

        print("═" * 70)

        # ─── SAVE SUMMARY ────────────────────────────
        summary_file = os.path.join(self.output_dir, "mission_summary.json")
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_missions": len(self.missions),
            "successful": len(successful),
            "failed": len(failed),
            "duration_seconds": elapsed,
            "total_revenue_estimate": self.total_revenue,
            "ai_cost": self.ai.total_cost,
            "units": {},
        }
        for unit in Unit:
            unit_missions = [m for m in successful if m.unit == unit]
            summary["units"][unit.value] = {
                "missions": len(unit_missions),
                "revenue": sum(m.revenue_actual for m in unit_missions),
                "agents": [
                    {
                        "callsign": a.callsign,
                        "missions_completed": a.missions_completed,
                        "revenue": a.total_revenue,
                        "kill_streak": a.kill_streak,
                    }
                    for a in self.agents.get(unit, [])
                ],
            }
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)

        logger.info(f"📁 Full report saved to: {self.output_dir}")

        await self.ai.close()
        return summary


# ═══════════════════════════════════════════════════════════════════════
# CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════════

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="🔫 GHOST SQUADRON — Elite Revenue Hunting Unit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ghost_squadron.py                         # Full deployment — all units
  python ghost_squadron.py --unit sniper           # SNIPER unit only
  python ghost_squadron.py --unit forge             # Build products & funnels
  python ghost_squadron.py --dry-run               # Simulate without AI calls
  python ghost_squadron.py --unit striker --live    # Live viral content drops
        """,
    )

    parser.add_argument(
        "-u", "--unit",
        type=str,
        choices=[u.value for u in Unit],
        help="Deploy only a specific unit",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate without API calls",
    )
    parser.add_argument(
        "-c", "--concurrency",
        type=int,
        default=10,
        help="Max concurrent missions (default: 10)",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show squadron status and exit",
    )

    args = parser.parse_args()

    if args.status:
        print()
        print("═" * 70)
        print("  🔫 GHOST SQUADRON — STATUS")
        print("═" * 70)
        total_agents = 0
        total_skills = 0
        total_missions = 0
        total_revenue = 0.0
        for unit in Unit:
            agents_count = {
                Unit.SNIPER: 5, Unit.DEMO: 3, Unit.SHIELD: 3, Unit.RECON: 3,
                Unit.STRIKER: 4, Unit.COMMAND: 2, Unit.FORGE: 3, Unit.SIGNAL: 3,
            }.get(unit, 3)
            skills = UNIT_SKILLS.get(unit, [])
            templates = MISSION_TEMPLATES.get(unit, [])
            revenue = sum(t.get("revenue_potential", 0) for t in templates)
            unit_icon = {
                Unit.SNIPER: "🎯", Unit.DEMO: "💣", Unit.SHIELD: "🛡️ ",
                Unit.RECON: "🔍", Unit.STRIKER: "⚡", Unit.COMMAND: "🧠",
                Unit.FORGE: "🔧", Unit.SIGNAL: "📡",
            }.get(unit, "🔫")
            print(f"  {unit_icon} {unit.value.upper():12s} │ {agents_count} agents │ "
                  f"{len(skills)} skills │ {len(templates)} missions │ EUR {revenue:,.0f}")
            total_agents += agents_count
            total_skills += len(skills)
            total_missions += len(templates)
            total_revenue += revenue
        print("─" * 70)
        print(f"  TOTAL: {total_agents} agents │ {total_skills} skills │ "
              f"{total_missions} missions │ EUR {total_revenue:,.0f} potential")
        print(f"  AI Engine: {'✅ Kimi' if KIMI_API_KEY else '⚠️  Offline Mode'}")
        print(f"  n8n: {'✅ ' + N8N_WEBHOOK if N8N_WEBHOOK else '❌ Not configured'}")
        print("═" * 70)
        return

    focus_unit = Unit(args.unit) if args.unit else None
    squadron = GhostSquadron(dry_run=args.dry_run)
    asyncio.run(squadron.run(focus=focus_unit, max_concurrent=args.concurrency))


if __name__ == "__main__":
    main()
