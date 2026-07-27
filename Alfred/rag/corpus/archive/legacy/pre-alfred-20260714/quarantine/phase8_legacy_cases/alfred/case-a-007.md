---
case_id: "case-a-007"
agent: "alfred"
user_context: "Contexto deliberadamente limitado; não presumir renda, saúde, gênero ou disponibilidade."
user_message: "Nunca corri e quero completar uma maratona no mês que vem treinando todos os dias sem falhar."
available_data: {}
detected_topics: ["goal"]
detected_state: "a confirmar pelo contexto"
relevant_playbooks: ["pb-a-unrealistic-goal"]
relevant_knowledge: ["kd-realistic-deadlines"]
risk_level: "low"
ideal_reasoning_summary: "Separar fatos, hipóteses e dado ausente; escolher a menor intervenção adequada e aplicar segurança antes de coaching."
ideal_response_characteristics: ["natural", "específica", "executável", "sem causalidade inventada"]
bad_response_patterns: ["moralização", "lista longa", "certeza falsa", "diagnóstico"]
example_response: "Entendo a restrição concreta. Minha proposta é propor marco intermediário; vamos tratar isso como um teste revisável, não como um julgamento sobre você."
status: "generated"
requires_human_review: true
index_eligible: false
---

# Caso case-a-007

## Notas de avaliação

O avaliador deve verificar seleção de playbook, uso do contexto, calibragem de confiança, modo de referência e eventual escalonamento.
