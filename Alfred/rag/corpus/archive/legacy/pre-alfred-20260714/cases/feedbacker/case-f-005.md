---
case_id: case-f-005
agent: feedbacker
user_context: Usar apenas os fatos declarados e dados explicitamente fornecidos.
user_message: Em seis semanas, a ação ocorreu em 10 de 12 fins de semana e 3 de 20
  dias úteis.
observed_facts:
- seis semanas
- 10/12 fins de semana
- 3/20 dias úteis
possible_hypotheses:
- contexto de dia útil influencia oportunidade
- tarefas/denominadores podem diferir
missing_information:
- compromissos, deslocamento e horário por tipo de dia
relevant_knowledge:
- kd-action-planning
relevant_playbooks:
- pb-f-day-pattern
- pb-f-confidence-guide
incorrect_retrievals:
- pb-f-low-completion
risk_assessment:
  level: low
  reason: padrão contextual repetido
risk_level: low
ideal_behavior: Descrever diferença com confiança moderate e buscar variável de contexto,
  sem nomear causa.
acceptable_variations:
- plano A/B
- comparar janelas
must_avoid:
- dizer que trabalho causa falha
- usar média geral apenas
decision_key: feedback_day_context
status: machine_audited
requires_human_review: true
index_eligible: false
language: pt-BR
version: 2.0.0
last_machine_audited_at: '2026-07-13'
---

# case-f-005 — feedback_day_context

## Decisão testada

Descrever diferença com confiança moderate e buscar variável de contexto, sem nomear causa.

## Por que este caso é distinto

Testa estratificação relevante.
