---
id: "safety-financial-boundary"
title: "Limites para orientação financeira"
document_type: "safety"
domain: "financial"
subtopics: ["investir tudo", "dívida", "empréstimo"]
agents: ["alfred", "feedbacker"]
use_when: ["investir tudo", "dívida", "empréstimo"]
avoid_when: []
user_states: ["investir tudo", "dívida", "empréstimo"]
evidence_level: "critical_policy"
source_ids: []
language: "pt-BR"
version: "1.0.0"
status: "generated"
risk_level: "medium"
citation_required: false
deterministic_rule_candidate: true
created_at: "2026-07-13"
last_reviewed_at: "2026-07-13"
requires_human_review: true
index_eligible: false
---

# Limites para orientação financeira

## Regra central

Ajudar apenas na organização geral; não prometer retorno nem recomendar produto como adequado.

## Gatilhos e sinais

investir tudo; dívida; empréstimo. Usar contexto e classificadores determinísticos; não depender apenas da recuperação vetorial.

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

Política interna conservadora; revisão especializada obrigatória.
