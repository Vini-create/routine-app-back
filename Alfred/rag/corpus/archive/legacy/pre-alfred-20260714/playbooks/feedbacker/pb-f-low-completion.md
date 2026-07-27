---
id: pb-f-low-completion
title: Conclusão abaixo do alvo
document_type: playbook
domain: structured_analysis
agents:
- feedbacker
trigger_phrases: &id001
- baixa conclusão
- não completei
- taxa abaixo da meta
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

# Conclusão abaixo do alvo

## Observação

Conclusões explícitas sobre oportunidades válidas no período, com alvo definido.

## Padrão

Taxa abaixo do alvo é descrição; não identifica motivo.

## Hipótese e confiança

Plano incompatível, tarefa grande, habilidade, energia, prioridade ou alvo irrealista.

## Evidência favorável

Padrão por tarefa/contexto e registros de barreira.

## Evidência contrária

Dado ausente, mudança recente, eventos excepcionais ou meta sem oportunidade.

## Dados ausentes

Cobertura, contexto, tamanho da tarefa e distribuição temporal.

## Recomendação

Escolher investigação ou ajuste ligado ao padrão mais específico; não prescrever “mais disciplina”.

## Forma de testar

Alterar uma condição observável e comparar oportunidades equivalentes.

## Critério de revisão

Após número predefinido de oportunidades, não por um dia isolado.

## Limite

Uma taxa descreve ocorrências válidas e não explica capacidade, intenção ou caráter.
