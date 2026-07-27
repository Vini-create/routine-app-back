---
id: "pb-f-incompatible-times"
title: "Horários incompatíveis"
document_type: "playbook"
domain: "structured_analysis"
subtopics: ["incompatible-times"]
agents: ["feedbacker"]
use_when: ["A ação está planejada em horário ocupado por compromisso fixo."]
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

# Horários incompatíveis

## Observação factual

A ação está planejada em horário ocupado por compromisso fixo. Incluir numerador, denominador, período e comparação quando disponíveis.

## Hipótese

O conflito de agenda explica parte da não execução. Esta hipótese não deve aparecer como causa confirmada.

## Nível de confiança

Calcular a partir de quantidade, consistência, qualidade e atualidade dos registros. Evitar precisão falsa; justificar a faixa verbal e numérica.

## Evidência disponível

Datas, status explícito de conclusão, duração planejada e realizada, tipo de dia e mudanças registradas.

## Evidência ausente

Contexto, energia, localização, prioridade, dependências externas e motivo do dado ausente, salvo quando já coletados.

## Recomendação

Mover para janela real ou reduzir frequência.

## Ação sugerida

Executar um teste por sete dias ou um ciclo relevante, mantendo as demais variáveis tão estáveis quanto for razoável.

## Formato de saída

```json
{
  "observation": "A ação está planejada em horário ocupado por compromisso fixo.",
  "hypothesis": "O conflito de agenda explica parte da não execução.",
  "confidence": 0.62,
  "available_evidence": ["registros do período"],
  "missing_information": ["contexto", "energia"],
  "recommended_action": "Mover para janela real ou reduzir frequência."
}
```

## Conhecimento relacionado

`kd-action-planning`.

## Erros a evitar

Confundir correlação com causa, omissão com falha, alta conclusão com sustentabilidade ou baixa conclusão com falta de caráter.
