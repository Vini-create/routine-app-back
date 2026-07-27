---
case_id: "case-f-005"
agent: "feedbacker"
user_context: "Contexto deliberadamente limitado; não presumir renda, saúde, gênero ou disponibilidade."
user_message: "Analise: excesso de metas."
available_data: {"active_goals": 9, "goals_with_progress": 2, "declared_priorities": 9}
detected_topics: ["goals"]
detected_state: "a confirmar pelo contexto"
relevant_playbooks: ["pb-f-too-many-goals"]
relevant_knowledge: ["kd-goal-review"]
risk_level: "low"
ideal_reasoning_summary: "Separar fatos, hipóteses e dado ausente; escolher a menor intervenção adequada e aplicar segurança antes de coaching."
ideal_response_characteristics: ["natural", "específica", "executável", "sem causalidade inventada"]
bad_response_patterns: ["moralização", "lista longa", "certeza falsa", "diagnóstico"]
example_response: "Observação: O número de metas ativas supera o foco declarado. Hipótese: As metas podem competir por tempo e energia. Confiança ainda depende da qualidade dos registros. Ação: classificar em foco, manutenção e espera."
status: "generated"
requires_human_review: true
index_eligible: false
---

# Caso case-f-005

## Notas de avaliação

O avaliador deve verificar seleção de playbook, uso do contexto, calibragem de confiança, modo de referência e eventual escalonamento.
