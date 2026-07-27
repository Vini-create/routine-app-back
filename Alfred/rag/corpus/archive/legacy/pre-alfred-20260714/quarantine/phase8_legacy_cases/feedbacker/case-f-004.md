---
case_id: "case-f-004"
agent: "feedbacker"
user_context: "Contexto deliberadamente limitado; não presumir renda, saúde, gênero ou disponibilidade."
user_message: "Analise: excesso de hábitos."
available_data: {"active_habits": 14, "median_completion": 0.29, "available_minutes_daily": 35}
detected_topics: ["habits"]
detected_state: "a confirmar pelo contexto"
relevant_playbooks: ["pb-f-too-many-habits"]
relevant_knowledge: ["kd-goal-conflicts"]
risk_level: "low"
ideal_reasoning_summary: "Separar fatos, hipóteses e dado ausente; escolher a menor intervenção adequada e aplicar segurança antes de coaching."
ideal_response_characteristics: ["natural", "específica", "executável", "sem causalidade inventada"]
bad_response_patterns: ["moralização", "lista longa", "certeza falsa", "diagnóstico"]
example_response: "Observação: Há muitos hábitos ativos simultaneamente. Hipótese: A competição por atenção pode reduzir execução. Confiança ainda depende da qualidade dos registros. Ação: pausar parte e manter uma ou duas prioridades."
status: "generated"
requires_human_review: true
index_eligible: false
---

# Caso case-f-004

## Notas de avaliação

O avaliador deve verificar seleção de playbook, uso do contexto, calibragem de confiança, modo de referência e eventual escalonamento.
