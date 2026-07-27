"""Cost-free intent routing for high-confidence Alfred requests."""

import re
import unicodedata
from dataclasses import dataclass

from app.ai.domain.enums import InternalRoute, SelectedSkill


def _compiled(*patterns: str) -> tuple[re.Pattern[str], ...]:
    return tuple(re.compile(pattern) for pattern in patterns)


def _canonical(value: str) -> str:
    folded = unicodedata.normalize("NFKD", value.casefold())
    without_accents = "".join(
        character for character in folded if not unicodedata.combining(character)
    )
    return " ".join(without_accents.split())


_DETERMINISTIC_PATTERNS = _compiled(
    r"\b(?:quantos?|quantas?|numero|total)\b.{0,45}\b(?:habitos?|metas?|tarefas?)\b",
    r"\b(?:habitos?|metas?|tarefas?)\b.{0,45}\b(?:ativos?|concluidos?|pendentes?)\b",
    r"\b(?:taxa|percentual|porcentagem)\b.{0,40}\b(?:conclusao|execucao)\b",
    r"\b(?:sequencia|streak)\b.{0,35}\b(?:atual|maior|habito)?\b",
    r"\bhow many\b.{0,45}\b(?:habits?|goals?|tasks?)\b",
    r"\b(?:completion rate|active habits?|current streak)\b",
    r"\bcuantos?\b.{0,45}\b(?:habitos?|metas?|tareas?)\b",
    r"\b(?:taux de completion|combien)\b.{0,45}\b(?:habitudes?|objectifs?)?\b",
)

_ANALYTICAL_PATTERNS = _compiled(
    r"\b(?:analise|avalie|diagnostique)\b.{0,70}\b(?:progresso|rotina|execucao|"
    r"habitos?|ultimos? \d+ dias|semanas?|mes)\b",
    r"\b(?:por que|porque)\b.{0,70}\b(?:nao consigo|estou falhando|abandono|"
    r"desisto|inconsistente)\b",
    r"\b(?:padroes?|gargalos?|anomalias?|tendencias?)\b.{0,60}\b(?:rotina|"
    r"habitos?|execucao|progresso)\b",
    r"\b(?:reorganize|reestruture|mude|ajuste)\b.{0,55}\b(?:rotina|plano|habitos?)\b",
    r"\b(?:analy[sz]e|evaluate|diagnose)\b.{0,70}\b(?:progress|routine|execution|"
    r"habits?|last \d+ days?|weeks?|month)\b",
    r"\b(?:analiza|evalua|diagnostica)\b.{0,70}\b(?:progreso|rutina|habitos?)\b",
    r"\b(?:analyse|evalue|diagnostique)\b.{0,70}\b(?:progres|routine|habitudes?)\b",
)

_KNOWLEDGE_PATTERNS = _compiled(
    r"\b(?:o que|que)\b.{0,25}\b(?:ciencia|pesquisa|estudos?|evidencias?)\b",
    r"\b(?:segundo|com base em)\b.{0,25}\b(?:ciencia|pesquisas?|estudos?|"
    r"evidencias?)\b",
    r"\b(?:ciencia|pesquisas?|estudos?|evidencias?)\b.{0,50}\b(?:sobre|para|"
    r"aplicad[ao]s?)\b",
    r"\b(?:fontes?|referencias?|artigos? cientificos?)\b",
    r"\bwhat does\b.{0,25}\b(?:science|research|evidence)\b",
    r"\b(?:scientific studies|research-backed|evidence-based|sources|references)\b",
    r"\b(?:que dice|segun)\b.{0,25}\b(?:la ciencia|la investigacion|estudios)\b",
    r"\b(?:que dit|selon)\b.{0,25}\b(?:la science|la recherche|les etudes)\b",
)


@dataclass(frozen=True, slots=True)
class DeterministicRoutingDecision:
    route: InternalRoute
    detected_intent: str
    confidence: float
    reason: str
    needs_model: bool


def _matches(patterns: tuple[re.Pattern[str], ...], value: str) -> bool:
    return any(pattern.search(value) for pattern in patterns)


def classify_route(
    message: str,
    selected_skill: SelectedSkill,
) -> DeterministicRoutingDecision:
    """Resolve clear intents locally and reserve a model for genuine ambiguity."""

    canonical = _canonical(message)
    deterministic = _matches(_DETERMINISTIC_PATTERNS, canonical)
    analytical = _matches(_ANALYTICAL_PATTERNS, canonical)
    knowledge = _matches(_KNOWLEDGE_PATTERNS, canonical)

    if knowledge and analytical:
        return DeterministicRoutingDecision(
            InternalRoute.RAG_THEN_FEEDBACKER,
            "knowledge_augmented_analysis",
            0.96,
            "The request explicitly combines evidence with longitudinal analysis.",
            False,
        )
    if knowledge:
        destination = (
            InternalRoute.RAG_THEN_FEEDBACKER
            if selected_skill
            in {
                SelectedSkill.ANALISAR_PROGRESSO,
                SelectedSkill.REORGANIZAR_ROTINA,
                SelectedSkill.CRIAR_PLANO,
            }
            else InternalRoute.RAG_THEN_ALFRED
        )
        return DeterministicRoutingDecision(
            destination,
            "knowledge_request",
            0.94,
            "The request explicitly asks for external evidence or sources.",
            False,
        )
    if deterministic and not analytical:
        return DeterministicRoutingDecision(
            InternalRoute.DETERMINISTIC,
            "simple_user_data_query",
            0.95,
            "The request can be answered from structured user data.",
            False,
        )
    if analytical:
        return DeterministicRoutingDecision(
            InternalRoute.FEEDBACKER,
            "deep_routine_analysis",
            0.93,
            "The request asks for longitudinal diagnosis or routine restructuring.",
            False,
        )

    skill_routes = {
        SelectedSkill.CONSULTAR_CONHECIMENTO: InternalRoute.RAG_THEN_ALFRED,
        SelectedSkill.ANALISAR_PROGRESSO: InternalRoute.FEEDBACKER,
        SelectedSkill.REORGANIZAR_ROTINA: InternalRoute.FEEDBACKER,
        SelectedSkill.CRIAR_PLANO: InternalRoute.FEEDBACKER,
        SelectedSkill.CONVERSAR: InternalRoute.ALFRED,
    }
    if selected_skill in skill_routes:
        return DeterministicRoutingDecision(
            skill_routes[selected_skill],
            f"selected_skill_{selected_skill.value}",
            0.82,
            "The selected skill is a strong hint and the message does not contradict it.",
            False,
        )

    return DeterministicRoutingDecision(
        InternalRoute.ALFRED,
        "general_conversation",
        0.62,
        "No high-confidence analytical, deterministic, or knowledge intent was found.",
        True,
    )
