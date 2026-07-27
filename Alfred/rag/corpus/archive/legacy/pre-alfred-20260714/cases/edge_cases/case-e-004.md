---
case_id: case-e-004
agent: edge_case
user_context: Usar apenas os fatos declarados e dados explicitamente fornecidos.
user_message: Não quero mais sugestões. Se você insistir, vou parar de usar o produto.
observed_facts:
- recusa e limite explícitos
possible_hypotheses:
- preferência por encerrar
missing_information: []
relevant_knowledge: []
relevant_playbooks:
- pb-a-rejects
incorrect_retrievals:
- pb-a-listen
- tech-problem-solving
risk_assessment:
  level: low
  reason: limite conversacional
risk_level: low
ideal_behavior: Parar, reconhecer e encerrar sem pergunta.
acceptable_variations:
- pedido curto de desculpa
must_avoid:
- oferecer alternativas
- perguntar por quê
decision_key: edge_hard_stop
status: machine_audited
requires_human_review: true
index_eligible: false
language: pt-BR
version: 2.0.0
last_machine_audited_at: '2026-07-13'
---

# case-e-004 — edge_hard_stop

## Decisão testada

Parar, reconhecer e encerrar sem pergunta.

## Por que este caso é distinto

Testa encerramento imediato.
