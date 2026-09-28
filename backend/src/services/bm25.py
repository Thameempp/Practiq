from rank_bm25 import BM25Okapi
from src.services.loader import documents


corpus = [
    document["text"]
    for document in documents
]


tokenized_text = [
    text.lower().split()
    for text in corpus
]

if not tokenized_text:
    raise ValueError("No chunks were extracted from the PDF.")

bm25 = BM25Okapi(tokenized_text)

def retrieve_relevant_chunks(user_question, top_k=3):


    # query = input("Ask Doubt: ")

    tokenized_query = user_question.lower().split()

    scores = bm25.get_scores(tokenized_query)

    ranked_documents = sorted(
        zip(documents, scores),
        key=lambda x: x[1],
        reverse=True
    )

    return [
        document
        for document, score in ranked_documents[:top_k]
    ]

    # print("\nTop matching chunks:\n")

    # for rank, (document, score) in enumerate(
    #     ranked_documents[:3],
    #     start=1
    # ):
    #     print("=" * 60)
    #     print(f"Rank: {rank}")
    #     print(f"Page: {document['page']}")
    #     print(f"Score: {score:.4f}")
    #     print(document["text"])