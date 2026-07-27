---
id: "pb-f-concentrated"
title: "Concentração de tarefas em um período"
document_type: "playbook"
domain: "structured_analysis"
subtopics: ["concentrated"]
agents: ["feedbacker"]
use_when: ["Grande parte das tarefas está concentrada em uma janela curta."]
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

# Concentração de tarefas em um período

## Observação factual

Grande parte das tarefas está concentrada em uma janela curta. Incluir numerador, denominador, período e comparação quando disponíveis.

## Hipótese

A concentração pode aumentar conflitos quando há imprevistos. Esta hipótese não deve aparecer como causa confirmada.

## Nível de confiança

Calcular a partir de quantidade, consistência, qualidade e atualidade dos registros. Evitar precisão falsa; justificar a faixa verbal e numérica.

## Evidência disponível

Datas, status explícito de conclusão, duração planejada e realizada, tipo de dia e mudanças registradas.

## Evidência ausente

Contexto, energia, localização, prioridade, dependências externas e motivo do dado ausente, salvo quando já coletados.

## Recomendação

Redistribuir itens flexíveis e preservar margem.

## Ação sugerida

Executar um teste por sete dias ou um ciclo relevante, mantendo as demais variáveis tão estáveis quanto for razoável.

## Formato de saída

```json
{
  "observation": "Grande parte das tarefas está concentrada em uma janela curta.",
  "hypothesis": "A concentração pode aumentar conflitos quando há imprevistos.",
  "confidence": 0.62,
  "available_evidence": ["registros do período"],
  "missing_information": ["contexto", "energia"],
  "recommended_action": "Redistribuir itens flexíveis e preservar margem."
}
```

## Conhecimento relacionado

`kd-energy-overload`.

## Erros a evitar

Confundir correlação com causa, omissão com falha, alta conclusão com sustentabilidade ou baixa conclusão com falta de caráter.
