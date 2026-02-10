import pytest
from stripe_manager import StripeManager, Product, PaymentRecord, RevenueStats

class TestStripeManager:
    def test_product_dataclass(self):
        p = Product(product_id="test_1", name="Test Product", price_cents=1000)
        assert p.currency == "eur"
        assert p.category == "digital"

    def test_payment_record_conversion(self):
        record = PaymentRecord(
            payment_id="pay_1",
            product_id="prod_1",
            amount_cents=5050,
            currency="eur",
            customer_email="test@example.com",
            status="succeeded"
        )
        assert record.amount_eur() == 50.50

    def test_revenue_stats_aggregation(self):
        stats = RevenueStats()
        stats.total_revenue_cents = 10000
        assert stats.total_eur() == 100.00

    def test_manager_simulation_mode(self, mock_env):
        """Test manager initialization without real Stripe key (simulation)."""
        manager = StripeManager()
        # Should not crash, but log warning
        assert hasattr(manager, "products")
