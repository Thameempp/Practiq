"""Share provider capacity across summaries using the same client and model."""

from threading import Lock
import time
from weakref import WeakKeyDictionary

from app.orchestration.runtime import check_active, current_task, report_progress, request_timeout

_clients = WeakKeyDictionary()
_lock = Lock()


def wait_for_capacity(delay: float) -> None:
    report_progress({"stage": "waiting", "label": f"Pacing summary requests; next provider budget in {delay:.0f}s. Completed passages are saved."})
    remaining = delay
    while remaining > 0:
        check_active()
        step = min(remaining, request_timeout(5))
        context = current_task.get()
        if context:
            context.cancel.wait(step)
        else:
            time.sleep(step)
        remaining -= step
    check_active()


def get_limiter(client, config):
    from app.core.config import settings
    from app.services.summary.quota import SummaryQuota
    key = (settings.SUMMARY_MODEL, config.requests_per_minute, config.tokens_per_minute)
    with _lock:
        limiters = _clients.setdefault(client, {})
        if key not in limiters:
            limiters[key] = SummaryQuota(config.requests_per_minute, config.tokens_per_minute)
        return limiters[key]
