---
case_id: "case-f-012"
agent: "feedbacker"
user_context: "Contexto deliberadamente limitado; não presumir renda, saúde, gênero ou disponibilidade."
user_message: "Analise: metas repetidamente adiadas."
available_data: {"goal": "certificação", "deadline_changes": 4, "linked_actions_last_30d": 1}
detected_topics: ["postponed"]
detected_state: "a confirmar pelo contexto"
relevant_playbooks: ["pb-f-postponed"]
relevant_knowledge: ["kd-goal-decomposition"]
risk_level: "low"
ideal_reasoning_summary: "Separar fatos, hipóteses e dado ausente; escolher a menor intervenção adequada e aplicar segurança antes de coaching."
ideal_response_characteristics: ["natural", "específica", "executável", "sem causalidade inventada"]
bad_response_patterns: ["moralização", "lista longa", "certeza falsa", "diagnóstico"]
example_response: "Observação: A mesma meta teve o prazo movido várias vezes. Hipótese: Escopo, prioridade ou dependência externa podem estar mal definidos. Confiança ainda depende da qualidade dos registros. Ação: redefinir marco ou pausar explicitamente."
status: "generated"
requires_human_review: true
index_eligible: false
---

# Caso case-f-012

## Notas de avaliação

O avaliador deve verificar seleção de playbook, uso do contexto, calibragem de confiança, modo de referência e eventual escalonamento.
