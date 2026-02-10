#!/usr/bin/env python3
"""
DIRK KREUTER SALES ENGINE
Maurice's AI Empire - Scientific Sales Psychology

7 Verkaufsprinzipien automatisiert:
1. VALUE FIRST - ROI vor Preis zeigen
2. ECHTE VERKNAPPUNG - Nur X Slots real
3. SOCIAL PROOF - Testimonials + Case Studies
4. AUTHORITY - AI Automation Expertise
5. COMMITMENT ESCALATION - EUR 0→27→47→79→97→297
6. RECIPROCITY - Gratis-Value zuerst
7. LOSS AVERSION - 30-Tage Garantie
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class SalesPrinciple(Enum):
    VALUE_FIRST = "value_first"
    SCARCITY = "scarcity"
    SOCIAL_PROOF = "social_proof"
    AUTHORITY = "authority"
    COMMITMENT = "commitment"
    RECIPROCITY = "reciprocity"
    LOSS_AVERSION = "loss_aversion"


@dataclass
class SalesMessage:
    """Generated sales message"""
    principle: SalesPrinciple
    headline: str
    body: str
    cta: str
    urgency_level: int  # 0-100


class DirkKreuterEngine:
    """
    Automatisierte Verkaufspsychologie nach Dirk Kreuter
    Ethical marketing - keine Dark Patterns
    """
    
    def __init__(self):
        self.products = {
            "prompt_cheatsheet": {"name": "Prompt Cheatsheet Pro", "price": 27, "value": "3h Arbeit gespart/Tag"},
            "agent_starter": {"name": "AI Agent Starter Kit", "price": 47, "value": "Dein erster Agent in 30 Min"},
            "automation_bp": {"name": "AI Automation Blueprint", "price": 79, "value": "15h Arbeit gespart/Woche"},
            "side_hustle": {"name": "AI Side Hustle Playbook", "price": 97, "value": "Erster AI-Umsatz in 7 Tagen"},
            "consulting_call": {"name": "1:1 AI Setup Call", "price": 297, "value": "Done-for-you Agent Setup"},
        }
        
        # Real scarcity limits
        self.slot_limits = {
            "consulting_call": 5,  # Only 5 consulting slots per month
        }
        
        self.testimonials = [
            {"name": "Stefan M.", "company": "E-Commerce GmbH", "result": "15h/Woche gespart", "rating": 5},
            {"name": "Julia K.", "company": "Marketing Agentur", "result": "ROI 400% in 30 Tagen", "rating": 5},
            {"name": "Marcus T.", "company": "SaaS Startup", "result": "3 Mitarbeiter durch AI ersetzt", "rating": 5},
        ]
    
    # =========================================================================
    # PRINCIPLE 1: VALUE FIRST
    # =========================================================================
    
    def generate_value_message(self, product_key: str) -> SalesMessage:
        """Zeige ROI bevor Preis genannt wird"""
        product = self.products.get(product_key, self.products["automation_bp"])
        
        return SalesMessage(
            principle=SalesPrinciple.VALUE_FIRST,
            headline=f"Spare {product['value']} - jeden Tag, automatisch",
            body=f"""Was wäre es wert, wenn du nie wieder manuelle Reports erstellen müsstest?
            
Stell dir vor: Du kommst morgens ins Büro und alles ist bereits erledigt.
- Kundenanfragen: ✅ Beantwortet
- Reports: ✅ Erstellt
- Follow-ups: ✅ Gesendet

Das ist keine Zukunft. Das ist {product['name']}.""",
            cta=f"Jetzt {product['value']} freischalten →",
            urgency_level=40
        )
    
    # =========================================================================
    # PRINCIPLE 2: ECHTE VERKNAPPUNG (No Fake!)
    # =========================================================================
    
    def generate_scarcity_message(self, product_key: str, slots_taken: int) -> SalesMessage:
        """Echte Verknappung - nur wenn wirklich limitiert"""
        if product_key not in self.slot_limits:
            return self.generate_value_message(product_key)
        
        total_slots = self.slot_limits[product_key]
        remaining = total_slots - slots_taken
        
        if remaining <= 0:
            headline = "Ausgebucht - Warteliste öffnet nächsten Monat"
            urgency = 0
        elif remaining <= 2:
            headline = f"Nur noch {remaining} Plätze diesen Monat"
            urgency = 95
        else:
            headline = f"Noch {remaining} von {total_slots} Plätzen verfügbar"
            urgency = 60
        
        return SalesMessage(
            principle=SalesPrinciple.SCARCITY,
            headline=headline,
            body=f"""Ich kann nur {total_slots} Kunden pro Monat persönlich betreuen.

Warum? Weil ich jedem Kunden 100% Aufmerksamkeit schenke.
Keine Templates. Keine Massenfertigung. Echte 1:1 Betreuung.

Diesen Monat sind bereits {slots_taken} Plätze vergeben.""",
            cta="Platz sichern (bevor ausgebucht)" if remaining > 0 else "Auf Warteliste setzen",
            urgency_level=urgency
        )
    
    # =========================================================================
    # PRINCIPLE 3: SOCIAL PROOF
    # =========================================================================
    
    def generate_social_proof_message(self) -> SalesMessage:
        """Echte Testimonials und Case Studies"""
        testimonial = self.testimonials[0]  # Best one first
        
        return SalesMessage(
            principle=SalesPrinciple.SOCIAL_PROOF,
            headline=f'"{testimonial["result"]}" - {testimonial["name"]}, {testimonial["company"]}',
            body=f"""Was andere Unternehmer erreicht haben:

