import pytest
from empire_nucleus import Brain, BrainCell

class TestBrain:
    def test_brain_cell_initialization(self):
        cell = BrainCell(name="risk", weight=0.8)
        assert cell.name == "risk"
        assert cell.weight == 0.8

    def test_brain_cell_evaluate_default(self):
        cell = BrainCell()
        result = cell.evaluate({})
        assert result["score"] == 50
        assert result["signal"] == "neutral"

    def test_brain_initialization(self):
        brain = Brain()
        assert len(brain.cells) == 8
        assert "ceo" in brain.cells
        assert "risk" in brain.cells

    def test_brain_decide_safe_mode(self):
        brain = Brain()
        context = {"risk_level": "high"}
        decision = brain.decide(context)
        assert "action" in decision
        assert "confidence" in decision
        assert isinstance(decision["confidence"], float)

    def test_brain_decide_aggressive_mode(self):
        brain = Brain()
        context = {"opportunity": "massive_growth"}
        decision = brain.decide(context)
        # Should persist keys, logic dependent on LLM or heuristic
        assert "action" in decision
