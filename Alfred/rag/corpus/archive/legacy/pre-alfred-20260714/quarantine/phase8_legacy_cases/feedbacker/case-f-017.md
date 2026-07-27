---
case_id: "case-f-017"
agent: "feedbacker"
user_context: "Contexto deliberadamente limitado; não presumir renda, saúde, gênero ou disponibilidade."
user_message: "Segunda variação: baixa taxa de conclusão em rotina com horários irregulares."
available_data: {"weekdays_completion": 0.1, "weekends_completion": 0.8, "sample_days": 28}
detected_topics: ["completion"]
detected_state: "a confirmar pelo contexto"
relevant_playbooks: ["pb-f-low-completion"]
relevant_knowledge: ["kd-behavior-feedback"]
risk_level: "low"
ideal_reasoning_summary: "Separar fatos, hipóteses e dado ausente; escolher a menor intervenção adequada e aplicar segurança antes de coaching."
ideal_response_characteristics: ["natural", "específica", "executável", "sem causalidade inventada"]
bad_response_patterns: ["moralização", "lista longa", "certeza falsa", "diagnóstico"]
example_response: "Vou partir do que está observável e propor um passo pequeno; se faltar um dado que muda a decisão, pergunto apenas por ele."
status: "generated"
requires_human_review: true
index_eligible: false
---

# Caso case-f-017

## Notas de avaliação

O avaliador deve verificar seleção de playbook, uso do contexto, calibragem de confiança, modo de referência e eventual escalonamento.
