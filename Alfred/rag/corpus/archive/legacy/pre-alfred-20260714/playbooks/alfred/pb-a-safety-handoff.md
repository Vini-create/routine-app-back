---
id: pb-a-safety-handoff
title: Interrupção de coaching e encaminhamento ao fluxo de segurança
document_type: playbook
domain: coaching
agents:
- alfred
trigger_phrases: &id001
- vou me machucar
- dor no peito
- desmaiei
- dobrar remédio
- não consigo ficar seguro
use_when: *id001
source_ids: []
language: pt-BR
version: 2.0.0
status: machine_audited
requires_human_review: true
index_eligible: false
risk_level: high
last_machine_audited_at: '2026-07-13'
related_knowledge: []
candidate_techniques: []
---

# Interrupção de coaching e encaminhamento ao fluxo de segurança

## Critérios de ativação

Há declaração de perigo imediato, autoagressão, emergência médica, alteração de medicamento ou outro gatilho crítico.

## Situações semelhantes que não devem ativá-lo

Não substituir o classificador determinístico; este playbook documenta somente a decisão de interromper coaching.

## O que pode estar acontecendo

Não formular causa. O conteúdo requer resposta de segurança e, quando aplicável, serviço de emergência.

## O que ainda não sabemos

Somente informações mínimas exigidas pelo fluxo determinístico; não conduzir entrevista clínica improvisada.

## Árvore de decisão

- Interromper objetivo de produtividade/rotina.
- Acionar regra determinística apropriada antes da recuperação vetorial.
- Fornecer ação imediata e contatos locais verificados.
- Não diagnosticar, prescrever, garantir segurança ou prolongar coaching.
- Registrar o evento conforme política de privacidade e produto.

## Conhecimentos relacionados

Nenhum; aplicar política compartilhada.

## Técnicas candidatas e condições

Nenhuma técnica de coaching é permitida durante o handoff de segurança.

## Como responder naturalmente

Direta, humana e orientada à ação segura; sem citação filosófica, técnica de hábito ou lista longa.

## Quando não fazer pergunta

Quando uma ação imediata é clara; não atrasá-la com perguntas.

## Quando não oferecer solução

Não oferecer solução de coaching durante a crise.

## Quando usar referência científica

Usar apenas fonte institucional necessária e contato local verificado.

## Quando encerrar ou mudar de fluxo

O fluxo de coaching permanece interrompido até o risco imediato ter sido encaminhado.

## Segurança

Este playbook apenas interrompe coaching; a resposta concreta pertence à camada determinística validada e localizada.
