---
case_id: case-f-007
agent: feedbacker
user_context: Usar apenas os fatos declarados e dados explicitamente fornecidos.
user_message: O prazo foi movido quatro vezes; em cada revisão consta 'não é minha
  prioridade'.
observed_facts:
- quatro reagendamentos
- mesmo motivo registrado
possible_hypotheses:
- meta perdeu prioridade
- meta pode ser imposta
missing_information:
- autoria da meta
- consequência de abandonar
relevant_knowledge:
- kd-goal-review
- kd-chosen-vs-imposed
relevant_playbooks:
- pb-f-postponed
incorrect_retrievals:
- pb-f-low-completion
risk_assessment:
  level: low
  reason: padrão de decisão não resolvida
risk_level: low
ideal_behavior: Recomendar revisão explícita, não novo prazo.
acceptable_variations:
- pausar ou abandonar como opções
- perguntar consequência
must_avoid:
- reagendar automaticamente
- moralizar
decision_key: feedback_postponement_priority
status: machine_audited
requires_human_review: true
index_eligible: false
language: pt-BR
version: 2.0.0
last_machine_audited_at: '2026-07-13'
---

# case-f-007 — feedback_postponement_priority

## Decisão testada

Recomendar revisão explícita, não novo prazo.

## Por que este caso é distinto

Testa revisão da existência da meta.
