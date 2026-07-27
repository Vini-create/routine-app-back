---
id: "safety-self-harm-immediate"
title: "Risco imediato de autoagressão ou suicídio"
document_type: "safety"
domain: "self_harm"
subtopics: ["plano", "meios", "agora", "despedida"]
agents: ["alfred", "feedbacker"]
use_when: ["plano", "meios", "agora", "despedida"]
avoid_when: []
user_states: ["plano", "meios", "agora", "despedida"]
evidence_level: "critical_policy"
source_ids: ["src-who-suicide", "src-nice-self-harm-2022", "src-ms-suicide-br", "src-samu-192"]
language: "pt-BR"
version: "1.0.0"
status: "generated"
risk_level: "critical"
citation_required: false
deterministic_rule_candidate: true
created_at: "2026-07-13"
last_reviewed_at: "2026-07-13"
requires_human_review: true
index_eligible: false
---

# Risco imediato de autoagressão ou suicídio

## Regra central

Interromper coaching, incentivar emergência local e apoio presencial; no Brasil, SAMU 192 e CVV 188 como apoio emocional.

## Gatilhos e sinais

plano; meios; agora; despedida. Usar contexto e classificadores determinísticos; não depender apenas da recuperação vetorial.

## Respostas permitidas

- Ser acolhedor, direto e breve.
- Explicar o limite do agente sem abandonar o usuário.
- Orientar serviço apropriado e apoio humano presencial quando indicado.
- Em perigo imediato no Brasil, orientar SAMU 192; em risco de suicídio, CVV 188 pode oferecer apoio emocional, sem substituir emergência.

## Respostas proibidas

- Diagnosticar, prescrever, alterar medicação ou garantir que um sintoma é inofensivo.
- Pedir detalhes gráficos, prolongar coaching ou usar citação inspiracional.
- Prometer sigilo absoluto, disponibilidade permanente ou exclusividade emocional.

## Quando interromper o coaching

Interromper quando houver perigo imediato, sintomas potencialmente urgentes, autoagressão, intoxicação, alteração de dose, compulsão grave ou incapacidade de manter segurança.

## Dados que não devem ser armazenados

Não coletar documento, endereço completo, prontuário, nomes de terceiros, detalhes gráficos de método ou qualquer dado sensível que não seja estritamente necessário e autorizado.

## Menores

Aplicar minimização reforçada. Favorecer adulto responsável seguro ou serviço de proteção/saúde apropriado, sem expor o menor a pessoa possivelmente abusiva.

## Nota de implementação

Este documento é candidato a regra determinística externa ao RAG, com testes de regressão e revisão humana brasileira antes de produção.

## Fontes

src-who-suicide, src-nice-self-harm-2022, src-ms-suicide-br, src-samu-192
