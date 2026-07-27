---
id: pb-f-recovery-trend
title: Queda e recuperação ao longo do tempo
document_type: playbook
domain: structured_analysis
agents:
- feedbacker
trigger_phrases: &id001
- recuperei depois da queda
- tendência de retomada
- um dia ruim
use_when: *id001
source_ids: []
language: pt-BR
version: 2.0.0
status: machine_audited
requires_human_review: true
index_eligible: false
risk_level: low
last_machine_audited_at: '2026-07-13'
---

# Queda e recuperação ao longo do tempo

## Observação

Série temporal com baseline, queda, mudança e recuperação.

## Padrão

Um dia não é tendência; recuperação requer retorno sustentado em oportunidades comparáveis.

## Hipótese e confiança

Mudança de contexto, adaptação de plano ou oscilação aleatória.

## Evidência favorável

Retorno consistente após intervenção/documentada.

## Evidência contrária

Poucos pontos, tarefas diferentes ou regressão à média.

## Dados ausentes

O que mudou e se a oportunidade permaneceu comparável.

## Recomendação

Descrever a retomada sem atribuir causa à estratégia sem contraste.

## Forma de testar

Manter condição e observar continuidade; procurar dado que contrarie.

## Critério de revisão

Após janela equivalente ao baseline.

## Limite

Melhora temporal após uma mudança não demonstra que a mudança causou a melhora.
