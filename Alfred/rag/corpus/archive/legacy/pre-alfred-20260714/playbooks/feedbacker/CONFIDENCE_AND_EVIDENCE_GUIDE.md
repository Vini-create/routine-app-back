---
id: pb-f-confidence-guide
title: Confiança e evidência do Feedbacker
document_type: playbook
domain: structured_analysis
agents:
- feedbacker
trigger_phrases: &id001
- nível de confiança
- dados suficientes
- quão certo é o padrão
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

# Confiança e evidência do Feedbacker

## Observação

Cobertura, número de oportunidades, duração, consistência e qualidade do dado.

## Padrão

Confiança descreve suporte da hipótese nos dados disponíveis; não probabilidade numérica nem certeza causal.

## Hipótese e confiança

low: poucos registros, janela curta, contradição ou muitas alternativas; moderate: repetição suficiente, mas variáveis relevantes faltam; high: padrão consistente, boa cobertura, poucas alternativas e relação diretamente observável.

## Evidência favorável

Repetição em oportunidades comparáveis, dado contrário procurado e definição estável.

## Evidência contrária

Dias ou contextos incompatíveis, dados ausentes, mudança de regra, amostra selecionada.

## Dados ausentes

Denominador, cobertura, período, comparadores e variáveis que mudariam a recomendação.

## Recomendação

Nunca elevar confiança por intuição. Mesmo high deve usar “os registros mostram”, não “a causa é”.

## Forma de testar

Declarar qual novo dado aumentaria ou reduziria a confiança.

## Critério de revisão

Recalcular quando entra período relevante ou muda a definição.

## Limite

A confiança qualifica suporte nos registros, nunca chance clínica, verdade subjetiva ou causalidade.
