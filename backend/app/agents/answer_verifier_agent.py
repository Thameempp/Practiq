"""Selectively recheck original claims, reusing evidence before bounded retrieval."""

from app.agents.base import BaseAgent
from app.orchestration.runtime import check_active
from app.services.verification.budget import bounded_target, build_prompt
from app.services.verification.models import VerificationResult
from app.services.verification.prompts import EXTRACT_SYSTEM, REVIEW_SYSTEM
from app.services.verification.results import insufficient, make_result
from app.services.verification.validation import parse_claims, validate_review


class AnswerVerifierAgent(BaseAgent[VerificationResult]):
    def __init__(self, generate_text, load_sources, search, *, on_progress=None):
        self.generate_text, self.load_sources, self.search = (
            generate_text,
            load_sources,
            search,
        )
        self.progress = on_progress or (lambda update: None)


    def verify(self, target) -> VerificationResult:
        return self.run(target)


    def _run(self, target) -> VerificationResult:
        target = bounded_target(target)
        self._stage("reviewing", "Rechecking the previous answer…")
        prompt, _ = build_prompt(EXTRACT_SYSTEM, target)
        claims = parse_claims(self.generate_text(EXTRACT_SYSTEM, prompt), target.answer)
        check_active()
        self._stage("citations", "Checking source references…")
        sources, issues = self.load_sources(target)
        self._stage("comparing", "Comparing document evidence…")
        initial, omitted = self._review(target, claims.claims, sources)
        final, rounds = initial, 0
        disputed = {
            c.claim_id
            for c in initial.claims
            if c.verdict in {"insufficient_evidence", "conflicting_sources"}
        }
        if disputed:
            self._stage("searching", "Finding supporting passages…")
            additional, search_issues = self.search(
                target,
                [c for c in claims.claims if c.id in disputed],
            )
            issues.extend(search_issues)
            known = {source.id: source for source in sources}
            new = [source for source in additional if source.id not in known]
            sources = list({**{source.id: source for source in new}, **known}.values())
            rounds = 1
            if new:
                self._stage("resolving", "Investigating conflicting evidence…")
                final, omitted = self._review(target, claims.claims, sources)
        if any(claim.correction for claim in final.claims):
            self._stage("correcting", "Preparing a corrected answer…")
        result = make_result(
            target,
            claims,
            initial,
            final,
            sources,
            list(dict.fromkeys(issues)),
            rounds,
        )
        if omitted:
            result.coverage_complete = False
            result.limitations.append("Some source passages did not fit the token budget and were not reviewed.")
        self._stage("complete", "Verification complete")
        return result


    def _review(self, target, claims, sources):
        prompt, visible = build_prompt(REVIEW_SYSTEM, target, claims=claims, sources=sources)
        if not visible:
            return insufficient(claims), bool(sources)
        check_active()
        raw = self.generate_text(REVIEW_SYSTEM, prompt)
        check_active()
        return validate_review(raw, claims, visible), len(visible) < len(sources)


    def _stage(self, stage: str, label: str) -> None:
        check_active()
        self.progress({"stage": stage, "label": label})
