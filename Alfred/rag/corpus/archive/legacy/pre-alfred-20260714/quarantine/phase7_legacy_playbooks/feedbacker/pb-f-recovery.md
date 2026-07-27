---
id: "pb-f-recovery"
title: "Recuperação após queda"
document_type: "playbook"
domain: "structured_analysis"
subtopics: ["recovery"]
agents: ["feedbacker"]
use_when: ["A execução voltou a subir após um período de queda."]
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

# Recuperação após queda

## Observação factual

A execução voltou a subir após um período de queda. Incluir numerador, denominador, período e comparação quando disponíveis.

## Hipótese

Algum ajuste recente pode estar ajudando. Esta hipótese não deve aparecer como causa confirmada.

## Nível de confiança

Calcular a partir de quantidade, consistência, qualidade e atualidade dos registros. Evitar precisão falsa; justificar a faixa verbal e numérica.

## Evidência disponível

Datas, status explícito de conclusão, duração planejada e realizada, tipo de dia e mudanças registradas.

## Evidência ausente

Contexto, energia, localização, prioridade, dependências externas e motivo do dado ausente, salvo quando já coletados.

## Recomendação

Preservar o ajuste e observar por mais um ciclo.

## Ação sugerida

Executar um teste por sete dias ou um ciclo relevante, mantendo as demais variáveis tão estáveis quanto for razoável.

## Formato de saída

```json
{
  "observation": "A execução voltou a subir após um período de queda.",
  "hypothesis": "Algum ajuste recente pode estar ajudando.",
  "confidence": 0.62,
  "available_evidence": ["registros do período"],
  "missing_information": ["contexto", "energia"],
  "recommended_action": "Preservar o ajuste e observar por mais um ciclo."
}
```

## Conhecimento relacionado

`kd-relapse-recovery`.

## Erros a evitar

Confundir correlação com causa, omissão com falha, alta conclusão com sustentabilidade ou baixa conclusão com falta de caráter.
