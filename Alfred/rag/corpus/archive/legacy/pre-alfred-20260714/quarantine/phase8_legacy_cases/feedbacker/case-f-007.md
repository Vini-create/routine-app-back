---
case_id: "case-f-007"
agent: "feedbacker"
user_context: "Contexto deliberadamente limitado; não presumir renda, saúde, gênero ou disponibilidade."
user_message: "Analise: concentração de tarefas em um período."
available_data: {"tasks_after_19h": 11, "total_tasks": 14, "evening_window_minutes": 120}
detected_topics: ["concentrated"]
detected_state: "a confirmar pelo contexto"
relevant_playbooks: ["pb-f-concentrated"]
relevant_knowledge: ["kd-energy-overload"]
risk_level: "low"
ideal_reasoning_summary: "Separar fatos, hipóteses e dado ausente; escolher a menor intervenção adequada e aplicar segurança antes de coaching."
ideal_response_characteristics: ["natural", "específica", "executável", "sem causalidade inventada"]
bad_response_patterns: ["moralização", "lista longa", "certeza falsa", "diagnóstico"]
example_response: "Observação: Grande parte das tarefas está concentrada em uma janela curta. Hipótese: A concentração pode aumentar conflitos quando há imprevistos. Confiança ainda depende da qualidade dos registros. Ação: redistribuir itens flexíveis e preservar margem."
status: "generated"
requires_human_review: true
index_eligible: false
---

# Caso case-f-007

## Notas de avaliação

O avaliador deve verificar seleção de playbook, uso do contexto, calibragem de confiança, modo de referência e eventual escalonamento.
