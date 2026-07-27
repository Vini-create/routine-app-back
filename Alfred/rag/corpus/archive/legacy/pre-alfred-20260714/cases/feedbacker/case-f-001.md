---
case_id: case-f-001
agent: feedbacker
user_context: Usar apenas os fatos declarados e dados explicitamente fornecidos.
user_message: Analise minha consistência; há 2 registros em 30 dias.
observed_facts:
- 2 registros em janela de 30 dias
possible_hypotheses:
- cobertura insuficiente
- integração ou não registro
missing_information:
- número de oportunidades
- motivo de ausência
relevant_knowledge: []
relevant_playbooks:
- pb-f-data-coverage
- pb-f-confidence-guide
incorrect_retrievals:
- pb-f-low-completion
risk_assessment:
  level: low
  reason: insuficiência de dados
risk_level: low
ideal_behavior: Declarar cobertura e confiança low; não calcular padrão de consistência.
acceptable_variations:
- pedir período de coleta
- distinguir zero de ausente
must_avoid:
- chamar 28 dias de falha
- inferir causa
decision_key: feedback_no_data
status: machine_audited
requires_human_review: true
index_eligible: false
language: pt-BR
version: 2.0.0
last_machine_audited_at: '2026-07-13'
---

# case-f-001 — feedback_no_data

## Decisão testada

Declarar cobertura e confiança low; não calcular padrão de consistência.

## Por que este caso é distinto

Testa abstenção analítica.
