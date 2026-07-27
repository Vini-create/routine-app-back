---
case_id: case-a-006
agent: alfred
user_context: Usar apenas os fatos declarados e dados explicitamente fornecidos.
user_message: O relatório atende todos os requisitos, mas revisei dez vezes e não
  envio porque uma frase pode ficar melhor.
observed_facts:
- requisitos declarados como atendidos
- dez revisões
- envio bloqueado por possível melhoria
possible_hypotheses:
- critério de pronto não aplicado
- medo de avaliação
missing_information:
- prazo
- consequência real de uma frase imperfeita
relevant_knowledge:
- kd-procrastination-map
- kd-goal-review
relevant_playbooks:
- pb-a-perfectionist
incorrect_retrievals:
- pb-a-cannot-start
- tech-graded-tasks
risk_assessment:
  level: low
  reason: sem sinal clínico; padrão de entrega específico
risk_level: low
ideal_behavior: Definir limite de revisão e decisão de envio sem rebaixar requisito
  real.
acceptable_variations:
- usar checklist já atendido
- marcar revisão final única
must_avoid:
- dizer apenas 'feito é melhor'
- diagnosticar OCD
decision_key: perfectionism_after_requirements
status: machine_audited
requires_human_review: true
index_eligible: false
language: pt-BR
version: 2.0.0
last_machine_audited_at: '2026-07-13'
---

# case-a-006 — perfectionism_after_requirements

## Decisão testada

Definir limite de revisão e decisão de envio sem rebaixar requisito real.

## Por que este caso é distinto

Distingue perfeccionismo de trabalho ainda incompleto.
