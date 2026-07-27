---
case_id: "case-f-002"
agent: "feedbacker"
user_context: "Contexto deliberadamente limitado; não presumir renda, saúde, gênero ou disponibilidade."
user_message: "Analise: conclusão apenas em determinados dias."
available_data: {"weekdays": {"completed": 2, "planned": 20}, "weekends": {"completed": 7, "planned": 8}}
detected_topics: ["pattern"]
detected_state: "a confirmar pelo contexto"
relevant_playbooks: ["pb-f-day-pattern"]
relevant_knowledge: ["kd-stable-context"]
risk_level: "low"
ideal_reasoning_summary: "Separar fatos, hipóteses e dado ausente; escolher a menor intervenção adequada e aplicar segurança antes de coaching."
ideal_response_characteristics: ["natural", "específica", "executável", "sem causalidade inventada"]
bad_response_patterns: ["moralização", "lista longa", "certeza falsa", "diagnóstico"]
example_response: "Observação: A conclusão varia de forma consistente entre tipos de dia. Hipótese: Horário, local ou carga podem diferir entre esses dias. Confiança ainda depende da qualidade dos registros. Ação: comparar contexto e testar janela alternativa."
status: "generated"
requires_human_review: true
index_eligible: false
---

# Caso case-f-002

## Notas de avaliação

O avaliador deve verificar seleção de playbook, uso do contexto, calibragem de confiança, modo de referência e eventual escalonamento.
