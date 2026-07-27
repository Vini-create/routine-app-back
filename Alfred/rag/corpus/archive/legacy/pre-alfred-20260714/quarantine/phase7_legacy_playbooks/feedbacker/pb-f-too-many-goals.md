---
id: "pb-f-too-many-goals"
title: "Excesso de metas"
document_type: "playbook"
domain: "structured_analysis"
subtopics: ["too-many-goals"]
agents: ["feedbacker"]
use_when: ["O número de metas ativas supera o foco declarado."]
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

# Excesso de metas

## Observação factual

O número de metas ativas supera o foco declarado. Incluir numerador, denominador, período e comparação quando disponíveis.

## Hipótese

As metas podem competir por tempo e energia. Esta hipótese não deve aparecer como causa confirmada.

## Nível de confiança

Calcular a partir de quantidade, consistência, qualidade e atualidade dos registros. Evitar precisão falsa; justificar a faixa verbal e numérica.

## Evidência disponível

Datas, status explícito de conclusão, duração planejada e realizada, tipo de dia e mudanças registradas.

## Evidência ausente

Contexto, energia, localização, prioridade, dependências externas e motivo do dado ausente, salvo quando já coletados.

## Recomendação

Classificar em foco, manutenção e espera.

## Ação sugerida

Executar um teste por sete dias ou um ciclo relevante, mantendo as demais variáveis tão estáveis quanto for razoável.

## Formato de saída

```json
{
  "observation": "O número de metas ativas supera o foco declarado.",
  "hypothesis": "As metas podem competir por tempo e energia.",
  "confidence": 0.62,
  "available_evidence": ["registros do período"],
  "missing_information": ["contexto", "energia"],
  "recommended_action": "Classificar em foco, manutenção e espera."
}
```

## Conhecimento relacionado

`kd-goal-review`.

## Erros a evitar

Confundir correlação com causa, omissão com falha, alta conclusão com sustentabilidade ou baixa conclusão com falta de caráter.
