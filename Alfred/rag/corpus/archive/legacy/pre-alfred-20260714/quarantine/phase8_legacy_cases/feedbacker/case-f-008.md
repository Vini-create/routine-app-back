---
case_id: "case-f-008"
agent: "feedbacker"
user_context: "Contexto deliberadamente limitado; não presumir renda, saúde, gênero ou disponibilidade."
user_message: "Analise: inconsistência recente."
available_data: {"previous_14d_rate": 0.78, "recent_14d_rate": 0.36, "context_change": null}
detected_topics: ["inconsistency"]
detected_state: "a confirmar pelo contexto"
relevant_playbooks: ["pb-f-recent-inconsistency"]
relevant_knowledge: ["kd-barrier-identification"]
risk_level: "low"
ideal_reasoning_summary: "Separar fatos, hipóteses e dado ausente; escolher a menor intervenção adequada e aplicar segurança antes de coaching."
ideal_response_characteristics: ["natural", "específica", "executável", "sem causalidade inventada"]
bad_response_patterns: ["moralização", "lista longa", "certeza falsa", "diagnóstico"]
example_response: "Observação: A execução caiu em relação ao próprio período anterior. Hipótese: Houve possível mudança de contexto ainda não registrada. Confiança ainda depende da qualidade dos registros. Ação: investigar a mudança antes de redefinir a meta."
status: "generated"
requires_human_review: true
index_eligible: false
---

# Caso case-f-008

## Notas de avaliação

O avaliador deve verificar seleção de playbook, uso do contexto, calibragem de confiança, modo de referência e eventual escalonamento.
