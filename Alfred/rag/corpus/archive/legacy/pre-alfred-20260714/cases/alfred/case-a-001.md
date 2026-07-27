---
case_id: case-a-001
agent: alfred
user_context: Usar apenas os fatos declarados e dados explicitamente fornecidos.
user_message: Abro o material de cálculo e passo quarenta minutos organizando arquivos
  sem estudar.
observed_facts:
- material foi aberto
- organização substituiu estudo por 40 minutos
possible_hypotheses:
- preparação periférica recompensadora
- primeiro passo incerto
- medo da dificuldade
missing_information:
- qual era a primeira questão
- se sabia resolvê-la
- o que fez em episódios anteriores
relevant_knowledge:
- kd-behavior-observable
- kd-procrastination-map
relevant_playbooks:
- pb-a-cannot-start
incorrect_retrievals:
- pb-a-no-time
- kd-sleep-duration
risk_assessment:
  level: low
  reason: sem sinal de dano; requer hipótese funcional calibrada
risk_level: low
ideal_behavior: Usar o episódio observado, distinguir organização de início e selecionar
  uma única hipótese testável.
acceptable_variations:
- limitar organização antes da primeira questão
- pedir um exemplo recente se o primeiro passo não estiver claro
must_avoid:
- chamar de preguiça
- prescrever rotina semanal
- afirmar medo sem dado
decision_key: start_preparation_substitution
status: machine_audited
requires_human_review: true
index_eligible: false
language: pt-BR
version: 2.0.0
last_machine_audited_at: '2026-07-13'
---

# case-a-001 — start_preparation_substitution

## Decisão testada

Usar o episódio observado, distinguir organização de início e selecionar uma única hipótese testável.

## Por que este caso é distinto

Testa preparação periférica, não apenas baixa execução.
