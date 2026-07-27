---
case_id: case-a-005
agent: alfred
user_context: Usar apenas os fatos declarados e dados explicitamente fornecidos.
user_message: Minha família decidiu que eu devo correr uma maratona, mas eu só quero
  melhorar meu fôlego.
observed_facts:
- meta da maratona veio da família
- usuário endossa melhorar fôlego, não a prova
possible_hypotheses:
- meta imposta
- objetivo próprio pode usar outra atividade
missing_information:
- consequências reais de recusar
- preferências e limitações
relevant_knowledge:
- kd-chosen-vs-imposed
- kd-goal-review
relevant_playbooks:
- pb-a-demotivated
incorrect_retrievals:
- pb-a-perfectionist
- tech-goal-review
risk_assessment:
  level: low
  reason: decisão de autonomia sem risco indicado
risk_level: low
ideal_behavior: Separar o valor escolhido da modalidade imposta e oferecer manter,
  trocar ou recusar.
acceptable_variations:
- explorar consequência familiar
- ajudar a formular limite
must_avoid:
- motivar para maratona
- chamar resistência de autossabotagem
decision_key: imposed_goal_legitimate_resistance
status: machine_audited
requires_human_review: true
index_eligible: false
language: pt-BR
version: 2.0.0
last_machine_audited_at: '2026-07-13'
---

# case-a-005 — imposed_goal_legitimate_resistance

## Decisão testada

Separar o valor escolhido da modalidade imposta e oferecer manter, trocar ou recusar.

## Por que este caso é distinto

Testa resistência legítima, não baixa motivação genérica.
