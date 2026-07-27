---
case_id: case-f-009
agent: feedbacker
user_context: Usar apenas os fatos declarados e dados explicitamente fornecidos.
user_message: Após uma semana baixa, houve três dias altos. Isso prova que a nova
  técnica funcionou?
observed_facts:
- uma semana baixa
- três dias altos
- técnica nova
possible_hypotheses:
- recuperação real
- oscilação
- regressão à média
- contexto mudou
missing_information:
- baseline comparável
- dados contrários
- outras mudanças
relevant_knowledge: []
relevant_playbooks:
- pb-f-recovery-trend
- pb-f-confidence-guide
incorrect_retrievals:
- pb-f-low-completion
risk_assessment:
  level: low
  reason: dados insuficientes para causalidade
risk_level: low
ideal_behavior: Descrever melhora recente com confiança low e negar prova causal.
acceptable_variations:
- definir janela equivalente
- procurar continuidade
must_avoid:
- atribuir causa
- usar porcentagem de confiança
decision_key: feedback_recovery_not_causality
status: machine_audited
requires_human_review: true
index_eligible: false
language: pt-BR
version: 2.0.0
last_machine_audited_at: '2026-07-13'
---

# case-f-009 — feedback_recovery_not_causality

## Decisão testada

Descrever melhora recente com confiança low e negar prova causal.

## Por que este caso é distinto

Testa melhora sem causalidade.
