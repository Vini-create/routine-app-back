---
case_id: case-f-004
agent: feedbacker
user_context: Usar apenas os fatos declarados e dados explicitamente fornecidos.
user_message: Há 11 horas de tarefas planejadas numa janela livre de 6 horas.
observed_facts:
- 11 horas planejadas
- 6 horas livres
possible_hypotheses:
- incompatibilidade direta de capacidade
missing_information:
- prioridades
- durações estimadas
- margem
relevant_knowledge:
- kd-goal-review
relevant_playbooks:
- pb-f-capacity-mismatch
incorrect_retrievals:
- pb-f-low-completion
risk_assessment:
  level: low
  reason: relação diretamente observável
risk_level: low
ideal_behavior: Classificar incompatibilidade com confiança high sobre o conflito,
  sem inferir por que foi criado.
acceptable_variations:
- pedir prioridade
- recomendar remover/mover escopo
must_avoid:
- confiança numérica
- dizer que usuário é irrealista
decision_key: feedback_capacity_direct
status: machine_audited
requires_human_review: true
index_eligible: false
language: pt-BR
version: 2.0.0
last_machine_audited_at: '2026-07-13'
---

# case-f-004 — feedback_capacity_direct

## Decisão testada

Classificar incompatibilidade com confiança high sobre o conflito, sem inferir por que foi criado.

## Por que este caso é distinto

Permite high para relação observável sem causalidade.
