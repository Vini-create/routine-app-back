---
id: "pb-f-low-completion"
title: "Baixa taxa de conclusão"
document_type: "playbook"
domain: "structured_analysis"
subtopics: ["low-completion"]
agents: ["feedbacker"]
use_when: ["A taxa de conclusão está abaixo do alvo no período."]
avoid_when: ["quando os dados não distinguem ausência de registro e falha"]
user_states: []
evidence_level: "operational_evidence_informed"
source_ids: []
language: "pt-BR"
version: "1.0.0"
status: "generated"
risk_level: "low"
citation_required: false
created_at: "2026-07-13"
last_reviewed_at: "2026-07-13"
requires_human_review: true
index_eligible: false
---

# Baixa taxa de conclusão

## Observação factual

A taxa de conclusão está abaixo do alvo no período. Incluir numerador, denominador, período e comparação quando disponíveis.

## Hipótese

O plano pode exceder capacidade ou conter barreiras recorrentes. Esta hipótese não deve aparecer como causa confirmada.

## Nível de confiança

Calcular a partir de quantidade, consistência, qualidade e atualidade dos registros. Evitar precisão falsa; justificar a faixa verbal e numérica.

## Evidência disponível

Datas, status explícito de conclusão, duração planejada e realizada, tipo de dia e mudanças registradas.

## Evidência ausente

Contexto, energia, localização, prioridade, dependências externas e motivo do dado ausente, salvo quando já coletados.

## Recomendação

Reduzir escopo e testar uma mudança por sete dias.

## Ação sugerida

Executar um teste por sete dias ou um ciclo relevante, mantendo as demais variáveis tão estáveis quanto for razoável.

## Formato de saída

```json
{
  "observation": "A taxa de conclusão está abaixo do alvo no período.",
  "hypothesis": "O plano pode exceder capacidade ou conter barreiras recorrentes.",
  "confidence": 0.62,
  "available_evidence": ["registros do período"],
  "missing_information": ["contexto", "energia"],
  "recommended_action": "Reduzir escopo e testar uma mudança por sete dias."
}
```

## Conhecimento relacionado

`kd-behavior-feedback`.

## Erros a evitar

Confundir correlação com causa, omissão com falha, alta conclusão com sustentabilidade ou baixa conclusão com falta de caráter.
