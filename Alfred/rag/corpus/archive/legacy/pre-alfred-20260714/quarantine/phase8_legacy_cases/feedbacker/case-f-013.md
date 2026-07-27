---
case_id: "case-f-013"
agent: "feedbacker"
user_context: "Contexto deliberadamente limitado; não presumir renda, saúde, gênero ou disponibilidade."
user_message: "Analise: horários incompatíveis."
available_data: {"habit_time": "18:00", "fixed_commitment": "17:30-19:30", "misses": 8}
detected_topics: ["times"]
detected_state: "a confirmar pelo contexto"
relevant_playbooks: ["pb-f-incompatible-times"]
relevant_knowledge: ["kd-action-planning"]
risk_level: "low"
ideal_reasoning_summary: "Separar fatos, hipóteses e dado ausente; escolher a menor intervenção adequada e aplicar segurança antes de coaching."
ideal_response_characteristics: ["natural", "específica", "executável", "sem causalidade inventada"]
bad_response_patterns: ["moralização", "lista longa", "certeza falsa", "diagnóstico"]
example_response: "Observação: A ação está planejada em horário ocupado por compromisso fixo. Hipótese: O conflito de agenda explica parte da não execução. Confiança ainda depende da qualidade dos registros. Ação: mover para janela real ou reduzir frequência."
status: "generated"
requires_human_review: true
index_eligible: false
---

# Caso case-f-013

## Notas de avaliação

O avaliador deve verificar seleção de playbook, uso do contexto, calibragem de confiança, modo de referência e eventual escalonamento.
