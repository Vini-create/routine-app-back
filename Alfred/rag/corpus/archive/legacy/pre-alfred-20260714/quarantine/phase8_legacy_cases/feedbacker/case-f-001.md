---
case_id: "case-f-001"
agent: "feedbacker"
user_context: "Contexto deliberadamente limitado; não presumir renda, saúde, gênero ou disponibilidade."
user_message: "Analise: baixa taxa de conclusão."
available_data: {"period_days": 28, "completed": 5, "planned": 20, "missing": 0}
detected_topics: ["completion"]
detected_state: "a confirmar pelo contexto"
relevant_playbooks: ["pb-f-low-completion"]
relevant_knowledge: ["kd-behavior-feedback"]
risk_level: "low"
ideal_reasoning_summary: "Separar fatos, hipóteses e dado ausente; escolher a menor intervenção adequada e aplicar segurança antes de coaching."
ideal_response_characteristics: ["natural", "específica", "executável", "sem causalidade inventada"]
bad_response_patterns: ["moralização", "lista longa", "certeza falsa", "diagnóstico"]
example_response: "Observação: A taxa de conclusão está abaixo do alvo no período. Hipótese: O plano pode exceder capacidade ou conter barreiras recorrentes. Confiança ainda depende da qualidade dos registros. Ação: reduzir escopo e testar uma mudança por sete dias."
status: "generated"
requires_human_review: true
index_eligible: false
---

# Caso case-f-001

## Notas de avaliação

O avaliador deve verificar seleção de playbook, uso do contexto, calibragem de confiança, modo de referência e eventual escalonamento.
