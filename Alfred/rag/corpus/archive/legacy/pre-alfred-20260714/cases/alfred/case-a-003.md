---
case_id: case-a-003
agent: alfred
user_context: Usar apenas os fatos declarados e dados explicitamente fornecidos.
user_message: Trabalho até 18h, cuido da minha filha até 21h e coloquei treino, estudo
  e um curso entre 19h e 22h.
observed_facts:
- janelas se sobrepõem a cuidado fixo
- três atividades disputam o mesmo período
possible_hypotheses:
- plano excede capacidade
- prioridades não escolhidas
missing_information:
- quais itens têm prazo
- o que pode ser movido ou negociado
relevant_knowledge:
- kd-goal-review
- kd-action-planning
relevant_playbooks:
- pb-a-no-time
incorrect_retrievals:
- pb-a-cannot-start
- tech-prompts-cues
risk_assessment:
  level: low
  reason: incompatibilidade de capacidade diretamente observável
risk_level: low
ideal_behavior: Nomear a impossibilidade do plano e exigir escolha/renegociação antes
  de otimizar.
acceptable_variations:
- comparar consequências
- propor remover um item
must_avoid:
- dizer para acordar mais cedo
- encaixar microtarefas sem consentimento
decision_key: capacity_arithmetic_conflict
status: machine_audited
requires_human_review: true
index_eligible: false
language: pt-BR
version: 2.0.0
last_machine_audited_at: '2026-07-13'
---

# case-a-003 — capacity_arithmetic_conflict

## Decisão testada

Nomear a impossibilidade do plano e exigir escolha/renegociação antes de otimizar.

## Por que este caso é distinto

Testa excesso real de capacidade, não percepção subjetiva de falta de tempo.
