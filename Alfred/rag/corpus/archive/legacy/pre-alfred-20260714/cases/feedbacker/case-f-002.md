---
case_id: case-f-002
agent: feedbacker
user_context: Usar apenas os fatos declarados e dados explicitamente fornecidos.
user_message: O aplicativo ficou offline por quatro dias e mostra zero nesses dias.
observed_facts:
- offline por quatro dias
- sistema mostra zero
possible_hypotheses:
- zeros podem ser artefato de ingestão
missing_information:
- se houve registro local ou execução fora do sistema
relevant_knowledge: []
relevant_playbooks:
- pb-f-data-coverage
incorrect_retrievals:
- pb-f-low-completion
risk_assessment:
  level: low
  reason: falha técnica conhecida
risk_level: low
ideal_behavior: Tratar dias como ausentes/indeterminados, não não conclusão.
acceptable_variations:
- recalcular excluindo dias
- aguardar sincronização
must_avoid:
- penalizar taxa
- inferir abandono
decision_key: feedback_missing_not_failure
status: machine_audited
requires_human_review: true
index_eligible: false
language: pt-BR
version: 2.0.0
last_machine_audited_at: '2026-07-13'
---

# case-f-002 — feedback_missing_not_failure

## Decisão testada

Tratar dias como ausentes/indeterminados, não não conclusão.

## Por que este caso é distinto

Testa semântica do dado, não desempenho.
