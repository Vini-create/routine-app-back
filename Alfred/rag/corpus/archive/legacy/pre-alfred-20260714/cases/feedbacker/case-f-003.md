---
case_id: case-f-003
agent: feedbacker
user_context: Usar apenas os fatos declarados e dados explicitamente fornecidos.
user_message: Concluí 4 de 12 sessões; seis não têm qualquer registro.
observed_facts:
- 4 conclusões
- 12 oportunidades declaradas
- 6 sem estado
possible_hypotheses:
- taxa não identificável até classificar ausências
missing_information:
- estado das outras duas
- significado dos seis ausentes
relevant_knowledge: []
relevant_playbooks:
- pb-f-data-coverage
- pb-f-low-completion
incorrect_retrievals:
- pb-f-confidence-guide
risk_assessment:
  level: low
  reason: denominador parcialmente indeterminado
risk_level: low
ideal_behavior: Apresentar intervalo possível e resolver cobertura antes de explicar
  baixa conclusão.
acceptable_variations:
- relatar 4 confirmações
- mostrar cenários conforme ausentes
must_avoid:
- afirmar taxa de 33% como definitiva
- causalidade
decision_key: feedback_low_completion_with_missing
status: machine_audited
requires_human_review: true
index_eligible: false
language: pt-BR
version: 2.0.0
last_machine_audited_at: '2026-07-13'
---

# case-f-003 — feedback_low_completion_with_missing

## Decisão testada

Apresentar intervalo possível e resolver cobertura antes de explicar baixa conclusão.

## Por que este caso é distinto

Combina baixa conclusão e ausência sem colapsá-las.
