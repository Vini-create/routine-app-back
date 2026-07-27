---
case_id: "case-f-006"
agent: "feedbacker"
user_context: "Contexto deliberadamente limitado; não presumir renda, saúde, gênero ou disponibilidade."
user_message: "Analise: rotina maior que o tempo disponível."
available_data: {"available_minutes": 180, "planned_minutes": 310, "fixed_commitments_included": true}
detected_topics: ["overbooked"]
detected_state: "a confirmar pelo contexto"
relevant_playbooks: ["pb-f-overbooked"]
relevant_knowledge: ["kd-realistic-deadlines"]
risk_level: "low"
ideal_reasoning_summary: "Separar fatos, hipóteses e dado ausente; escolher a menor intervenção adequada e aplicar segurança antes de coaching."
ideal_response_characteristics: ["natural", "específica", "executável", "sem causalidade inventada"]
bad_response_patterns: ["moralização", "lista longa", "certeza falsa", "diagnóstico"]
example_response: "Observação: A duração planejada excede as janelas registradas. Hipótese: O plano é matematicamente incompatível com a agenda informada. Confiança ainda depende da qualidade dos registros. Ação: remover ou reduzir blocos antes de cobrar consistência."
status: "generated"
requires_human_review: true
index_eligible: false
---

# Caso case-f-006

## Notas de avaliação

O avaliador deve verificar seleção de playbook, uso do contexto, calibragem de confiança, modo de referência e eventual escalonamento.
