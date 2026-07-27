---
id: pb-f-day-pattern
title: Diferença entre tipos de dia
document_type: playbook
domain: structured_analysis
agents:
- feedbacker
trigger_phrases: &id001
- funciona no fim de semana
- falha durante a semana
- padrão por dia
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

# Diferença entre tipos de dia

## Observação

Taxas por tipo de dia com oportunidades e cobertura comparáveis.

## Padrão

Diferença repetida entre contextos, não simples comparação de médias sem denominador.

## Hipótese e confiança

Compromissos, deslocamento, sono, ambiente ou janela podem diferir.

## Evidência favorável

Múltiplas semanas e diferença consistente.

## Evidência contrária

Poucos dias, feriados, mudança de regra ou tarefas diferentes.

## Dados ausentes

Variáveis que diferem entre tipos de dia.

## Recomendação

Adaptar plano ao tipo de dia; não impor o plano do fim de semana à semana.

## Forma de testar

Usar plano A/B e observar oportunidades equivalentes.

## Critério de revisão

Após pelo menos mais de um ciclo de cada tipo de dia.

## Limite

Diferença entre dias não identifica qual variável contextual produziu a diferença.
