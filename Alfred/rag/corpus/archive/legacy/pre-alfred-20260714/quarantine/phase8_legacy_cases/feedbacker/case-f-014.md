---
case_id: "case-f-014"
agent: "feedbacker"
user_context: "Contexto deliberadamente limitado; não presumir renda, saúde, gênero ou disponibilidade."
user_message: "Analise: padrões insuficientes para conclusão."
available_data: {"records": 4, "window_days": 30, "completion_values": [true, false, true, false]}
detected_topics: ["pattern"]
detected_state: "a confirmar pelo contexto"
relevant_playbooks: ["pb-f-insufficient-pattern"]
relevant_knowledge: ["kd-self-monitoring"]
risk_level: "low"
ideal_reasoning_summary: "Separar fatos, hipóteses e dado ausente; escolher a menor intervenção adequada e aplicar segurança antes de coaching."
ideal_response_characteristics: ["natural", "específica", "executável", "sem causalidade inventada"]
bad_response_patterns: ["moralização", "lista longa", "certeza falsa", "diagnóstico"]
example_response: "Observação: Há poucos registros ou grande variabilidade. Hipótese: Não é possível sustentar uma explicação com confiança. Confiança ainda depende da qualidade dos registros. Ação: coletar dados mínimos antes de alterar tudo."
status: "generated"
requires_human_review: true
index_eligible: false
---

# Caso case-f-014

## Notas de avaliação

O avaliador deve verificar seleção de playbook, uso do contexto, calibragem de confiança, modo de referência e eventual escalonamento.
