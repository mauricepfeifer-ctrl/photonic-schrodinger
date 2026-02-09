#!/usr/bin/env python3
"""
💰 STRIPE MANAGER — Payment Processing for AI Imperium

Handles:
- Product catalog (all landing pages)
- Checkout session creation
- Webhook processing for payment events
- Revenue tracking integration

Setup:
    pip install stripe
    export STRIPE_SECRET_KEY=sk_test_...
    export STRIPE_WEBHOOK_SECRET=whsec_...
"""

import os
import json
import time
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from datetime import datetime

try:
    import stripe
except ImportError:
    stripe = None  # type: ignore

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("StripeManager")


# ─── PRODUCT CATALOG ────────────────────────────────
@dataclass
class Product:
    """A product in the AI Imperium catalog."""
    product_id: str
    name: str
    description: str
    price_cents: int  # Price in cents (EUR)
    currency: str = "eur"
    landing_url: str = ""
    stripe_price_id: Optional[str] = None  # Set after Stripe sync
    stripe_product_id: Optional[str] = None
    category: str = "digital"  # digital, consulting, software


PRODUCTS: Dict[str, Product] = {
    "bma_starter": Product(
        product_id="bma_starter",
        name="BMA Consulting – Starter",
        description="Normprüfung für Brandmeldeanlagen nach DIN 14675",
        price_cents=19700,
        landing_url="https://mauricepfeifer-ctrl.github.io/photonic-schrodinger/consulting/",
        category="consulting",
    ),
    "ai_consulting": Product(
        product_id="ai_consulting",
        name="AI Consulting – Sprint",
        description="KI-Automatisierung für Geschäftsprozesse – 2h Deep Dive",
        price_cents=29700,
        landing_url="https://mauricepfeifer-ctrl.github.io/photonic-schrodinger/ai-consulting/",
        category="consulting",
    ),
    "file_cleaner": Product(
        product_id="file_cleaner",
        name="File Cleaner Pro",
        description="KI-gestützte Dateiorganisation – 10.000+ Dateien in 30 Minuten",
        price_cents=4700,
        landing_url="https://mauricepfeifer-ctrl.github.io/photonic-schrodinger/file-cleaner/",
        category="software",
    ),
    "prompt_starter": Product(
        product_id="prompt_starter",
        name="Prompt Masterclass – Video-Kurs",
        description="3h Masterclass: Zero-Shot, Few-Shot, Chain-of-Thought + 50 Templates",
        price_cents=6700,
        category="digital",
    ),
    "prompt_pro": Product(
        product_id="prompt_pro",
        name="Prompt Masterclass – Workshop",
        description="Videokurs + 2h Live-Workshop mit persönlichem Feedback",
        price_cents=19700,
        category="digital",
    ),
    "prompt_vip": Product(
        product_id="prompt_vip",
        name="Prompt Masterclass – VIP Coaching",
        description="3x 1:1 Coaching + Custom Prompt-Library + 90 Tage Support",
        price_cents=49700,
        category="digital",
    ),
}


# ─── REVENUE TRACKER ────────────────────────────────
@dataclass
class PaymentRecord:
    """Single payment record."""
    payment_id: str
    product_id: str
    amount_cents: int
    currency: str
    customer_email: str
    status: str  # completed, refunded, failed
    timestamp: str = ""
    stripe_session_id: str = ""

    def amount_eur(self) -> float:
        return self.amount_cents / 100.0


@dataclass
class RevenueStats:
    """Aggregated revenue statistics."""
    total_revenue_cents: int = 0
    total_transactions: int = 0
    refunds: int = 0
    by_product: Dict[str, int] = field(default_factory=dict)
    by_category: Dict[str, int] = field(default_factory=dict)
    last_payment: Optional[str] = None

    def total_eur(self) -> float:
        return self.total_revenue_cents / 100.0


REVENUE_FILE = "revenue_log.json"


