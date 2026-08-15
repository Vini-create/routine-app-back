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
    r"\b(?:quais|liste|listar|mostre|mostra)\b.{0,55}\b(?:tarefas?|atividades?|agenda|programacao|rotina)\b",
    r"\b(?:o que|que)\b.{0,25}\b(?:tenho|esta programado|esta agendado)\b.{0,35}\b(?:hoje|amanha|dia|semana)?\b",
    r"\b(?:what|which|list|show)\b.{0,45}\b(?:tasks?|activities|schedule)\b",
    r"\b(?:cuales|lista|muestra)\b.{0,45}\b(?:tareas?|actividades|agenda)\b",
)

_GREETING_PATTERNS = _compiled(
    r"^(?:ola|oi|hello|hi|hey|hola|bonjour)[!,.? ]*$",
)

_PATCH_REQUEST_PATTERNS = _compiled(
    r"\b(?:mude|altere|ajuste|reorganize|remarque|troque|reduza|aumente|adicione)\b.{0,75}\b(?:rotina|tarefa|atividade|habito|meta|horario|duracao|prioridade)\b",
    r"\b(?:change|update|adjust|reschedule|reduce|increase)\b.{0,75}\b(?:routine|task|habit|goal|time|duration|priority)\b",
    r"\b(?:cambia|ajusta|reprograma|reduce|aumenta)\b.{0,75}\b(?:rutina|tarea|habito|meta|hora|duracion)\b",
    r"\b(?:monte|crie|faca|proponha|sugira)\b.{0,70}\b(?:alteracao|mudanca|ajuste|reorganizacao)\b",
    r"\b(?:sugestao|proposta)\b.{0,45}\b(?:alteracao|mudanca|ajuste)\b",
    r"\b(?:make|create|propose|suggest)\b.{0,70}\b(?:change|adjustment|reorganization)\b",
    r"\b(?:propon|sugier|crea)\w*\b.{0,70}\b(?:cambio|ajuste|reorganizacion)\b",
)
_OPEN_ENDED_PATCH_PATTERNS = _compiled(
    r"\b(?:monte|crie|faca|proponha|sugira)\b.{0,70}\b(?:alteracao|mudanca|ajuste|reorganizacao)\b",
    r"\b(?:sugestao|proposta)\b.{0,45}\b(?:alteracao|mudanca|ajuste)\b",
    r"\b(?:make|create|propose|suggest)\b.{0,70}\b(?:change|adjustment|reorganization)\b",
    r"\b(?:propon|sugier|crea)\w*\b.{0,70}\b(?:cambio|ajuste|reorganizacion)\b",
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

_IDEAL_ROUTINE_PATTERNS = _compiled(
    r"\b(?:rotina|routine|rutina)\b.{0,45}\b(?:ideal|perfeit[ao]|"
    r"personalizad[ao]|otim[ao]|perfect|personalized|optimal|ideale|"
    r"personnalisee)\b",
    r"\b(?:ideal|perfeit[ao]|personalizad[ao]|otim[ao]|perfect|"
    r"personalized|optimal|ideale|personnalisee)\b.{0,45}\b"
    r"(?:rotina|routine|rutina)\b",
    r"\b(?:crie|criar|monte|montar|faca|organize|planeje|create|build|"
    r"make|design|crea|crear|construye|cree|creer|construis)\b.{0,45}\b"
    r"(?:rotina|routine|rutina)\b",
)
_EXPLICIT_OBJECTIVE_PATTERNS = _compiled(
    r"\b(?:meu|minha|my|mi|mon|ma)\s+(?:objetivo|meta|foco|prioridade|"
    r"goal|target|focus|objetivo|objectif|priorite)\b.{0,30}\b"
    r"(?:e|is|es|est|:)",
    r"\b(?:objetivo|meta|foco|prioridade|goal|target|focus|objectif|"
    r"priorite)\b\s*[:=-]\s*\w+",
    r"\b(?:para|to|for|pour)\s+(?!(?:mim|me|mi|moi)\b)\w+",
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


def is_explicit_patch_request(message: str) -> bool:
    """Identify an explicit request to change existing application data."""

    return _matches(_PATCH_REQUEST_PATTERNS, _canonical(message))


def is_open_ended_patch_request(message: str) -> bool:
    """Identify when Alfred was asked to choose and design the adjustment."""

    return _matches(_OPEN_ENDED_PATCH_PATTERNS, _canonical(message))


def active_goals(goals: list[dict[str, object]]) -> list[dict[str, object]]:
    """Return goals that can still guide a new plan, preserving priority order."""

    return [
        goal
        for goal in goals
        if str(goal.get("status", "")).casefold() in {"active", "in_progress"}
    ]


def needs_routine_goal_clarification(
    message: str,
    selected_skill: SelectedSkill,
    goals: list[dict[str, object]],
) -> bool:
    """Require an objective before generating a personalized ideal routine."""

    canonical = _canonical(message)
    mentions_routine = bool(re.search(r"\b(?:rotina|routine|rutina)\b", canonical))
    asks_for_routine = _matches(_IDEAL_ROUTINE_PATTERNS, canonical) or (
        selected_skill is SelectedSkill.CRIAR_PLANO and mentions_routine
    )
    if not asks_for_routine:
        return False

    current_goals = active_goals(goals)
    references_known_goal = any(
        (title := _canonical(str(goal.get("title", ""))))
        and len(title) >= 4
        and title in canonical
        for goal in current_goals
    )
    states_objective = _matches(_EXPLICIT_OBJECTIVE_PATTERNS, canonical)
    if references_known_goal or states_objective:
        return False

    # The wording is explicit enough to protect both automatic and manually
    # selected flows from generating an ungrounded routine.
    return True


def classify_route(
    message: str,
    selected_skill: SelectedSkill,
) -> DeterministicRoutingDecision:
    """Resolve clear intents locally and reserve a model for genuine ambiguity."""

    canonical = _canonical(message)
    deterministic = _matches(_DETERMINISTIC_PATTERNS, canonical)
    analytical = _matches(_ANALYTICAL_PATTERNS, canonical)
    knowledge = _matches(_KNOWLEDGE_PATTERNS, canonical)
    patch_request = is_explicit_patch_request(message)

    # A selected skill is a hint, not an instruction to run an expensive
    # capability when the actual message is only a greeting.  This also keeps
    # accidental "olá" turns from consuming a weekly deep-analysis unit.
    if _matches(_GREETING_PATTERNS, canonical):
        return DeterministicRoutingDecision(
            InternalRoute.ALFRED,
            "general_greeting",
            0.99,
            "A greeting should receive a conversational response regardless of the selected skill.",
            False,
        )

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
    if patch_request:
        return DeterministicRoutingDecision(
            InternalRoute.FEEDBACKER,
            "routine_change_request",
            0.96,
            "The user explicitly requested a change to owned routine data.",
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
