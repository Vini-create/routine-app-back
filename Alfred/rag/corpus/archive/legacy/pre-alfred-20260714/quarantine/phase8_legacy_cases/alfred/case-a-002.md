---
case_id: "case-a-002"
agent: "alfred"
user_context: "Contexto deliberadamente limitado; não presumir renda, saúde, gênero ou disponibilidade."
user_message: "Começo a correr toda segunda-feira, mantenho por dez dias e depois sumo por um mês."
available_data: {}
detected_topics: ["stops"]
detected_state: "a confirmar pelo contexto"
relevant_playbooks: ["pb-a-starts-stops"]
relevant_knowledge: ["kd-relapse-recovery"]
risk_level: "low"
ideal_reasoning_summary: "Separar fatos, hipóteses e dado ausente; escolher a menor intervenção adequada e aplicar segurança antes de coaching."
ideal_response_characteristics: ["natural", "específica", "executável", "sem causalidade inventada"]
bad_response_patterns: ["moralização", "lista longa", "certeza falsa", "diagnóstico"]
example_response: "Entendo a restrição concreta. Minha proposta é manter uma versão mínima e revisar o ponto de ruptura; vamos tratar isso como um teste revisável, não como um julgamento sobre você."
status: "generated"
requires_human_review: true
index_eligible: false
---

# Caso case-a-002

## Notas de avaliação

O avaliador deve verificar seleção de playbook, uso do contexto, calibragem de confiança, modo de referência e eventual escalonamento.