class StripeManager:
    """
    Stripe Payment Manager for AI Imperium.

    Handles product sync, checkout creation, and webhook processing.
    Falls back to simulation mode if stripe package not installed.
    """

    def __init__(self) -> None:
        self.secret_key = os.getenv("STRIPE_SECRET_KEY", "")
        self.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")
        self.currency = os.getenv("STRIPE_CURRENCY", "eur")
        self.products = PRODUCTS
        self.stats = RevenueStats()
        self.payments: List[PaymentRecord] = []
        self.bus = None  # Redis bus, injected externally

        if stripe and self.secret_key:
            stripe.api_key = self.secret_key
            self.live = True
            logger.info("💳 Stripe LIVE mode — connected")
        else:
            self.live = False
            if not stripe:
                logger.warning("⚠️ stripe package not installed (pip install stripe)")
            else:
                logger.warning("⚠️ STRIPE_SECRET_KEY not set — simulation mode")

        self._load_revenue()

    # ─── PRODUCT SYNC ────────────────────────────────

    def sync_products(self) -> Dict[str, str]:
        """Sync local product catalog to Stripe. Returns {product_id: stripe_price_id}."""
        if not self.live:
            logger.info("📋 [SIM] Would sync products to Stripe")
            return {}

        synced = {}
        for pid, product in self.products.items():
            try:
                # Create or find product
                sp = stripe.Product.create(
                    name=product.name,
                    description=product.description,
                    metadata={"imperium_id": pid, "category": product.category},
                )
                product.stripe_product_id = sp.id

                # Create price
                price = stripe.Price.create(
                    product=sp.id,
                    unit_amount=product.price_cents,
                    currency=product.currency,
                )
                product.stripe_price_id = price.id
                synced[pid] = price.id
                logger.info(f"  ✅ {product.name} → {price.id}")

            except Exception as e:
                logger.error(f"  ❌ {product.name}: {e}")

        return synced

    # ─── CHECKOUT ─────────────────────────────────────

    def create_checkout_url(
        self,
        product_id: str,
        customer_email: Optional[str] = None,
        success_url: str = "https://mauricepfeifer-ctrl.github.io/photonic-schrodinger/?success=true",
        cancel_url: str = "https://mauricepfeifer-ctrl.github.io/photonic-schrodinger/?canceled=true",
    ) -> Optional[str]:
        """Create a Stripe Checkout Session and return the URL."""
        product = self.products.get(product_id)
        if not product:
            logger.error(f"❌ Unknown product: {product_id}")
            return None

        if not self.live:
            sim_url = f"https://checkout.stripe.com/sim/{product_id}?amount={product.price_cents}"
            logger.info(f"📋 [SIM] Checkout URL: {sim_url}")
            return sim_url

        try:
            params: Dict[str, Any] = {
                "payment_method_types": ["card"],
                "line_items": [{
                    "price_data": {
                        "currency": product.currency,
                        "product_data": {
                            "name": product.name,
                            "description": product.description,
                        },
                        "unit_amount": product.price_cents,
                    },
                    "quantity": 1,
                }],
                "mode": "payment",
                "success_url": success_url,
                "cancel_url": cancel_url,
                "metadata": {"imperium_product_id": product_id},
            }
            if customer_email:
                params["customer_email"] = customer_email

            session = stripe.checkout.Session.create(**params)
            logger.info(f"💳 Checkout created: {product.name} → {session.url}")
            return session.url

        except Exception as e:
            logger.error(f"❌ Checkout creation failed: {e}")
            return None

    # ─── WEBHOOK PROCESSING ──────────────────────────

    def handle_webhook(self, payload: bytes, sig_header: str) -> Dict[str, Any]:
        """
        Process incoming Stripe webhook event.
        Returns event data dict.
        """
        if not self.live:
            return {"status": "simulation", "message": "Stripe not connected"}

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.webhook_secret
            )
        except stripe.error.SignatureVerificationError:  # type: ignore
            logger.error("❌ Webhook signature verification failed")
            return {"status": "error", "message": "Invalid signature"}
        except Exception as e:
            logger.error(f"❌ Webhook processing error: {e}")
            return {"status": "error", "message": str(e)}

        # Handle checkout.session.completed
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            return self._process_payment(session)

        # Handle charge.refunded
        elif event["type"] == "charge.refunded":
            charge = event["data"]["object"]
            return self._process_refund(charge)

        return {"status": "ignored", "type": event["type"]}

    def _process_payment(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Process a completed payment."""
        product_id = (session.get("metadata") or {}).get("imperium_product_id", "unknown")
        amount = session.get("amount_total", 0)
        currency = session.get("currency", "eur")
        email = session.get("customer_email", "unknown")

        record = PaymentRecord(
            payment_id=session.get("id", f"pay_{int(time.time())}"),
            product_id=product_id,
            amount_cents=amount,
            currency=currency,
            customer_email=email,
            status="completed",
            timestamp=datetime.now().isoformat(),
            stripe_session_id=session.get("id", ""),
        )

        self.payments.append(record)
        self._update_stats(record)
        self._save_revenue()

        product_name = self.products.get(product_id, Product(
            product_id=product_id, name=product_id,
            description="", price_cents=amount
        )).name

        # Publish to Redis bus
        event_data = {
            "type": "payment_completed",
            "product": product_name,
            "amount_eur": record.amount_eur(),
            "customer": email,
            "timestamp": record.timestamp,
        }

        if self.bus:
            self.bus.publish("business/payment", event_data)
            self.bus.publish("business/revenue", {
                "amount": record.amount_eur(),
                "currency": currency,
                "total": self.stats.total_eur(),
            })

        logger.info(f"💰 PAYMENT: €{record.amount_eur():.2f} for {product_name} from {email}")
        return {"status": "success", **event_data}

    def _process_refund(self, charge: Dict[str, Any]) -> Dict[str, Any]:
        """Process a refund."""
        amount = charge.get("amount_refunded", 0)
        self.stats.refunds += 1
        self.stats.total_revenue_cents -= amount
        self._save_revenue()

        event_data = {
            "type": "refund",
            "amount_eur": amount / 100.0,
            "timestamp": datetime.now().isoformat(),
        }

        if self.bus:
            self.bus.publish("business/refund", event_data)

        logger.info(f"🔄 REFUND: €{amount / 100.0:.2f}")
        return {"status": "refunded", **event_data}

    # ─── STATS ───────────────────────────────────────

    def _update_stats(self, record: PaymentRecord) -> None:
        """Update aggregated stats."""
        self.stats.total_revenue_cents += record.amount_cents
        self.stats.total_transactions += 1
        self.stats.last_payment = record.timestamp

        # By product
        self.stats.by_product[record.product_id] = (
            self.stats.by_product.get(record.product_id, 0) + record.amount_cents
        )

        # By category
        product = self.products.get(record.product_id)
        if product:
            cat = product.category
            self.stats.by_category[cat] = (
                self.stats.by_category.get(cat, 0) + record.amount_cents
            )

    def get_revenue_stats(self) -> Dict[str, Any]:
        """Get current revenue stats as dict."""
        return {
            "total_eur": self.stats.total_eur(),
            "transactions": self.stats.total_transactions,
            "refunds": self.stats.refunds,
            "by_product": {
                pid: cents / 100.0 for pid, cents in self.stats.by_product.items()
            },
            "by_category": {
                cat: cents / 100.0 for cat, cents in self.stats.by_category.items()
            },
            "last_payment": self.stats.last_payment,
        }

    def get_revenue_summary(self) -> str:
        """Pretty-print revenue summary for Telegram."""
        s = self.stats
        lines = [
            "💰 REVENUE DASHBOARD",
            "═" * 30,
            f"Total: €{s.total_eur():.2f}",
            f"Transactions: {s.total_transactions}",
            f"Refunds: {s.refunds}",
        ]

        if s.by_product:
            lines.append("\n📦 By Product:")
            for pid, cents in sorted(s.by_product.items(), key=lambda x: -x[1]):
                name = self.products.get(pid, Product(
                    product_id=pid, name=pid, description="", price_cents=0
                )).name
                lines.append(f"  {name}: €{cents / 100:.2f}")

        if s.by_category:
            lines.append("\n📊 By Category:")
            for cat, cents in sorted(s.by_category.items(), key=lambda x: -x[1]):
                lines.append(f"  {cat}: €{cents / 100:.2f}")

        if s.last_payment:
            lines.append(f"\n🕐 Last: {s.last_payment}")

        return "\n".join(lines)

    # ─── PERSISTENCE ─────────────────────────────────

    def _load_revenue(self) -> None:
        """Load revenue history from file."""
        try:
            if os.path.exists(REVENUE_FILE):
                with open(REVENUE_FILE, "r") as f:
                    data = json.load(f)
                self.stats.total_revenue_cents = data.get("total_revenue_cents", 0)
                self.stats.total_transactions = data.get("total_transactions", 0)
                self.stats.refunds = data.get("refunds", 0)
                self.stats.by_product = data.get("by_product", {})
                self.stats.by_category = data.get("by_category", {})
                self.stats.last_payment = data.get("last_payment")

                for p in data.get("payments", []):
                    self.payments.append(PaymentRecord(**p))

                logger.info(f"📂 Loaded revenue: €{self.stats.total_eur():.2f} from {len(self.payments)} payments")
        except Exception as e:
            logger.warning(f"⚠️ Could not load revenue data: {e}")

    def _save_revenue(self) -> None:
        """Save revenue history to file."""
        try:
            data = {
                "total_revenue_cents": self.stats.total_revenue_cents,
                "total_transactions": self.stats.total_transactions,
                "refunds": self.stats.refunds,
                "by_product": self.stats.by_product,
                "by_category": self.stats.by_category,
                "last_payment": self.stats.last_payment,
                "payments": [asdict(p) for p in self.payments[-100:]],  # Keep last 100
            }
            with open(REVENUE_FILE, "w") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"❌ Could not save revenue data: {e}")


# ─── STANDALONE TEST ──────────────────────────────────
def main() -> None:
    """Test the Stripe Manager."""
    print("=" * 60)
    print("💳 STRIPE MANAGER — TEST")
    print("=" * 60)

    sm = StripeManager()

    # Show product catalog
    print(f"\n📦 Product Catalog ({len(sm.products)} products):")
    for pid, p in sm.products.items():
        print(f"  {p.name}: €{p.price_cents / 100:.2f} [{p.category}]")

    # Simulate checkout
    print("\n🔗 Generating checkout URLs:")
    for pid in ["bma_starter", "prompt_pro", "file_cleaner"]:
        url = sm.create_checkout_url(pid, customer_email="test@example.com")
        print(f"  {pid}: {url}")

    # Simulate payment
    print("\n💰 Simulating payment...")
    sm._process_payment({
        "id": "cs_test_demo",
        "metadata": {"imperium_product_id": "prompt_pro"},
        "amount_total": 19700,
        "currency": "eur",
        "customer_email": "demo@customer.com",
    })

    # Show stats
    print(f"\n{sm.get_revenue_summary()}")


if __name__ == "__main__":
    main()
