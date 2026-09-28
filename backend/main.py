from src.services.llm import ask_pdf

def main():
    print('PDF Assistant')
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        question = input("Ask Doubt: ").strip()

        if question.lower() in {"exit", "quit"}:
            print('Goodbye.')
            break

        if not question:
            continue

        ask_pdf(question)
        print()


if __name__ == "__main__":
    main()