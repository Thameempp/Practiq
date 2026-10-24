import re

from app.query.patterns import ALL_DOCUMENTS, CHAPTER, COMPARISON, DOC_REFERENCE, POINTS, SUMMARY_ACTION, SUMMARY_NOUN, reference_of
from app.query.schemas import QueryAnalysis
from app.services.verification.detection import is_verification_request
from app.services.understanding.query import structure_query


def analyze_query(question: str, *, has_documents=False) -> QueryAnalysis:
    text = question.strip()
    if is_verification_request(text):
        return QueryAnalysis(intent="verify_answer")
    if structure_query(text):
        return QueryAnalysis(intent="document_structure", document_scope="all" if ALL_DOCUMENTS.search(text) else "unspecified")
    all_docs = bool(ALL_DOCUMENTS.search(text))
    chapter = CHAPTER.search(text)
    study = bool(re.search(r"\b(?:revision|study)\s+(?:notes|material)|\bflashcards\b", text, re.I))
    compare = bool(COMPARISON.search(text))
    # Topic questions about summaries/key points are not document summaries.
    direct = bool(SUMMARY_ACTION.search(text) or SUMMARY_NOUN.search(text))
    noun_request = bool(re.search(r"\b(?:give|get|provide|show|need|want)\b.*\b(?:summary|overview)\b", text, re.I))
    points = bool(POINTS.search(text))
    points_text = re.sub(r"^what are (?:the )?", "", text, flags=re.I)
    generic_points = bool(re.fullmatch(r"(?:(?:please )?(?:give|show|provide)(?: me)? (?:the )?)?(?:main points|key points|main ideas|key takeaways)[.?!\s]*", points_text, re.I))
    about_doc = bool(re.search(r"\bwhat(?:'s| is) (?:this|the) (?:document|pdf|file|book|paper) (?:all )?about\b", text, re.I))
    summary = direct or noun_request or about_doc or points and (
        bool(DOC_REFERENCE.search(text)) or has_documents and generic_points)
    if study:
        intent = "create_study_material"
    elif compare and all_docs:
        intent = "cross_document_qa"
    elif summary:
        intent = "summarize_all_documents" if all_docs else "summarize_document"
    else:
        intent = "document_qa"
    if re.search(r"\bsummary statistic", text, re.I) and not SUMMARY_ACTION.search(text):
        intent = "document_qa"
    kind = "chapter" if chapter else "key_points" if points else "brief" if re.search(r"\bbrief|in short|tl;?dr\b", text, re.I) else "comprehensive"
    reference = reference_of(text) if summary and not about_doc else None
    return QueryAnalysis(
        intent=intent, document_scope="all" if all_docs else "single" if reference else "unspecified",
        document_reference=reference, summary_type=kind,
        chapter_reference=chapter.group(1) if chapter else None,
        consolidated=bool(re.search(r"\b(?:consolidated|combined|unified)\b|\bsingle summary\b", text, re.I)),
    )
