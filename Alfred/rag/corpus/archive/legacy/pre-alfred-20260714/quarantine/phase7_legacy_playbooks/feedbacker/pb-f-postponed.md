---
id: "pb-f-postponed"
title: "Metas repetidamente adiadas"
document_type: "playbook"
domain: "structured_analysis"
subtopics: ["postponed"]
agents: ["feedbacker"]
use_when: ["A mesma meta teve o prazo movido várias vezes."]
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

# Metas repetidamente adiadas

## Observação factual

A mesma meta teve o prazo movido várias vezes. Incluir numerador, denominador, período e comparação quando disponíveis.

## Hipótese

Escopo, prioridade ou dependência externa podem estar mal definidos. Esta hipótese não deve aparecer como causa confirmada.

## Nível de confiança

Calcular a partir de quantidade, consistência, qualidade e atualidade dos registros. Evitar precisão falsa; justificar a faixa verbal e numérica.

## Evidência disponível

Datas, status explícito de conclusão, duração planejada e realizada, tipo de dia e mudanças registradas.

## Evidência ausente

Contexto, energia, localização, prioridade, dependências externas e motivo do dado ausente, salvo quando já coletados.

## Recomendação

Redefinir marco ou pausar explicitamente.

## Ação sugerida

Executar um teste por sete dias ou um ciclo relevante, mantendo as demais variáveis tão estáveis quanto for razoável.

## Formato de saída

```json
{
  "observation": "A mesma meta teve o prazo movido várias vezes.",
  "hypothesis": "Escopo, prioridade ou dependência externa podem estar mal definidos.",
  "confidence": 0.62,
  "available_evidence": ["registros do período"],
  "missing_information": ["contexto", "energia"],
  "recommended_action": "Redefinir marco ou pausar explicitamente."
}
```

## Conhecimento relacionado

`kd-goal-decomposition`.

## Erros a evitar

Confundir correlação com causa, omissão com falha, alta conclusão com sustentabilidade ou baixa conclusão com falta de caráter.
