"""Own one coordinator per application process, including concurrent first requests."""

from threading import Lock

_lock = Lock()
_coordinator = None


def get_orchestrator():
    global _coordinator
    with _lock:
        if _coordinator is None:
            from app.orchestration.orchestration import Orchestrator
            _coordinator = Orchestrator()
        return _coordinator


def close_orchestrator():
    global _coordinator
    with _lock:
        if _coordinator is not None:
            _coordinator.executor.close()
            _coordinator = None
