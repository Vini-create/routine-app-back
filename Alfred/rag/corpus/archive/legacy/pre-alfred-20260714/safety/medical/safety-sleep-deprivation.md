---
id: "safety-sleep-deprivation"
title: "Privação de sono e desempenho"
document_type: "safety"
domain: "medical"
subtopics: ["durmo quatro horas", "virar a noite", "dirigir com sono"]
agents: ["alfred", "feedbacker"]
use_when: ["durmo quatro horas", "virar a noite", "dirigir com sono"]
avoid_when: []
user_states: ["durmo quatro horas", "virar a noite", "dirigir com sono"]
evidence_level: "critical_policy"
source_ids: ["src-sleep-aasm-2015"]
language: "pt-BR"
version: "1.0.0"
status: "generated"
risk_level: "high"
citation_required: false
deterministic_rule_candidate: true
created_at: "2026-07-13"
last_reviewed_at: "2026-07-13"
requires_human_review: true
index_eligible: false
---

# Privação de sono e desempenho

## Regra central

Não otimizar rotina baseada em privação; priorizar segurança e avaliação se persistente.

## Gatilhos e sinais

durmo quatro horas; virar a noite; dirigir com sono. Usar contexto e classificadores determinísticos; não depender apenas da recuperação vetorial.

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

src-sleep-aasm-2015
