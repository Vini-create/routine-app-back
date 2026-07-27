---
id: "pb-f-good-overload"
title: "Bom desempenho com sinais de sobrecarga"
document_type: "playbook"
domain: "structured_analysis"
subtopics: ["good-overload"]
agents: ["feedbacker"]
use_when: ["A conclusão é alta, mas coexistem pouco sono ou carga crescente."]
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

# Bom desempenho com sinais de sobrecarga

## Observação factual

A conclusão é alta, mas coexistem pouco sono ou carga crescente. Incluir numerador, denominador, período e comparação quando disponíveis.

## Hipótese

O desempenho pode ter custo não sustentável. Esta hipótese não deve aparecer como causa confirmada.

## Nível de confiança

Calcular a partir de quantidade, consistência, qualidade e atualidade dos registros. Evitar precisão falsa; justificar a faixa verbal e numérica.

## Evidência disponível

Datas, status explícito de conclusão, duração planejada e realizada, tipo de dia e mudanças registradas.

## Evidência ausente

Contexto, energia, localização, prioridade, dependências externas e motivo do dado ausente, salvo quando já coletados.

## Recomendação

Reduzir carga e proteger recuperação.

## Ação sugerida

Executar um teste por sete dias ou um ciclo relevante, mantendo as demais variáveis tão estáveis quanto for razoável.

## Formato de saída

```json
{
  "observation": "A conclusão é alta, mas coexistem pouco sono ou carga crescente.",
  "hypothesis": "O desempenho pode ter custo não sustentável.",
  "confidence": 0.62,
  "available_evidence": ["registros do período"],
  "missing_information": ["contexto", "energia"],
  "recommended_action": "Reduzir carga e proteger recuperação."
}
```

## Conhecimento relacionado

`kd-sleep-performance`.

## Erros a evitar

Confundir correlação com causa, omissão com falha, alta conclusão com sustentabilidade ou baixa conclusão com falta de caráter.
