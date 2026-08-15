from app.ai.retrieval.editorial_phrases import (
    load_editorial_phrases,
    retrieve_motivational_phrase,
)


def test_editorial_phrase_collection_is_complete_and_localized() -> None:
    phrases = load_editorial_phrases()

    assert len(phrases) >= 6
    assert len({phrase["phrase_id"] for phrase in phrases}) == len(phrases)
    assert all(
        set(phrase["texts"]) == {"pt-BR", "en", "es", "fr"} for phrase in phrases
    )


def test_explicit_motivational_request_retrieves_one_relevant_phrase() -> None:
    phrase = retrieve_motivational_phrase(
        "Estou desanimado com minha meta, preciso de motivação.",
        response_language="pt-BR",
        recent_assistant_messages=[],
    )

    assert phrase is not None
    assert phrase["origin"] == "alfred_editorial"
    assert phrase["text"]


def test_factual_request_does_not_receive_a_motivational_phrase() -> None:
    assert (
        retrieve_motivational_phrase(
            "Quais são minhas tarefas de hoje?",
            response_language="pt-BR",
            recent_assistant_messages=[],
        )
        is None
    )


def test_recently_used_phrase_is_not_repeated() -> None:
    message = "Estou desanimado com minha meta, preciso de motivação."
    first = retrieve_motivational_phrase(
        message,
        response_language="pt-BR",
        recent_assistant_messages=[],
    )
    assert first is not None

    second = retrieve_motivational_phrase(
        message,
        response_language="pt-BR",
        recent_assistant_messages=[first["text"]],
    )

    assert second is None or second["phrase_id"] != first["phrase_id"]


def test_lightly_paraphrased_phrase_is_also_treated_as_recent() -> None:
    message = "Estou desanimado com minha meta, preciso de motivação."
    first = retrieve_motivational_phrase(
        message,
        response_language="pt-BR",
        recent_assistant_messages=[],
    )
    assert first is not None
    paraphrase = first["text"].replace("Um dia", "Cada dia").replace("; é", ", mas é")

    second = retrieve_motivational_phrase(
        message,
        response_language="pt-BR",
        recent_assistant_messages=[f"Lembre-se: {paraphrase}"],
    )

    assert second is None or second["phrase_id"] != first["phrase_id"]
