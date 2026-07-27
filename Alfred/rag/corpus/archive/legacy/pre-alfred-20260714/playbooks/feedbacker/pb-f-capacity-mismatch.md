---
id: pb-f-capacity-mismatch
title: Plano excede janelas ou compromissos
document_type: playbook
domain: structured_analysis
agents:
- feedbacker
trigger_phrases: &id001
- rotina maior que o tempo
- horários incompatíveis
- agenda sobreposta
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

# Plano excede janelas ou compromissos

## Observação

Duração planejada, janelas livres, deslocamento, compromissos e margem.

## Padrão

Sobreposição ou soma maior que a capacidade é incompatibilidade diretamente observável.

## Hipótese e confiança

Estimativa ruim, excesso de itens ou compromisso que precisa ser negociado.

## Evidência favorável

Conflito de horário e duração em dados autorizados.

## Evidência contrária

Tarefa flexível, duração incorreta ou compromisso cancelado.

## Dados ausentes

Prioridade e consequência de mover cada item.

## Recomendação

Remover, mover, delegar ou reduzir escopo antes de otimizar sequência.

## Forma de testar

Aplicar o orçamento corrigido por uma semana típica.

## Critério de revisão

Comparar duração real e janelas; não avaliar motivação.

## Limite

Confiança alta pode valer para a sobreposição observada, não para o motivo de ela ter sido criada.
