---
case_id: "case-f-003"
agent: "feedbacker"
user_context: "Contexto deliberadamente limitado; não presumir renda, saúde, gênero ou disponibilidade."
user_message: "Analise: meta sem ações associadas."
available_data: {"goal": "concluir TCC", "linked_actions": [], "days_active": 21}
detected_topics: ["actions"]
detected_state: "a confirmar pelo contexto"
relevant_playbooks: ["pb-f-goal-no-actions"]
relevant_knowledge: ["kd-action-planning"]
risk_level: "low"
ideal_reasoning_summary: "Separar fatos, hipóteses e dado ausente; escolher a menor intervenção adequada e aplicar segurança antes de coaching."
ideal_response_characteristics: ["natural", "específica", "executável", "sem causalidade inventada"]
bad_response_patterns: ["moralização", "lista longa", "certeza falsa", "diagnóstico"]
example_response: "Observação: A meta não possui ações registradas. Hipótese: A intenção pode não estar operacionalizada. Confiança ainda depende da qualidade dos registros. Ação: vincular uma próxima ação observável."
status: "generated"
requires_human_review: true
index_eligible: false
---

# Caso case-f-003

## Notas de avaliação

O avaliador deve verificar seleção de playbook, uso do contexto, calibragem de confiança, modo de referência e eventual escalonamento.
