def print_usage(final_usage, headers):
    print("\n--- Token Usage Breakdown ---")

    if final_usage is None:
        print("Usage statistics could not be retrieved.")
        return

    print(f"Prompt Tokens:     {final_usage.prompt_tokens}")
    print(f"Completion Tokens: {final_usage.completion_tokens}")
    print(f"Total Tokens:      {final_usage.total_tokens}")

    prompt_details = getattr(final_usage, "prompt_tokens_details", None)
    completion_details = getattr(
        final_usage,
        "completion_tokens_details",
        None,
    )

    if prompt_details is not None:
        print(
            "Cached Prompt Tokens: "
            f"{getattr(prompt_details, 'cached_tokens', 0)}"
        )

    if completion_details is not None:
        print(
            "Reasoning Tokens: "
            f"{getattr(completion_details, 'reasoning_tokens', 0)}"
        )

    print("\n--- Rate Limit Quota Remaining ---")
    print(
        "Tokens Remaining: "
        f"{headers.get('x-ratelimit-remaining-tokens', 'N/A')}"
    )
    print(
        "Token Window Reset Time: "
        f"{headers.get('x-ratelimit-reset-tokens', 'N/A')}"
    )