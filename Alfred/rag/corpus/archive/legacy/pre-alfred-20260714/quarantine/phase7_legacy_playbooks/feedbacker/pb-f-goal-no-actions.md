---
id: "pb-f-goal-no-actions"
title: "Meta sem ações associadas"
document_type: "playbook"
domain: "structured_analysis"
subtopics: ["goal-no-actions"]
agents: ["feedbacker"]
use_when: ["A meta não possui ações registradas."]
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

# Meta sem ações associadas

## Observação factual

A meta não possui ações registradas. Incluir numerador, denominador, período e comparação quando disponíveis.

## Hipótese

A intenção pode não estar operacionalizada. Esta hipótese não deve aparecer como causa confirmada.

## Nível de confiança

Calcular a partir de quantidade, consistência, qualidade e atualidade dos registros. Evitar precisão falsa; justificar a faixa verbal e numérica.

## Evidência disponível

Datas, status explícito de conclusão, duração planejada e realizada, tipo de dia e mudanças registradas.

## Evidência ausente

Contexto, energia, localização, prioridade, dependências externas e motivo do dado ausente, salvo quando já coletados.

## Recomendação

Vincular uma próxima ação observável.

## Ação sugerida

Executar um teste por sete dias ou um ciclo relevante, mantendo as demais variáveis tão estáveis quanto for razoável.

## Formato de saída

```json
{
  "observation": "A meta não possui ações registradas.",
  "hypothesis": "A intenção pode não estar operacionalizada.",
  "confidence": 0.62,
  "available_evidence": ["registros do período"],
  "missing_information": ["contexto", "energia"],
  "recommended_action": "Vincular uma próxima ação observável."
}
```

## Conhecimento relacionado

`kd-action-planning`.

## Erros a evitar

Confundir correlação com causa, omissão com falha, alta conclusão com sustentabilidade ou baixa conclusão com falta de caráter.
