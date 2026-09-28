import os
from groq import Groq
from src.core.config import settings
from pathlib import Path
import time
from src.services.bm25 import retrieve_relevant_chunks
from src.services.loader import page_count, documents
from src.utils.usage import print_usage


client = Groq(api_key = settings.GROQ_API_KEY)

# overview of pdf content
def build_document_overview():
    pages = {
        page_number: []
        for page_number in range(1, page_count + 1)
    }

    for document in documents:
        pages[document['page']].append(document['text'])

    return "\n\n".join(
        f'[page {page_number}]\n'
        + (
            '\n'.join(page_chunks)
            if page_chunks
            else "[No extractable text found on this page]"
        )
        for page_number, page_chunks in pages.items()
    )


def ask_pdf(user_question):
    
    context_text = build_document_overview()
    system_prompt = (
        "You are a document question-answering assistant.\n\n"
        "Use the rules below:\n"
        "1. Use DOCUMENT METADATA for structural facts such as page count.\n"
        "2. Use PDF TEXT CONTEXT for facts found inside the document.\n"
        "3. Never infer the total page count from retrieved text chunks.\n"
        "4. If the answer is not available in either source, say: "
        "'I cannot find that information in the document.'\n\n"
        f"DOCUMENT METADATA:\n"
        f"Total pages: {page_count}\n\n"
        f"FULL PAGE-BY-PAGE PDF CONTENT:\n{context_text}"
    )

    raw_response = client.chat.completions.with_raw_response.create(
        messages=[
            {
                "role":"system",
                "content":system_prompt

            },
            {
                "role":"user",
                "content":user_question,
            }
        ],
        model="openai/gpt-oss-120b",
        stream=True,
        extra_body={"stream_options": {"include_usage": True}}
    )

    # 2. Extract remaining token information immediately from headers
    remaining_tokens = raw_response.headers.get("x-ratelimit-remaining-tokens", "N/A")
    reset_time = raw_response.headers.get("x-ratelimit-reset-tokens", "N/A")

    chat_completion = raw_response.parse()

    answer_parts = []
    final_usage = None

    for chunk in chat_completion:
        if chunk.choices:
            content = chunk.choices[0].delta.content

            if content:
                yield content
                time.sleep(0.04)
        if chunk.usage is not None:
            final_usage = chunk.usage



    print_usage(final_usage, raw_response.headers)
    


