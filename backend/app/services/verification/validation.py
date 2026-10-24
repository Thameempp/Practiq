import unicodedata

from pydantic import ValidationError

from app.services.verification.models import ClaimSet, Review, VerificationError


def normalized(text: str) -> str:
    return " ".join(unicodedata.normalize("NFC", text).split()).casefold()


def parse_model(model, raw):
    try:
        return model.model_validate_json(raw) if isinstance(raw, str) else model.model_validate(raw)
    except (ValidationError, ValueError, TypeError) as error:
        raise VerificationError("The verifier returned an invalid review. The answer could not be confirmed.") from error


def parse_claims(raw, answer: str):
    result = parse_model(ClaimSet, raw)
    ids = [claim.id for claim in result.claims]
    if len(ids) != len(set(ids)) or any(normalized(c.text) not in normalized(answer) for c in result.claims):
        raise VerificationError("The verifier could not identify the original claims reliably.")
    return result


def validate_review(raw, claims, visible):
    result = parse_model(Review, raw)
    ids = [claim.claim_id for claim in result.claims]
    if len(ids) != len(set(ids)) or set(ids) != {claim.id for claim in claims}:
        raise VerificationError("The verifier did not review every disputed claim.")
    for claim in result.claims:
        stances, documents = set(), set()
        for reference in claim.evidence:
            source = visible.get(reference.source_id)
            if not source or normalized(reference.quote) not in normalized(source["text"]):
                raise VerificationError("The verifier cited an unconfirmed PDF passage.")
            stances.add(reference.stance)
            documents.add(source["document_id"])
        expected = {"supported": "supports", "contradicted": "contradicts",
                    "partially_supported": "supports"}.get(claim.verdict)
        invalid = bool(expected and expected not in stances)
        invalid |= claim.verdict in {"supported", "contradicted"} and stances != {expected}
        invalid |= stances == {"supports", "contradicts"} and len(documents) > 1 and claim.verdict != "conflicting_sources"
        invalid |= claim.verdict == "conflicting_sources" and (stances != {"supports", "contradicts"} or len(documents) < 2)
        invalid |= claim.verdict == "insufficient_evidence" and bool(claim.evidence)
        needs_correction = claim.verdict in {"contradicted", "partially_supported"}
        invalid |= bool(claim.correction) != needs_correction
        if invalid:
            raise VerificationError("The verifier's verdict is not backed by its evidence.")
    return result
