---
id: pb-a-no-time
title: Capacidade insuficiente ou conflito de prioridades
document_type: playbook
domain: coaching
agents:
- alfred
trigger_phrases: &id001
- não tenho tempo
- minha agenda não cabe
- tudo é prioridade
- estou sobrecarregado
use_when: *id001
source_ids: []
language: pt-BR
version: 2.0.0
status: machine_audited
requires_human_review: true
index_eligible: false
risk_level: low
last_machine_audited_at: '2026-07-13'
related_knowledge:
- kd-goal-review
- kd-action-planning
candidate_techniques:
- tech-problem-solving
- tech-goal-review
---

# Capacidade insuficiente ou conflito de prioridades

## Critérios de ativação

Compromissos e durações conhecidos excedem as janelas disponíveis ou duas prioridades competem pelo mesmo recurso.

## Situações semelhantes que não devem ativá-lo

Não ativar apenas porque uma tarefa foi adiada; investigar clareza, energia e recusa legítima.

## O que pode estar acontecendo

Pode haver excesso real de demanda, estimativa ruim, prioridade não explicitada ou obrigação que precisa ser renegociada.

## O que ainda não sabemos

Compromissos fixos, durações, prazo, consequência de adiar e o que pode ser removido ou negociado.

## Árvore de decisão

- Se a soma excede a capacidade, remover, delegar, adiar ou renegociar antes de otimizar.
- Se duas prioridades têm consequências diferentes, torná-las explícitas e escolher.
- Se a estimativa é incerta, medir uma execução antes de refazer toda a agenda.
- Se a meta perdeu prioridade, revisar ou pausar; não reduzi-la indefinidamente.

## Conhecimentos relacionados

`kd-goal-review`, `kd-action-planning`

## Técnicas candidatas e condições

`tech-problem-solving`, `tech-goal-review`

## Como responder naturalmente

Mostrar o conflito concreto e nomear o custo da escolha; não vender produtividade como criação de tempo.

## Quando não fazer pergunta

Quando a incompatibilidade já é aritmética e a única decisão restante é qual compromisso mover.

## Quando não oferecer solução

Quando a limitação depende de decisão de empregador, cuidador ou profissional e não há margem autorizada.

## Quando usar referência científica

Normalmente sem referência; usar evidência apenas para explicar revisão de metas sob pedido.

## Quando encerrar ou mudar de fluxo

Encerrar com uma decisão de capacidade, não com uma lista de truques.

## Segurança

Não sugerir cortar sono, cuidado essencial, tratamento ou medida de segurança para fazer a agenda caber.
