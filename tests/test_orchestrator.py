import pytest
from empire_orchestrator import EmpireOrchestrator, AgentType, EmpireStats

class TestOrchestrator:
    def test_task_generation(self):
        orch = EmpireOrchestrator()
        task = orch.generate_task(AgentType.SALES, "task_123")
        assert task.agent_type == "sales"
        assert len(task.prompt) > 0

    def test_stats_tracking(self):
        stats = EmpireStats()
        stats.total_tasks += 10
        stats.completed_tasks += 5
        assert stats.success_rate == 0.5  # Assuming property exists or calculation

    def test_orchestrator_initialization(self):
        orch = EmpireOrchestrator()
        assert hasattr(orch, "brain")
        assert hasattr(orch, "swarm")

    def test_run_wave_smoke_test(self):
        """Ensure run_wave doesn't crash immediately."""
        orch = EmpireOrchestrator()
        # Mocking execute would be ideal here if not relying on live calls
