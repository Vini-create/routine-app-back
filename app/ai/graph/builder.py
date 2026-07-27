"""LangGraph builder matching the canonical Mermaid workflow."""

from typing import Any, cast

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.ai.domain.enums import InternalRoute
from app.ai.graph.conditions import (
    route_after_rag,
    route_after_retrieval_validation,
    route_after_safety,
    route_critic_approval,
    route_critic_requirement,
    route_human_decision,
    route_main_capability,
    route_memory_decision,
    route_patch_presence,
    route_patch_safety,
)
from app.ai.graph.nodes import MAIN_GRAPH_NODES
from app.ai.graph.runtime import GraphRuntimeContext
from app.ai.graph.state import AgentState

GRAPH_RECURSION_LIMIT = 100


def build_graph_builder() -> StateGraph[
    AgentState,
    GraphRuntimeContext,
    AgentState,
    AgentState,
]:
    """Create the uncompiled graph so its structure can be inspected in tests."""

    graph = StateGraph(AgentState, context_schema=GraphRuntimeContext)
    for node_name, node in MAIN_GRAPH_NODES.items():
        # LangGraph accepts partial state dictionaries at runtime, while its
        # current typing overload requires a full TypedDict return.
        graph.add_node(node_name, cast(Any, node))

    graph.add_edge(START, "iniciar_estado")
    graph.add_edge("iniciar_estado", "detectar_idioma")
    graph.add_edge("detectar_idioma", "normalizar_entrada")
    graph.add_edge("normalizar_entrada", "verificar_injecao")
    graph.add_edge("verificar_injecao", "classificar_risco")
    graph.add_conditional_edges(
        "classificar_risco",
        route_after_safety,
        {
            "blocked": "resposta_segura",
            "allowed": "carregar_contexto",
        },
    )
    graph.add_edge("resposta_segura", "traduzir_resposta")

    graph.add_edge("carregar_contexto", "carregar_historico")
    graph.add_edge("carregar_historico", "carregar_memoria")
    graph.add_edge("carregar_memoria", "construir_contexto")
    graph.add_edge("construir_contexto", "calcular_metricas")
    graph.add_edge("calcular_metricas", "detectar_tendencias")
    graph.add_edge("detectar_tendencias", "detectar_anomalias")
    graph.add_edge("detectar_anomalias", "prever_risco_abandono")
    graph.add_edge(
        "prever_risco_abandono",
        "construir_estado_comportamental",
    )
    graph.add_edge(
        "construir_estado_comportamental",
        "classificar_intencao",
    )
    graph.add_conditional_edges(
        "classificar_intencao",
        route_main_capability,
        {
            InternalRoute.SAFE_RESPONSE.value: "resposta_segura",
            InternalRoute.DETERMINISTIC.value: "responder_dado_simples",
            InternalRoute.ALFRED.value: "selecionar_estrategia_alfred",
            InternalRoute.FEEDBACKER.value: "diagnosticar_execucao",
            InternalRoute.RAG_THEN_ALFRED.value: "decidir_busca_rag",
            InternalRoute.RAG_THEN_FEEDBACKER.value: "decidir_busca_rag",
        },
    )

    graph.add_edge("responder_dado_simples", "validar_schema")

    graph.add_edge("decidir_busca_rag", "construir_consulta")
    graph.add_edge("construir_consulta", "recuperar_documentos")
    graph.add_edge("recuperar_documentos", "reranquear_documentos")
    graph.add_edge("reranquear_documentos", "validar_recuperacao")
    graph.add_conditional_edges(
        "validar_recuperacao",
        route_after_retrieval_validation,
        {
            "sufficient": "montar_evidence_pack",
            "insufficient": "marcar_baixa_confianca",
        },
    )
    for rag_exit in ("montar_evidence_pack", "marcar_baixa_confianca"):
        graph.add_conditional_edges(
            rag_exit,
            route_after_rag,
            {
                "alfred": "selecionar_estrategia_alfred",
                "feedbacker": "diagnosticar_execucao",
            },
        )

    graph.add_edge(
        "selecionar_estrategia_alfred",
        "planejar_resposta_alfred",
    )
    graph.add_edge(
        "planejar_resposta_alfred",
        "gerar_intervencao_alfred",
    )
    graph.add_edge(
        "gerar_intervencao_alfred",
        "renderizar_resposta_alfred",
    )
    graph.add_edge("renderizar_resposta_alfred", "decidir_uso_critico")

    graph.add_edge("diagnosticar_execucao", "identificar_padroes")
    graph.add_edge("identificar_padroes", "gerar_hipoteses")
    graph.add_edge("gerar_hipoteses", "gerar_recomendacoes")
    graph.add_edge("gerar_recomendacoes", "gerar_patch")
    graph.add_edge("gerar_patch", "definir_metricas_sucesso")
    graph.add_edge(
        "definir_metricas_sucesso",
        "montar_relatorio_feedbacker",
    )
    graph.add_edge("montar_relatorio_feedbacker", "decidir_uso_critico")

    graph.add_conditional_edges(
        "decidir_uso_critico",
        route_critic_requirement,
        {
            "critic": "criticar_saida",
            "skip": "validar_schema",
        },
    )
    graph.add_conditional_edges(
        "criticar_saida",
        route_critic_approval,
        {
            "approved": "validar_schema",
            "revise": "revisar_saida",
        },
    )
    graph.add_edge("revisar_saida", "criticar_saida")
    graph.add_conditional_edges(
        "validar_schema",
        route_patch_presence,
        {
            "patch": "validar_patch",
            "no_patch": "decidir_memoria",
        },
    )
    graph.add_edge("validar_patch", "simular_patch")
    graph.add_conditional_edges(
        "simular_patch",
        route_patch_safety,
        {
            "safe": "preparar_confirmacao",
            "unsafe": "converter_patch_em_texto",
        },
    )
    graph.add_edge("converter_patch_em_texto", "decidir_memoria")
    graph.add_edge("preparar_confirmacao", "aguardar_confirmacao")
    graph.add_conditional_edges(
        "aguardar_confirmacao",
        route_human_decision,
        {
            "accepted": "aplicar_patch",
            "rejected": "registrar_rejeicao",
            "edited": "revalidar_patch_editado",
            "pending": "formatar_resposta",
        },
    )
    graph.add_edge("aplicar_patch", "criar_auditoria")
    graph.add_edge("criar_auditoria", "decidir_memoria")
    graph.add_edge("registrar_rejeicao", "decidir_memoria")
    graph.add_edge("revalidar_patch_editado", "validar_patch")

    graph.add_conditional_edges(
        "decidir_memoria",
        route_memory_decision,
        {
            "store": "extrair_memoria",
            "skip": "formatar_resposta",
        },
    )
    graph.add_edge("extrair_memoria", "classificar_memoria")
    graph.add_edge("classificar_memoria", "deduplicar_memoria")
    graph.add_edge("deduplicar_memoria", "persistir_memoria")
    graph.add_edge("persistir_memoria", "formatar_resposta")

    graph.add_edge("formatar_resposta", "traduzir_resposta")
    graph.add_edge("traduzir_resposta", "finalizar_trace")
    graph.add_edge("finalizar_trace", END)
    return graph


def build_graph() -> CompiledStateGraph[
    AgentState,
    GraphRuntimeContext,
    AgentState,
    AgentState,
]:
    """Compile the request graph without model clients or API keys."""

    return build_graph_builder().compile(name="winperium_alfred")
