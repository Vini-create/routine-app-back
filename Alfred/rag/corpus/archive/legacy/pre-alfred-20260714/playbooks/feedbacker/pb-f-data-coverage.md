---
id: pb-f-data-coverage
title: Cobertura de dados e ausência de registro
document_type: playbook
domain: structured_analysis
agents:
- feedbacker
trigger_phrases: &id001
- sem dados
- dias não registrados
- zero ou ausente
- poucos registros
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

# Cobertura de dados e ausência de registro

## Observação

Oportunidades esperadas, registros presentes, zeros explícitos e falhas técnicas.

## Padrão

Ausência de registro não equivale a não execução; cobertura baixa limita qualquer taxa.

## Hipótese e confiança

Pode haver não registro, sincronização, mudança de rotina ou não execução — hipóteses separadas.

## Evidência favorável

Logs de ingestão, marcação explícita de não conclusão, oportunidade confirmada.

## Evidência contrária

Dias fora da rotina, aplicativo sem sincronizar, comportamento feito fora do sistema.

## Dados ausentes

Denominador e motivo de ausência.

## Recomendação

Apresentar cobertura primeiro; não calcular tendência forte com cobertura insuficiente.

## Forma de testar

Melhorar registro por período mínimo ou cruzar com fonte autorizada.

## Critério de revisão

Reavaliar quando a cobertura representar as oportunidades-alvo.

## Limite

Sem cobertura representativa, o Feedbacker deve se abster de classificar desempenho.
