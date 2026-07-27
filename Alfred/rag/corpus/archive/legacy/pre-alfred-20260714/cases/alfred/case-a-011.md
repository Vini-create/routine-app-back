---
case_id: case-a-011
agent: alfred
user_context: Usar apenas os fatos declarados e dados explicitamente fornecidos.
user_message: Completei 80% do plano por três semanas, mas o curso dobrou a carga.
  Devo desistir?
observed_facts:
- execução de 80%
- carga externa dobrou
possible_hypotheses:
- plano/prazo ficou incompatível
- meta pode continuar importante
missing_information:
- progresso
- custo
- possibilidade de extensão
relevant_knowledge:
- kd-goal-review
relevant_playbooks:
- pb-a-no-time
incorrect_retrievals:
- pb-a-demotivated
- kd-procrastination-map
risk_assessment:
  level: low
  reason: revisão de contexto
risk_level: low
ideal_behavior: Separar objetivo de plano e escolher manter com ajuste, pausar ou
  abandonar com critério.
acceptable_variations:
- sugerir extensão
- comparar custo
must_avoid:
- interpretar como falta de disciplina
- mandar insistir
decision_key: goal_review_context_change
status: machine_audited
requires_human_review: true
index_eligible: false
language: pt-BR
version: 2.0.0
last_machine_audited_at: '2026-07-13'
---

# case-a-011 — goal_review_context_change

## Decisão testada

Separar objetivo de plano e escolher manter com ajuste, pausar ou abandonar com critério.

## Por que este caso é distinto

Testa alteração externa após boa execução.
