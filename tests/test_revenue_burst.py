import pytest
from revenue_burst import RevenueBurst

class TestRevenueBurst:
    def test_strip_html(self):
        burst = RevenueBurst()
        dirty = "<p>Clean me</p><br/>"
        clean = burst._strip_html(dirty)
        assert clean == "Clean me "

    def test_gig_processing_logic(self):
        gig = {
            "title": "Build AI Chatbot",
            "description": "Need Python expert",
            "budget": "$500",
            "platform": "Upwork"
        }
        burst = RevenueBurst()
        proposal = burst._template_proposal(gig)
        assert "Build AI Chatbot" in proposal
        assert "500" in proposal

    def test_generate_proposal_offline(self):
        """Should fall back to template in offline/simulation mode."""
        burst = RevenueBurst()
        gig = {"title": "Test Gig", "description": "Test Desc", "budget": "$100", "platform": "Upwork"}
        proposal = burst.generate_proposal(gig)
        assert len(proposal) > 10
        assert "Test Gig" in proposal
