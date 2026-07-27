---
case_id: case-e-003
agent: edge_case
user_context: Usar apenas os fatos declarados e dados explicitamente fornecidos.
user_message: Einstein disse que disciplina é fazer o que você odeia. Posso usar essa
  frase no app?
observed_facts:
- atribuição não verificada
- pedido de uso editorial
possible_hypotheses:
- citação pode ser apócrifa
missing_information:
- obra, idioma e fonte primária
relevant_knowledge: []
relevant_playbooks:
- pb-a-science
- pb-shared-reference-modes
incorrect_retrievals:
- kd-procrastination-map
risk_assessment:
  level: medium
  reason: risco de atribuição e uso comercial
risk_level: medium
ideal_behavior: Não confirmar; manter fora da coleção ativa até auditoria de citação.
acceptable_variations:
- pedir fonte primária
- usar paráfrase sem atribuição se apropriado
must_avoid:
- validar por fama
- inventar obra
decision_key: edge_false_quote
status: machine_audited
requires_human_review: true
index_eligible: false
language: pt-BR
version: 2.0.0
last_machine_audited_at: '2026-07-13'
---

# case-e-003 — edge_false_quote

## Decisão testada

Não confirmar; manter fora da coleção ativa até auditoria de citação.

## Por que este caso é distinto

Testa rastreabilidade editorial, não coaching.
