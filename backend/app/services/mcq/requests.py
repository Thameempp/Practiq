"""Validate direct agent calls as well as HTTP requests before doing any work."""

from app.services.mcq.errors import MCQGenerationError


def validate_request(document_id, scope, count):
    if not isinstance(document_id, str) or not document_id.strip():
        raise MCQGenerationError("A document ID is required.")
    if isinstance(count, bool) or not isinstance(count, int) or not 1 <= count <= 10:
        raise MCQGenerationError("The quiz must contain between 1 and 10 questions.")
    if scope is not None and not isinstance(scope, dict):
        raise MCQGenerationError("The selected section must be an object.")
    if (scope or {}).get("documentId") not in (None, "", document_id):
        raise MCQGenerationError("The selected section belongs to a different document.")
