---
case_id: "case-a-013"
agent: "alfred"
user_context: "Contexto deliberadamente limitado; não presumir renda, saúde, gênero ou disponibilidade."
user_message: "Depois das férias decidi que amanhã vou acordar às cinco, treinar, estudar e cozinhar todas as refeições."
available_data: {}
detected_topics: ["everything"]
detected_state: "a confirmar pelo contexto"
relevant_playbooks: ["pb-a-change-everything"]
relevant_knowledge: ["kd-goal-conflicts"]
risk_level: "low"
ideal_reasoning_summary: "Separar fatos, hipóteses e dado ausente; escolher a menor intervenção adequada e aplicar segurança antes de coaching."
ideal_response_characteristics: ["natural", "específica", "executável", "sem causalidade inventada"]
bad_response_patterns: ["moralização", "lista longa", "certeza falsa", "diagnóstico"]
example_response: "Entendo a restrição concreta. Minha proposta é experimento de sete dias com uma mudança; vamos tratar isso como um teste revisável, não como um julgamento sobre você."
status: "generated"
requires_human_review: true
index_eligible: false
---

# Caso case-a-013

## Notas de avaliação

O avaliador deve verificar seleção de playbook, uso do contexto, calibragem de confiança, modo de referência e eventual escalonamento.
