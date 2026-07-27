from collections import Counter

from Alfred.rag.chunks import (
    TOKEN_LIMITS,
    build_chunks,
    parse_markdown_sections,
)
from Alfred.rag.loader import load_production_documents


def get_document(document_id: str):
    return next(
        document
        for document in load_production_documents()
        if document.document_id == document_id
    )


def test_parses_canonical_markdown_sections():
    document = get_document("kd-action-planning")

    title, sections = parse_markdown_sections(document.body)

    assert title == "Executable Action Planning"
    assert len(sections) == 11
    assert sections[0].title == "Operational definition"
    assert sections[-1].title == "Sources"


def test_builds_expected_knowledge_chunk():
    document = get_document("kd-action-planning")

    chunk = build_chunks(document)[0]

    assert chunk.chunk_id == "chunk-kd-action-planning-001"
    assert chunk.document_type == "knowledge"
    assert chunk.topic_id == "planning"
    assert chunk.concept_id == "action-planning"
    assert chunk.playbook_id is None
    assert chunk.source_ids == (
        "src-bcttv1-2013",
        "src-self-regulation-2020",
    )
    assert 250 <= chunk.token_count <= 650


def test_builds_expected_playbook_chunk():
    document = get_document("pb-user-cannot-start")

    chunk = build_chunks(document)[0]

    assert chunk.chunk_id == "chunk-pb-user-cannot-start-whole"
    assert chunk.document_type == "playbook"
    assert chunk.playbook_id == "user-cannot-start"
    assert chunk.concept_id is None
    assert "action-planning" in chunk.related_concept_ids
    assert "I know what I need to do but cannot start" in chunk.trigger_phrases
    assert 300 <= chunk.token_count <= 900


def test_builds_one_valid_unique_chunk_per_production_document():
    documents = load_production_documents()

    chunks = [
        chunk
        for document in documents
        for chunk in build_chunks(document)
    ]

    assert len(documents) == 45
    assert len(chunks) == 45
    assert len({chunk.chunk_id for chunk in chunks}) == 45

    assert Counter(chunk.document_type for chunk in chunks) == {
        "knowledge": 28,
        "playbook": 17,
    }

    for chunk in chunks:
        minimum, maximum = TOKEN_LIMITS[chunk.document_type]

        assert chunk.content.startswith("# ")
        assert chunk.content.strip()
        assert minimum <= chunk.token_count <= maximum