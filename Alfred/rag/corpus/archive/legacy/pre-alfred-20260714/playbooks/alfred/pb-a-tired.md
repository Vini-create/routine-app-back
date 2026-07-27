---
id: pb-a-tired
title: Cansaço, sono e queda de energia
document_type: playbook
domain: coaching
agents:
- alfred
trigger_phrases: &id001
- estou exausto
- sem energia
- dormindo pouco
- cochilo dirigindo
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
- kd-sleep-duration
- kd-behavior-observable
candidate_techniques: []
---

# Cansaço, sono e queda de energia

## Critérios de ativação

A pessoa relaciona execução a cansaço, sono curto ou sonolência.

## Situações semelhantes que não devem ativá-lo

Não chamar cansaço toda resistência ou perda de interesse; não diagnosticar causa.

## O que pode estar acontecendo

Pode ser privação de sono, carga, turno, doença, medicação, sofrimento ou oscilação pontual.

## O que ainda não sabemos

Duração e período; impacto; direção/máquinas; dor, falta de ar, desmaio, mudança intensa; condição conhecida.

## Árvore de decisão

- Se há sonolência ao dirigir/máquina ou sinal médico, interromper coaching e acionar segurança.
- Se há padrão persistente com prejuízo, orientar avaliação adequada sem diagnosticar.
- Se é oscilação pontual sem risco, proteger descanso e reagendar o que é negociável.
- Se o problema é agenda crônica, usar capacidade insuficiente depois da triagem.

## Conhecimentos relacionados

`kd-sleep-duration`, `kd-behavior-observable`

## Técnicas candidatas e condições

Nenhuma antes da triagem; organização de rotina só pode voltar depois de afastado o risco imediato.

## Como responder naturalmente

Priorizar segurança e recuperação sobre desempenho; não recomendar suplemento, medicamento ou técnica clínica.

## Quando não fazer pergunta

Quando a pessoa já relata risco imediato, como dirigir com sono: dar instrução segura sem prolongar coleta.

## Quando não oferecer solução

Quando pede causa médica ou alteração de tratamento.

## Quando usar referência científica

Usar referência institucional ao fornecer faixa geral de sono ou explicar risco.

## Quando encerrar ou mudar de fluxo

Mudar imediatamente para fluxo de segurança em atividade perigosa ou emergência.

## Segurança

Sonolência ao dirigir, desmaio, dor no peito ou falta de ar interrompem este playbook e acionam segurança.
