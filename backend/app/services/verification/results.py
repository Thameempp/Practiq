from uuid import uuid4

from app.services.verification.models import ClaimVerdict, Review, VerificationResult


def insufficient(claims, reason="The available PDF passages do not establish this claim."):
    return Review(claims=[ClaimVerdict(claim_id=c.id, verdict="insufficient_evidence", reason=reason)
                          for c in claims])


def overall(review) -> str:
    verdicts = {claim.verdict for claim in review.claims}
    if "conflicting_sources" in verdicts:
        return "conflicting_sources"
    if len(verdicts) == 1:
        return next(iter(verdicts))
    if "supported" in verdicts or "partially_supported" in verdicts:
        return "partially_supported"
    return "contradicted" if "contradicted" in verdicts else "insufficient_evidence"


def make_result(target, claims, initial, final, sources, issues, rounds):
    corrections = {claim.claim_id: claim.correction for claim in final.claims if claim.correction}
    texts = {claim.id: claim.text for claim in claims.claims}
    answer = "\n".join(c.correction or texts[c.claim_id] for c in final.claims
                       if c.correction or c.verdict == "supported") if corrections else None
    ids = {ref.source_id for claim in final.claims for ref in claim.evidence}
    limitations = ["Verification checks bounded PDF passages, not exhaustive coverage of every page."]
    if target.truncated or not claims.complete:
        limitations.append("Only part of the original answer was checked; this verdict does not confirm the entire response.")
    if target.artifact == "summary":
        limitations.append("Claim checks do not establish that the summary includes every essential topic.")
    if corrections and any(c.verdict in {"insufficient_evidence", "conflicting_sources"} for c in final.claims):
        limitations.append("The corrected answer includes grounded claims only; unresolved claims are omitted.")
    return VerificationResult(response_id=uuid4().hex, original_response_id=target.response_id,
        verdict=overall(final), initial_verdict=overall(initial), claims=final.claims,
        claim_texts=texts, sources=[source.public() for source in sources if source.id in ids],
        corrected_answer=answer, limitations=limitations, citation_issues=issues,
        retrieval_rounds=rounds, coverage_complete=not target.truncated and claims.complete, scope=target.scope)
