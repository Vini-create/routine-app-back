---
case_id: "case-f-019"
agent: "feedbacker"
user_context: "Contexto deliberadamente limitado; não presumir renda, saúde, gênero ou disponibilidade."
user_message: "Segunda variação: meta sem ações associadas em rotina com horários irregulares."
available_data: {"records": 3, "missing": 4}
detected_topics: ["actions"]
detected_state: "a confirmar pelo contexto"
relevant_playbooks: ["pb-f-goal-no-actions"]
relevant_knowledge: ["kd-action-planning"]
risk_level: "low"
ideal_reasoning_summary: "Separar fatos, hipóteses e dado ausente; escolher a menor intervenção adequada e aplicar segurança antes de coaching."
ideal_response_characteristics: ["natural", "específica", "executável", "sem causalidade inventada"]
bad_response_patterns: ["moralização", "lista longa", "certeza falsa", "diagnóstico"]
example_response: "Vou partir do que está observável e propor um passo pequeno; se faltar um dado que muda a decisão, pergunto apenas por ele."
status: "generated"
requires_human_review: true
index_eligible: false
---

# Caso case-f-019

## Notas de avaliação

O avaliador deve verificar seleção de playbook, uso do contexto, calibragem de confiança, modo de referência e eventual escalonamento.
