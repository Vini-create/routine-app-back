---
id: "pb-f-too-many-habits"
title: "Excesso de hábitos"
document_type: "playbook"
domain: "structured_analysis"
subtopics: ["too-many-habits"]
agents: ["feedbacker"]
use_when: ["Há muitos hábitos ativos simultaneamente."]
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

# Excesso de hábitos

## Observação factual

Há muitos hábitos ativos simultaneamente. Incluir numerador, denominador, período e comparação quando disponíveis.

## Hipótese

A competição por atenção pode reduzir execução. Esta hipótese não deve aparecer como causa confirmada.

## Nível de confiança

Calcular a partir de quantidade, consistência, qualidade e atualidade dos registros. Evitar precisão falsa; justificar a faixa verbal e numérica.

## Evidência disponível

Datas, status explícito de conclusão, duração planejada e realizada, tipo de dia e mudanças registradas.

## Evidência ausente

Contexto, energia, localização, prioridade, dependências externas e motivo do dado ausente, salvo quando já coletados.

## Recomendação

Pausar parte e manter uma ou duas prioridades.

## Ação sugerida

Executar um teste por sete dias ou um ciclo relevante, mantendo as demais variáveis tão estáveis quanto for razoável.

## Formato de saída

```json
{
  "observation": "Há muitos hábitos ativos simultaneamente.",
  "hypothesis": "A competição por atenção pode reduzir execução.",
  "confidence": 0.62,
  "available_evidence": ["registros do período"],
  "missing_information": ["contexto", "energia"],
  "recommended_action": "Pausar parte e manter uma ou duas prioridades."
}
```

## Conhecimento relacionado

`kd-goal-conflicts`.

## Erros a evitar

Confundir correlação com causa, omissão com falha, alta conclusão com sustentabilidade ou baixa conclusão com falta de caráter.
