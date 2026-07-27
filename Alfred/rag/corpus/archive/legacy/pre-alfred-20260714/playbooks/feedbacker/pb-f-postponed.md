---
id: pb-f-postponed
title: Meta ou prazo repetidamente movido
document_type: playbook
domain: structured_analysis
agents:
- feedbacker
trigger_phrases: &id001
- adiada de novo
- prazo movido várias vezes
- meta postergada
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

# Meta ou prazo repetidamente movido

## Observação

Histórico de prazos, motivo registrado, execução e progresso.

## Padrão

Reagendamento repetido sem mudança de plano sugere decisão não resolvida.

## Hipótese e confiança

Prazo irrealista, baixa prioridade, dependência externa ou meta não endossada.

## Evidência favorável

Mesma justificativa e plano inalterado em vários ciclos.

## Evidência contrária

Mudanças externas reais e plano adaptado.

## Dados ausentes

Valor atual, controle e condição necessária.

## Recomendação

Solicitar revisão explícita: manter, alterar, pausar ou abandonar.

## Forma de testar

Aplicar a nova decisão, não apenas um novo prazo.

## Critério de revisão

Na data definida pela opção escolhida.

## Limite

Reagendamento repetido sustenta revisão da decisão, não diagnóstico de motivação.
