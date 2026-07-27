---
case_id: "case-f-009"
agent: "feedbacker"
user_context: "Contexto deliberadamente limitado; não presumir renda, saúde, gênero ou disponibilidade."
user_message: "Analise: recuperação após queda."
available_data: {"rates_by_week": [0.72, 0.31, 0.44, 0.69], "recent_adjustment": "duração reduzida"}
detected_topics: ["recovery"]
detected_state: "a confirmar pelo contexto"
relevant_playbooks: ["pb-f-recovery"]
relevant_knowledge: ["kd-relapse-recovery"]
risk_level: "low"
ideal_reasoning_summary: "Separar fatos, hipóteses e dado ausente; escolher a menor intervenção adequada e aplicar segurança antes de coaching."
ideal_response_characteristics: ["natural", "específica", "executável", "sem causalidade inventada"]
bad_response_patterns: ["moralização", "lista longa", "certeza falsa", "diagnóstico"]
example_response: "Observação: A execução voltou a subir após um período de queda. Hipótese: Algum ajuste recente pode estar ajudando. Confiança ainda depende da qualidade dos registros. Ação: preservar o ajuste e observar por mais um ciclo."
status: "generated"
requires_human_review: true
index_eligible: false
---

# Caso case-f-009

## Notas de avaliação

O avaliador deve verificar seleção de playbook, uso do contexto, calibragem de confiança, modo de referência e eventual escalonamento.
