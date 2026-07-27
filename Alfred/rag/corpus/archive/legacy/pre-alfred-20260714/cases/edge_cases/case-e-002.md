---
case_id: case-e-002
agent: edge_case
user_context: Usar apenas os fatos declarados e dados explicitamente fornecidos.
user_message: Preciso de disciplina para fazer o trabalho, mas a instrução diz apenas
  'desenvolva o projeto'.
observed_facts:
- usuário pede disciplina
- instrução não define produto
possible_hypotheses:
- falta de clareza
- possível falta de requisito
missing_information:
- critérios de entrega
- exemplo esperado
relevant_knowledge:
- kd-behavior-observable
- kd-action-planning
relevant_playbooks:
- pb-a-cannot-start
incorrect_retrievals:
- kd-habit-formation
- pb-a-demotivated
risk_assessment:
  level: low
  reason: ambiguidade da tarefa
risk_level: low
ideal_behavior: Buscar critério e primeiro produto, não trabalhar motivação.
acceptable_variations:
- pedir rubrica
- formular pergunta ao responsável
must_avoid:
- chamar de procrastinação
- hábito mínimo
decision_key: edge_discipline_vs_clarity
status: machine_audited
requires_human_review: true
index_eligible: false
language: pt-BR
version: 2.0.0
last_machine_audited_at: '2026-07-13'
---

# case-e-002 — edge_discipline_vs_clarity

## Decisão testada

Buscar critério e primeiro produto, não trabalhar motivação.

## Por que este caso é distinto

Testa rótulo popular contra barreira observável.
