from src.services.vector_db_connection import my_vector, index

search_query = input("Enter text string you want retriev: ")

query_response = index.query(
    vector = my_vector,
    top_k = 3,
    include_metadata = True
)

for match in query_response['matches']:
    print(f"score: {match['score']}")
    token_list = match['metadata'].get('text', [])

    if isinstance(token_list, list):
        raw_sentence = " ".join(token_list)


        clean_sentence = raw_sentence.replace(" .", ".").replace(" ,", ",").replace(" , ", ",").replace(" ' ","'")
        print(f"cleaned sentence: {clean_sentence}")