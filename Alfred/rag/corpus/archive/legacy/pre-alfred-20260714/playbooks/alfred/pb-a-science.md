---
id: pb-a-science
title: Pedido explícito de evidência
document_type: playbook
domain: coaching
agents:
- alfred
trigger_phrases: &id001
- qual é a fonte
- me mostre estudos
- isso tem evidência
- você está inventando
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
- kd-habit-formation
- kd-procrastination-map
- kd-retrieval-practice
- kd-spaced-practice
candidate_techniques: []
---

# Pedido explícito de evidência

## Critérios de ativação

O usuário pede origem, qualidade, prova ou limite de uma afirmação identificável.

## Situações semelhantes que não devem ativá-lo

Não ativar para pedido vago de motivação nem responder com referências não relacionadas.

## O que pode estar acontecendo

É uma solicitação epistemológica, não oposição; a melhor resposta pode ser reconhecer que a evidência não sustenta a alegação.

## O que ainda não sabemos

Qual afirmação está em disputa, população/contexto relevante e profundidade desejada.

## Árvore de decisão

- Identificar a afirmação exata.
- Recuperar no máximo fontes que a sustentem diretamente.
- Explicar desenho, achado e limite.
- Se a fonte não responder à afirmação, dizer isso.
- Distinguir framework, associação, ensaio e meta-análise.

## Conhecimentos relacionados

`kd-goal-review`, `kd-habit-formation`, `kd-procrastination-map`, `kd-retrieval-practice`, `kd-spaced-practice`

## Técnicas candidatas e condições

Nenhuma por padrão; responder primeiro à afirmação e à evidência solicitada.

## Como responder naturalmente

Começar pela conclusão calibrada e fornecer fonte rastreável; evitar lista decorativa de estudos.

## Quando não fazer pergunta

Quando a afirmação contestada já está explícita.

## Quando não oferecer solução

Quando o pedido é somente bibliográfico; não acrescentar coaching.

## Quando usar referência científica

Sempre explícita; DOI, PubMed/PMC ou instituição oficial, com limite próximo ao achado.

## Quando encerrar ou mudar de fluxo

Encerrar após responder a alegação ou declarar a lacuna.

## Segurança

Em saúde e risco, priorizar diretriz institucional atual e não transformar estudo em aconselhamento individual.
