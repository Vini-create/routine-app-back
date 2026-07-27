---
id: pb-a-cannot-start
title: Não consegue iniciar uma tarefa
document_type: playbook
domain: coaching
agents:
- alfred
trigger_phrases: &id001
- não consigo começar
- fico organizando e não começo
- travado na primeira etapa
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
- kd-behavior-observable
- kd-procrastination-map
- kd-action-planning
candidate_techniques:
- tech-action-planning
- tech-graded-tasks
- tech-restructure-environment
---

# Não consegue iniciar uma tarefa

## Critérios de ativação

Existe tarefa escolhida e uma oportunidade recente em que o início não ocorreu.

## Situações semelhantes que não devem ativá-lo

Não ativar para falta de tempo comprovada, sonolência importante, dor, meta recusada ou tarefa sem instrução básica.

## O que pode estar acontecendo

Podem existir ambiguidade do primeiro passo, habilidade insuficiente, aversividade, medo de avaliação ou preparação periférica recompensadora.

## O que ainda não sabemos

O que ocorreu no último momento de início; se a pessoa sabia o primeiro passo; se tinha material, tempo e habilidade.

## Árvore de decisão

- Se o primeiro passo é desconhecido, definir uma ação reconhecível.
- Se falta habilidade, buscar exemplo, instrução ou ajuda antes de reduzir.
- Se preparação substitui execução, limitar preparação e iniciar pelo produto da tarefa.
- Se dificuldade excede capacidade demonstrada, usar tarefa graduada com critério de avanço.
- Se a pessoa não quer a meta, mudar para escolha da meta.

## Conhecimentos relacionados

`kd-behavior-observable`, `kd-procrastination-map`, `kd-action-planning`

## Técnicas candidatas e condições

`tech-action-planning`, `tech-graded-tasks`, `tech-restructure-environment`

## Como responder naturalmente

Referir-se ao episódio específico e oferecer somente a intervenção ligada à hipótese mais sustentada.

## Quando não fazer pergunta

Quando o relato já contém tarefa, antecedente, desvio e restrição; apresentar a decisão diretamente.

## Quando não oferecer solução

Quando a pessoa pede apenas escuta ou ainda não escolheu realizar a tarefa.

## Quando usar referência científica

Somente se a pessoa pedir fundamento ou contestar a distinção entre intenção e execução.

## Quando encerrar ou mudar de fluxo

Encerrar ao definir o próximo início. Mudar para segurança se houver sofrimento agudo ou sintoma.

## Segurança

Escalonar somente se o episódio trouxer sofrimento agudo, sintoma ou perigo; dificuldade de início isolada não é crise.
