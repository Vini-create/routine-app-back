---
case_id: case-a-002
agent: alfred
user_context: Usar apenas os fatos declarados e dados explicitamente fornecidos.
user_message: Leio o enunciado de programação, mas não sei como transformar o requisito
  em código.
observed_facts:
- usuário abriu e leu a tarefa
- declara não saber converter requisito em código
possible_hypotheses:
- lacuna de habilidade
- requisito ambíguo
missing_information:
- qual conceito falta
- se há exemplo ou documentação autorizada
relevant_knowledge:
- kd-behavior-observable
relevant_playbooks:
- pb-a-cannot-start
incorrect_retrievals:
- tech-graded-tasks
- kd-procrastination-map
risk_assessment:
  level: low
  reason: barreira de habilidade provável
risk_level: low
ideal_behavior: Encaminhar primeiro para instrução/exemplo; não reduzir a tarefa como
  se fosse aversão.
acceptable_variations:
- pedir o requisito específico
- sugerir ajuda técnica adequada
must_avoid:
- diagnosticar procrastinação
- usar hábito mínimo
decision_key: start_missing_skill
status: machine_audited
requires_human_review: true
index_eligible: false
language: pt-BR
version: 2.0.0
last_machine_audited_at: '2026-07-13'
---

# case-a-002 — start_missing_skill

## Decisão testada

Encaminhar primeiro para instrução/exemplo; não reduzir a tarefa como se fosse aversão.

## Por que este caso é distinto

Distingue incapacidade técnica de resistência ao início.
