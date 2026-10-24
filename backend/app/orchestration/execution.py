"""Compatibility interface for callers that already hold a routing decision."""

from app.orchestration.service import get_orchestrator


def execute_decision(decision):
    coordinator = get_orchestrator()
    yield from coordinator.stream(coordinator.from_decision(decision))
