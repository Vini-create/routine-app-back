from __future__ import annotations
from Alfred.rag.loader import LoadedDocument
import re
from dataclasses import dataclass
from typing import Any
from functools import lru_cache
import tiktoken
EMBEDDING_MODEL = "text-embedding-3-small"


@lru_cache
def get_token_encoder(model: str = EMBEDDING_MODEL) -> tiktoken.Encoding:
    return tiktoken.encoding_for_model(model)


def count_tokens(text: str, model: str = EMBEDDING_MODEL) -> int:
    encoder = get_token_encoder(model)
    return len(encoder.encode(text))

TOKEN_LIMITS = {
    "knowledge": (250, 650),
    "playbook": (300, 900),
}


def validate_token_count(
    document_type: str,
    token_count: int,
    document_id: str,
) -> None:
    try:
        minimum, maximum = TOKEN_LIMITS[document_type]
    except KeyError as error:
        raise ValueError(
            f"Unsupported document type: '{document_type}'."
        ) from error

    if not minimum <= token_count <= maximum:
        raise ValueError(
            f"Document '{document_id}' has {token_count} tokens. "
            f"A '{document_type}' chunk must have between "
            f"{minimum} and {maximum} tokens."
        )

def build_whole_document_chunk(document: LoadedDocument) -> Chunk:
    metadata = document.metadata
    document_type = metadata["document_type"]
    token_count = count_tokens(document.body)

    validate_token_count(
        document_type=document_type,
        token_count=token_count,
        document_id=document.document_id,
    )

    chunk_suffix = "whole" if document_type == "playbook" else "001"

    return Chunk(
        chunk_id=f"chunk-{document.document_id}-{chunk_suffix}",
        document_id=document.document_id,
        document_type=document_type,
        topic_id=metadata["topic_id"],
        concept_id=metadata.get("concept_id"),
        playbook_id=metadata.get("playbook_id"),
        content=document.body,
        section="Whole document",
        source_ids=tuple(metadata.get("source_ids", [])),
        language=metadata["language"],
        status=metadata["status"],
        source_path=document.registry["path"],
        token_count=token_count,
        related_concept_ids=tuple(
            metadata.get("related_concept_ids", [])
        ),
        trigger_phrases=tuple(metadata.get("trigger_phrases", [])),
    )

def build_chunks(document: LoadedDocument) -> tuple[Chunk, ...]:
    return (build_whole_document_chunk(document),)

@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    document_id: str
    document_type: str
    topic_id: str
    content: str
    section: str
    source_ids: tuple[str, ...]
    language: str
    status: str
    source_path: str
    token_count: int
    concept_id: str | None = None
    playbook_id: str | None = None
    related_concept_ids: tuple[str, ...] = ()
    trigger_phrases: tuple[str, ...] = ()

    def to_metadata(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "document_type": self.document_type,
            "topic_id": self.topic_id,
            "concept_id": self.concept_id,
            "playbook_id": self.playbook_id,
            "section": self.section,
            "source_ids": list(self.source_ids),
            "language": self.language,
            "status": self.status,
            "source_path": self.source_path,
            "token_count": self.token_count,
            "related_concept_ids": list(self.related_concept_ids),
            "trigger_phrases": list(self.trigger_phrases),
        }
    
@dataclass(frozen=True)
class MarkdownSection:
    title: str
    content: str

    def render(self) -> str:
        return f"## {self.title}\n\n{self.content}"


def parse_markdown_sections(
    markdown: str,
) -> tuple[str, tuple[MarkdownSection, ...]]:
    title_match = re.match(r"^# (?P<title>[^\n]+)\n*", markdown)

    if title_match is None:
        raise ValueError("The document must start with a Markdown '# ' title.")

    document_title = title_match.group("title").strip()
    remaining_text = markdown[title_match.end():].strip()

    section_matches = list(
        re.finditer(r"^## (?P<title>[^\n]+)\s*$", remaining_text, re.MULTILINE)
    )

    if not section_matches:
        raise ValueError("The document must contain at least one Markdown '## ' section.")

    sections: list[MarkdownSection] = []

    for index, section_match in enumerate(section_matches):
        next_section_start = (
            section_matches[index + 1].start()
            if index + 1 < len(section_matches)
            else len(remaining_text)
        )

        section_title = section_match.group("title").strip()
        section_content = remaining_text[
            section_match.end():next_section_start
        ].strip()

        if not section_content:
            raise ValueError(
                f"The '{section_title}' section has no content."
            )

        sections.append(
            MarkdownSection(
                title=section_title,
                content=section_content,
            )
        )

    return document_title, tuple(sections)
