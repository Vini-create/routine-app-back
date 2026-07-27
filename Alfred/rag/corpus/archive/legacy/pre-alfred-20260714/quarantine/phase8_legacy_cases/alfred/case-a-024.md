---
case_id: "case-a-024"
agent: "alfred"
user_context: "Contexto deliberadamente limitado; não presumir renda, saúde, gênero ou disponibilidade."
user_message: "Trabalho das 9h às 18h, estudo para concurso e treino para competir; meu sono caiu para cinco horas."
available_data: {}
detected_topics: ["training"]
detected_state: "a confirmar pelo contexto"
relevant_playbooks: ["pb-a-study-work-training"]
relevant_knowledge: ["kd-goal-conflicts"]
risk_level: "low"
ideal_reasoning_summary: "Separar fatos, hipóteses e dado ausente; escolher a menor intervenção adequada e aplicar segurança antes de coaching."
ideal_response_characteristics: ["natural", "específica", "executável", "sem causalidade inventada"]
bad_response_patterns: ["moralização", "lista longa", "certeza falsa", "diagnóstico"]
example_response: "Entendo a restrição concreta. Minha proposta é alternar ênfases e usar mínimos de manutenção; vamos tratar isso como um teste revisável, não como um julgamento sobre você."
status: "generated"
requires_human_review: true
index_eligible: false
---

# Caso case-a-024

## Notas de avaliação

O avaliador deve verificar seleção de playbook, uso do contexto, calibragem de confiança, modo de referência e eventual escalonamento.
