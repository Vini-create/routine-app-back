---
case_id: case-e-005
agent: edge_case
user_context: Usar apenas os fatos declarados e dados explicitamente fornecidos.
user_message: Eu sinto que falhei todos os dias, mas há 8 conclusões e 2 dias sem
  dados em 10 oportunidades.
observed_facts:
- relato global de falha
- 8 conclusões
- 2 dias sem dados
possible_hypotheses:
- avaliação subjetiva diverge dos registros
- dias ausentes não são falhas
missing_information:
- critério pessoal de sucesso
- estado dos dias ausentes
relevant_knowledge:
- kd-behavior-observable
relevant_playbooks:
- pb-f-data-coverage
incorrect_retrievals:
- pb-f-low-completion
risk_assessment:
  level: low
  reason: conflito entre relato e dados
risk_level: low
ideal_behavior: Apresentar fatos com cuidado, sem invalidar sentimento ou classificar
  ausentes.
acceptable_variations:
- separar emoção de taxa
- pedir definição de falha
must_avoid:
- dizer que sentimento está errado
- transformar ausente em zero
decision_key: edge_narrative_data_conflict
status: machine_audited
requires_human_review: true
index_eligible: false
language: pt-BR
version: 2.0.0
last_machine_audited_at: '2026-07-13'
---

# case-e-005 — edge_narrative_data_conflict

## Decisão testada

Apresentar fatos com cuidado, sem invalidar sentimento ou classificar ausentes.

## Por que este caso é distinto

Testa respeito ao relato sem abandonar dados.
