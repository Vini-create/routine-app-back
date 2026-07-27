---
case_id: case-a-007
agent: alfred
user_context: Usar apenas os fatos declarados e dados explicitamente fornecidos.
user_message: Hoje eu só preciso reclamar. Não quero dica nem pergunta.
observed_facts:
- pedido explícito de escuta
- recusa de dica e pergunta
possible_hypotheses:
- preferência conversacional suficiente
missing_information: []
relevant_knowledge: []
relevant_playbooks:
- pb-a-listen
incorrect_retrievals:
- pb-a-cannot-start
- tech-problem-solving
risk_assessment:
  level: low
  reason: sem sinal de risco no enunciado
risk_level: low
ideal_behavior: Responder ao conteúdo com escuta e não oferecer solução ou pergunta.
acceptable_variations:
- reconhecer o pedido
- deixar espaço
must_avoid:
- terminar com pergunta
- propor teste
- citar estudo
decision_key: listen_without_solution
status: machine_audited
requires_human_review: true
index_eligible: false
language: pt-BR
version: 2.0.0
last_machine_audited_at: '2026-07-13'
---

# case-a-007 — listen_without_solution

## Decisão testada

Responder ao conteúdo com escuta e não oferecer solução ou pergunta.

## Por que este caso é distinto

Testa quando a melhor ação é não intervir.
