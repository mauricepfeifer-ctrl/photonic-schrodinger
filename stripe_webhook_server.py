#!/usr/bin/env python3
"""
🌐 STRIPE WEBHOOK SERVER — HTTP Endpoint for Stripe Events

Lightweight aiohttp server that:
- Receives Stripe webhook events (POST /stripe/webhook)
- Exposes revenue stats API (GET /stripe/stats)
- Publishes payment events to Redis bus
- Sends Telegram notifications on purchase

Usage:
    python stripe_webhook_server.py
    # Then: stripe listen --forward-to localhost:8080/stripe/webhook

Port: 8080 (or WEBHOOK_PORT env var)
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict

from aiohttp import web

from stripe_manager import StripeManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("WebhookServer")

PORT = int(os.getenv("WEBHOOK_PORT", "8080"))


class WebhookServer:
    """HTTP server for Stripe webhooks and revenue API."""

    def __init__(self) -> None:
        self.stripe_mgr = StripeManager()
        self.app = web.Application()
        self._setup_routes()

        # Try to connect Redis bus
        try:
            from redis_bus import RedisBus
            bus = RedisBus()
            if bus.connect():
                self.stripe_mgr.bus = bus
                logger.info("✅ Redis connected for event publishing")
            else:
                logger.warning("⚠️ Redis not available, running standalone")
        except Exception:
            logger.warning("⚠️ Redis not available, running standalone")

    def _setup_routes(self) -> None:
        self.app.router.add_post("/stripe/webhook", self.handle_webhook)
        self.app.router.add_get("/stripe/stats", self.handle_stats)
        self.app.router.add_get("/stripe/products", self.handle_products)
        self.app.router.add_post("/stripe/checkout", self.handle_create_checkout)
        self.app.router.add_get("/health", self.handle_health)

    # ─── WEBHOOK ──────────────────────────────────────

    async def handle_webhook(self, request: web.Request) -> web.Response:
        """Handle incoming Stripe webhook event."""
        payload = await request.read()
        sig_header = request.headers.get("Stripe-Signature", "")

        result = self.stripe_mgr.handle_webhook(payload, sig_header)

        if result.get("status") == "error":
            return web.json_response(result, status=400)

        # Send Telegram notification for successful payments
        if result.get("type") == "payment_completed":
            await self._notify_telegram(result)

        return web.json_response(result)

    # ─── STATS API ────────────────────────────────────

    async def handle_stats(self, request: web.Request) -> web.Response:
        """Return current revenue statistics."""
        stats = self.stripe_mgr.get_revenue_stats()
        return web.json_response(stats)

    # ─── PRODUCTS API ─────────────────────────────────

    async def handle_products(self, request: web.Request) -> web.Response:
        """Return product catalog."""
        products = {}
        for pid, p in self.stripe_mgr.products.items():
            products[pid] = {
                "name": p.name,
                "description": p.description,
                "price_eur": p.price_cents / 100.0,
                "category": p.category,
                "landing_url": p.landing_url,
            }
        return web.json_response(products)

    # ─── CHECKOUT API ─────────────────────────────────

    async def handle_create_checkout(self, request: web.Request) -> web.Response:
        """Create a checkout session. Body: {"product_id": "...", "email": "..."}"""
        try:
            data = await request.json()
        except Exception:
            return web.json_response({"error": "Invalid JSON"}, status=400)

        product_id = data.get("product_id")
        email = data.get("email")

        if not product_id:
            return web.json_response({"error": "product_id required"}, status=400)

        url = self.stripe_mgr.create_checkout_url(product_id, customer_email=email)
        if url:
            return web.json_response({"checkout_url": url})
        return web.json_response({"error": "Could not create checkout"}, status=500)

    # ─── HEALTH ───────────────────────────────────────

    async def handle_health(self, request: web.Request) -> web.Response:
        """Health check endpoint."""
        stats = self.stripe_mgr.get_revenue_stats()
        return web.json_response({
            "status": "healthy",
            "stripe_live": self.stripe_mgr.live,
            "total_revenue_eur": stats["total_eur"],
            "transactions": stats["transactions"],
        })

    # ─── TELEGRAM NOTIFICATION ────────────────────────

    async def _notify_telegram(self, event: Dict[str, Any]) -> None:
        """Send Telegram notification for payment events."""
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        user_id = os.getenv("TELEGRAM_USER_ID")

        if not token or not user_id:
            return

        text = (
            f"🎉 NEUER KAUF!\n\n"
            f"📦 {event.get('product', 'Unknown')}\n"
            f"💰 €{event.get('amount_eur', 0):.2f}\n"
            f"📧 {event.get('customer', 'Unknown')}\n"
            f"🕐 {event.get('timestamp', '')}\n\n"
            f"Total Revenue: €{self.stripe_mgr.stats.total_eur():.2f}"
        )

        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                await session.post(
                    f"https://api.telegram.org/bot{token}/sendMessage",
                    json={"chat_id": user_id, "text": text, "parse_mode": "HTML"},
                )
        except Exception as e:
            logger.error(f"❌ Telegram notification failed: {e}")

    def run(self) -> None:
        """Start the webhook server."""
        logger.info(f"🌐 Webhook Server starting on port {PORT}")
        logger.info(f"   POST /stripe/webhook  — Stripe events")
        logger.info(f"   GET  /stripe/stats    — Revenue dashboard")
        logger.info(f"   GET  /stripe/products — Product catalog")
        logger.info(f"   POST /stripe/checkout — Create checkout")
        logger.info(f"   GET  /health          — Health check")
        web.run_app(self.app, port=PORT)


if __name__ == "__main__":
    server = WebhookServer()
    server.run()
