---
case_id: "case-a-005"
agent: "alfred"
user_context: "Contexto deliberadamente limitado; não presumir renda, saúde, gênero ou disponibilidade."
user_message: "Quero criar doze hábitos na próxima semana: treino, leitura, água, meditação e mais oito coisas."
available_data: {}
detected_topics: ["habits"]
detected_state: "a confirmar pelo contexto"
relevant_playbooks: ["pb-a-too-many-habits"]
relevant_knowledge: ["kd-goal-conflicts"]
risk_level: "low"
ideal_reasoning_summary: "Separar fatos, hipóteses e dado ausente; escolher a menor intervenção adequada e aplicar segurança antes de coaching."
ideal_response_characteristics: ["natural", "específica", "executável", "sem causalidade inventada"]
bad_response_patterns: ["moralização", "lista longa", "certeza falsa", "diagnóstico"]
example_response: "Entendo a restrição concreta. Minha proposta é escolher uma ou duas mudanças e manter o resto; vamos tratar isso como um teste revisável, não como um julgamento sobre você."
status: "generated"
requires_human_review: true
index_eligible: false
---

# Caso case-a-005

## Notas de avaliação

O avaliador deve verificar seleção de playbook, uso do contexto, calibragem de confiança, modo de referência e eventual escalonamento.