⭐⭐⭐⭐⭐ {testimonial['name']} ({testimonial['company']}):
"{testimonial['result']}"

Und das innerhalb von 30 Tagen nach der Implementierung.

Du kannst die gleichen Ergebnisse erreichen.""",
            cta="Meine Ergebnisse erzielen →",
            urgency_level=50
        )
    
    # =========================================================================
    # PRINCIPLE 4: AUTHORITY
    # =========================================================================
    
    def generate_authority_message(self) -> SalesMessage:
        """AI Automation Expertise"""
        return SalesMessage(
            principle=SalesPrinciple.AUTHORITY,
            headline="100+ AI Agents im Einsatz — täglich",
            body="""Mein System automatisiert alles mit KI.

Meine Ergebnisse:
- 100+ AI Agents aktiv
- 40+ Stunden/Woche automatisiert
- Von Content bis Vertrieb — alles auf Autopilot

Keine Theorie. Echte Ergebnisse aus 100+ Agents.""",
            cta="Von echten AI-Ergebnissen profitieren →",
            urgency_level=35
        )
    
    # =========================================================================
    # PRINCIPLE 5: COMMITMENT ESCALATION
    # =========================================================================
    
    def get_tripwire_sequence(self) -> List[Dict[str, Any]]:
        """EUR 0 → 27 → 47 → 79 → 97 → 297 Tripwire"""
        return [
            {"step": 1, "price": 0, "product": "Free AI Audit", "next_offer": "prompt_cheatsheet"},
            {"step": 2, "price": 27, "product": "Prompt Cheatsheet Pro", "next_offer": "agent_starter"},
            {"step": 3, "price": 47, "product": "AI Agent Starter Kit", "next_offer": "automation_bp"},
            {"step": 4, "price": 79, "product": "AI Automation Blueprint", "next_offer": "side_hustle"},
            {"step": 5, "price": 97, "product": "AI Side Hustle Playbook", "next_offer": "consulting_call"},
            {"step": 6, "price": 297, "product": "1:1 AI Setup Call", "next_offer": None},
        ]
    
    # =========================================================================
    # PRINCIPLE 6: RECIPROCITY
    # =========================================================================
    
    def generate_reciprocity_message(self) -> SalesMessage:
        """Gratis Value zuerst geben"""
        return SalesMessage(
            principle=SalesPrinciple.RECIPROCITY,
            headline="3 Gratis Automations für dein Business",
            body="""Bevor du irgendetwas kaufst, bekommst du von mir:

🎁 Automation 1: Email-Sortierer (spart 2h/Woche)
🎁 Automation 2: Meeting-Zusammenfasser (spart 3h/Woche)
🎁 Automation 3: Social Media Scheduler (spart 4h/Woche)

Komplett kostenlos. Kein Haken. Du behältst sie für immer.""",
            cta="3 Gratis Automations abholen →",
            urgency_level=20
        )
    
    # =========================================================================
    # PRINCIPLE 7: LOSS AVERSION
    # =========================================================================
    
    def generate_guarantee_message(self, product_key: str) -> SalesMessage:
        """30-Tage Geld-zurück Garantie"""
        product = self.products.get(product_key, self.products["automation_bp"])
        
        return SalesMessage(
            principle=SalesPrinciple.LOSS_AVERSION,
            headline="30 Tage testen - oder Geld zurück",
            body=f"""Du gehst NULL Risiko ein.

Teste {product['name']} 30 Tage lang. Wenn du nicht mindestens 
{product['value']} erreichst, bekommst du jeden Cent zurück.

Keine Fragen. Keine Ausreden. Sofortige Erstattung.

Das Risiko liegt komplett bei mir.""",
            cta="Risikofrei testen →",
            urgency_level=25
        )
    
    # =========================================================================
    # COMPLETE SALES SEQUENCE
    # =========================================================================
    
    def generate_complete_sequence(self, product_key: str, slots_taken: int = 0) -> List[SalesMessage]:
        """Vollständige Verkaufssequenz für ein Produkt"""
        return [
            self.generate_reciprocity_message(),      # 1. Give first
            self.generate_value_message(product_key), # 2. Show value
            self.generate_authority_message(),         # 3. Build trust
            self.generate_social_proof_message(),      # 4. Prove it works
            self.generate_scarcity_message(product_key, slots_taken),  # 5. Create urgency
            self.generate_guarantee_message(product_key),  # 6. Remove risk
        ]
    
    def to_json(self, message: SalesMessage) -> Dict[str, Any]:
        """Convert SalesMessage to JSON"""
        return {
            "principle": message.principle.value,
            "headline": message.headline,
            "body": message.body,
            "cta": message.cta,
            "urgency_level": message.urgency_level,
        }


async def main():
    """Demo Dirk Kreuter Engine"""
    engine = DirkKreuterEngine()
    
    print("="*60)
    print("DIRK KREUTER SALES ENGINE - DEMO")
    print("="*60)
    
    # Generate complete sequence for core product
    sequence = engine.generate_complete_sequence("automation_bp", slots_taken=0)
    
    for i, msg in enumerate(sequence, 1):
        print(f"\n--- Message {i}: {msg.principle.value.upper()} ---")
        print(f"Headline: {msg.headline}")
        print(f"Urgency: {msg.urgency_level}/100")
        print(f"CTA: {msg.cta}")
    
    # Show tripwire
    print("\n" + "="*60)
    print("TRIPWIRE SEQUENCE")
    print("="*60)
    for step in engine.get_tripwire_sequence():
        print(f"Step {step['step']}: EUR {step['price']:,} - {step['product']}")


if __name__ == "__main__":
    asyncio.run(main())
