import re

LABELS = {"supported": "Supported", "contradicted": "Contradicted",
          "partially_supported": "Partially supported", "insufficient_evidence": "Insufficient evidence",
          "conflicting_sources": "Conflicting sources"}


def escape(text: str) -> str:
    return re.sub(r"([\\`*_{}\[\]<>()#!|])", r"\\\1", text)


def render_result(result) -> str:
    scope = " (checked claims only)" if not result.coverage_complete else ""
    parts = [f"**Verification: {LABELS[result.verdict]}{scope}**\n"]
    if result.scope:
        parts.append("**Topic:** " + escape(" > ".join(result.scope.get("topic_path", [result.scope["title"]]))) + "\n")
    for claim in result.claims:
        refs = " ".join(f"[[{source_id}]]" for source_id in dict.fromkeys(ref.source_id for ref in claim.evidence))
        parts.append(f"- **{LABELS[claim.verdict]}:** {escape(result.claim_texts[claim.claim_id])}\n"
                     f"  {escape(claim.reason)} {refs}\n")
        if claim.correction:
            parts.append(f"  **Correction:** {escape(claim.correction)} {refs}\n")
    if result.citation_issues:
        parts.append("\n**Source checks:** " + " ".join(escape(issue) for issue in result.citation_issues) + "\n")
    parts.append("\n" + " ".join(escape(note) for note in result.limitations))
    return "\n".join(parts)
