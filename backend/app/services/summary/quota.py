"""Conservative rolling request/token reservations, reconciled with actual usage."""

from collections import deque
from math import isfinite
from threading import Lock
from time import monotonic

from app.orchestration.runtime import check_active
from app.services.summary.models import SummaryError
from app.services.summary.pacing import wait_for_capacity


def usage_tokens(response):
    usage = getattr(response, "usage", None)
    if usage is None:
        usage = getattr(getattr(response, "x_groq", None), "usage", None)
    return getattr(usage, "total_tokens", None)


class SummaryQuota:
    def __init__(self, requests: int, tokens: int, *, clock=monotonic, wait=wait_for_capacity):
        self.requests, self.tokens = requests, tokens
        self.clock, self.wait = clock, wait
        self.pending, self.lock = deque(), Lock()


    def reserve(self, tokens: int) -> list:
        if tokens > self.tokens:
            raise SummaryError("A summary request exceeds the configured per-minute token budget. Lower SUMMARY_INPUT_TOKENS or raise SUMMARY_TOKENS_PER_MINUTE to your provider's actual limit.")
        while True:
            check_active()
            with self.lock:
                now = self.clock()
                while self.pending and self.pending[0][0] <= now - 60:
                    self.pending.popleft()
                if len(self.pending) < self.requests and sum(item[1] for item in self.pending) + tokens <= self.tokens:
                    reservation = [now, tokens]
                    self.pending.append(reservation)
                    return reservation
                delay = max(0.01, self.pending[0][0] + 60 - now)
            self.wait(delay)


    def reconcile(self, reservation: list, used) -> None:
        if isinstance(used, (int, float)) and not isinstance(used, bool) and isfinite(used) and used >= 0:
            with self.lock:
                reservation[1] = int(used)
