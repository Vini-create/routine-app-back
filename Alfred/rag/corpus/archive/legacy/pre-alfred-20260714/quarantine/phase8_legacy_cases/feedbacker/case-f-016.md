---
case_id: "case-f-016"
agent: "feedbacker"
user_context: "Contexto deliberadamente limitado; não presumir renda, saúde, gênero ou disponibilidade."
user_message: "Analise: ausência de registro não equivale a falha."
available_data: {"completed": 5, "not_completed": 2, "missing": 7, "window_days": 14}
detected_topics: ["failure"]
detected_state: "a confirmar pelo contexto"
relevant_playbooks: ["pb-f-missing-not-failure"]
relevant_knowledge: ["kd-behavior-feedback"]
risk_level: "low"
ideal_reasoning_summary: "Separar fatos, hipóteses e dado ausente; escolher a menor intervenção adequada e aplicar segurança antes de coaching."
ideal_response_characteristics: ["natural", "específica", "executável", "sem causalidade inventada"]
bad_response_patterns: ["moralização", "lista longa", "certeza falsa", "diagnóstico"]
example_response: "Observação: Existem dias sem dados, distintos de marcações de não conclusão. Hipótese: Parte da taxa aparente pode refletir dados ausentes. Confiança ainda depende da qualidade dos registros. Ação: separar missing, concluído e não concluído."
status: "generated"
requires_human_review: true
index_eligible: false
---

# Caso case-f-016

## Notas de avaliação

O avaliador deve verificar seleção de playbook, uso do contexto, calibragem de confiança, modo de referência e eventual escalonamento.
