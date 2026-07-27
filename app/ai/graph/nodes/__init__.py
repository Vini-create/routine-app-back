"""Canonical registry of executable nodes from ``graph_overview.md``."""

from collections.abc import Awaitable, Callable, Mapping
from types import MappingProxyType
from typing import Any

from app.ai.graph.nodes.analysis import (
    build_feedbacker_report_node,
    define_success_metrics_node,
    diagnose_execution_node,
    generate_hypotheses_node,
    generate_patch_node,
    generate_recommendations_node,
    identify_patterns_node,
)
from app.ai.graph.nodes.behavioral import (
    build_behavioral_state_node,
    calculate_metrics_node,
    detect_anomalies_node,
    detect_trends_node,
    predict_dropout_risk_node,
)
from app.ai.graph.nodes.context import (
    build_context_node,
    load_history_node,
    load_memory_node,
    load_user_context_node,
)
from app.ai.graph.nodes.conversation import (
    generate_alfred_intervention_node,
    plan_alfred_response_node,
    render_alfred_response_node,
    select_alfred_strategy_node,
)
from app.ai.graph.nodes.deterministic import answer_deterministic_query_node
from app.ai.graph.nodes.entry import (
    build_safe_response_node,
    check_prompt_injection_node,
    classify_safety_risk_node,
    detect_language_node,
    initialize_state_node,
    normalize_input_node,
)
from app.ai.graph.nodes.human_loop import (
    apply_patch_node,
    await_confirmation_node,
    create_audit_node,
    register_rejection_node,
    revalidate_edited_patch_node,
)
from app.ai.graph.nodes.learning import (
    evaluate_effectiveness_node,
    observe_outcome_node,
    register_intervention_node,
)
from app.ai.graph.nodes.memory import (
    classify_memory_node,
    decide_memory_node,
    deduplicate_memory_node,
    extract_memory_node,
    persist_memory_node,
)
from app.ai.graph.nodes.output import (
    finalize_trace_node,
    format_response_node,
    translate_response_node,
)
from app.ai.graph.nodes.retrieval import (
    build_evidence_pack_node,
    build_retrieval_query_node,
    decide_rag_search_node,
    mark_low_confidence_node,
    rerank_documents_node,
    retrieve_documents_node,
    validate_retrieval_node,
)
from app.ai.graph.nodes.routing import classify_intent_node
from app.ai.graph.nodes.validation import (
    convert_patch_to_text_node,
    critique_output_node,
    decide_critic_use_node,
    prepare_confirmation_node,
    revise_output_node,
    simulate_patch_node,
    validate_patch_node,
    validate_schema_node,
)

NodeCallable = Callable[..., Awaitable[dict[str, Any]]]

MAIN_GRAPH_NODES: Mapping[str, NodeCallable] = MappingProxyType(
    {
        "iniciar_estado": initialize_state_node,
        "detectar_idioma": detect_language_node,
        "normalizar_entrada": normalize_input_node,
        "verificar_injecao": check_prompt_injection_node,
        "classificar_risco": classify_safety_risk_node,
        "resposta_segura": build_safe_response_node,
        "carregar_contexto": load_user_context_node,
        "carregar_historico": load_history_node,
        "carregar_memoria": load_memory_node,
        "construir_contexto": build_context_node,
        "calcular_metricas": calculate_metrics_node,
        "detectar_tendencias": detect_trends_node,
        "detectar_anomalias": detect_anomalies_node,
        "prever_risco_abandono": predict_dropout_risk_node,
        "construir_estado_comportamental": build_behavioral_state_node,
        "classificar_intencao": classify_intent_node,
        "responder_dado_simples": answer_deterministic_query_node,
        "decidir_busca_rag": decide_rag_search_node,
        "construir_consulta": build_retrieval_query_node,
        "recuperar_documentos": retrieve_documents_node,
        "reranquear_documentos": rerank_documents_node,
        "validar_recuperacao": validate_retrieval_node,
        "montar_evidence_pack": build_evidence_pack_node,
        "marcar_baixa_confianca": mark_low_confidence_node,
        "selecionar_estrategia_alfred": select_alfred_strategy_node,
        "planejar_resposta_alfred": plan_alfred_response_node,
        "gerar_intervencao_alfred": generate_alfred_intervention_node,
        "renderizar_resposta_alfred": render_alfred_response_node,
        "diagnosticar_execucao": diagnose_execution_node,
        "identificar_padroes": identify_patterns_node,
        "gerar_hipoteses": generate_hypotheses_node,
        "gerar_recomendacoes": generate_recommendations_node,
        "gerar_patch": generate_patch_node,
        "definir_metricas_sucesso": define_success_metrics_node,
        "montar_relatorio_feedbacker": build_feedbacker_report_node,
        "decidir_uso_critico": decide_critic_use_node,
        "criticar_saida": critique_output_node,
        "revisar_saida": revise_output_node,
        "validar_schema": validate_schema_node,
        "validar_patch": validate_patch_node,
        "simular_patch": simulate_patch_node,
        "converter_patch_em_texto": convert_patch_to_text_node,
        "preparar_confirmacao": prepare_confirmation_node,
        "aguardar_confirmacao": await_confirmation_node,
        "aplicar_patch": apply_patch_node,
        "registrar_rejeicao": register_rejection_node,
        "revalidar_patch_editado": revalidate_edited_patch_node,
        "criar_auditoria": create_audit_node,
        "decidir_memoria": decide_memory_node,
        "extrair_memoria": extract_memory_node,
        "classificar_memoria": classify_memory_node,
        "deduplicar_memoria": deduplicate_memory_node,
        "persistir_memoria": persist_memory_node,
        "formatar_resposta": format_response_node,
        "traduzir_resposta": translate_response_node,
        "finalizar_trace": finalize_trace_node,
    }
)

ASYNC_LEARNING_NODES: Mapping[str, NodeCallable] = MappingProxyType(
    {
        "registrar_intervencao": register_intervention_node,
        "observar_resultado": observe_outcome_node,
        "avaliar_eficacia": evaluate_effectiveness_node,
    }
)

ALL_EXECUTABLE_NODES: Mapping[str, NodeCallable] = MappingProxyType(
    {**MAIN_GRAPH_NODES, **ASYNC_LEARNING_NODES}
)

__all__ = [
    "ALL_EXECUTABLE_NODES",
    "ASYNC_LEARNING_NODES",
    "MAIN_GRAPH_NODES",
    "NodeCallable",
]
