from rank_bm25 import BM25Okapi


def build_bm25(chunks):



    corpus = [
        chunk["text"] 
        for chunk in chunks
    ]


    tokenized_text = [
        text.lower().split()
        for text in corpus
    ]

    return BM25Okapi(tokenized_text)