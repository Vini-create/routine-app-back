---
case_id: "case-f-015"
agent: "feedbacker"
user_context: "Contexto deliberadamente limitado; não presumir renda, saúde, gênero ou disponibilidade."
user_message: "Analise: ausência de dados suficientes."
available_data: {"records": 0, "window_days": 14, "planned_items": 7}
detected_topics: ["data"]
detected_state: "a confirmar pelo contexto"
relevant_playbooks: ["pb-f-no-data"]
relevant_knowledge: ["kd-self-monitoring"]
risk_level: "low"
ideal_reasoning_summary: "Separar fatos, hipóteses e dado ausente; escolher a menor intervenção adequada e aplicar segurança antes de coaching."
ideal_response_characteristics: ["natural", "específica", "executável", "sem causalidade inventada"]
bad_response_patterns: ["moralização", "lista longa", "certeza falsa", "diagnóstico"]
example_response: "Observação: Não há registros suficientes no período. Hipótese: Qualquer causalidade seria especulativa. Confiança ainda depende da qualidade dos registros. Ação: solicitar registro simples e contexto básico."
status: "generated"
requires_human_review: true
index_eligible: false
---

# Caso case-f-015

## Notas de avaliação

O avaliador deve verificar seleção de playbook, uso do contexto, calibragem de confiança, modo de referência e eventual escalonamento.
