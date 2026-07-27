---
case_id: case-a-010
agent: alfred
user_context: Usar apenas os fatos declarados e dados explicitamente fornecidos.
user_message: Minha escala alterna manhã e noite; o único evento estável é pegar o
  ônibus depois do turno.
observed_facts:
- horários variam
- evento pós-turno é recorrente
possible_hypotheses:
- âncora por evento pode ser mais adequada que horário fixo
missing_information:
- segurança e cansaço no trajeto
- ação possível no ônibus
relevant_knowledge:
- kd-action-planning
- kd-if-then-plans
relevant_playbooks:
- pb-a-irregular-schedule
incorrect_retrievals:
- kd-habit-formation
- pb-a-no-time
risk_assessment:
  level: medium
  reason: turnos exigem checagem de sono, mas sem risco explícito
risk_level: medium
ideal_behavior: Usar evento ou tipo de dia, após checar se a ação é segura e viável.
acceptable_variations:
- plano A/B
- âncora ao ônibus
must_avoid:
- impor 6h todos os dias
- prometer hábito automático
decision_key: irregular_event_anchor
status: machine_audited
requires_human_review: true
index_eligible: false
language: pt-BR
version: 2.0.0
last_machine_audited_at: '2026-07-13'
---

# case-a-010 — irregular_event_anchor

## Decisão testada

Usar evento ou tipo de dia, após checar se a ação é segura e viável.

## Por que este caso é distinto

Testa estabilidade por evento em vez de relógio.
