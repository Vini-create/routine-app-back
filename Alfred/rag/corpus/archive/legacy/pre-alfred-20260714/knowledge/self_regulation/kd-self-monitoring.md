---
id: kd-self-monitoring
title: Automonitoramento mínimo orientado a decisão
document_type: knowledge
domain: self_regulation
agents:
- alfred
- feedbacker
retrieval_terms:
- o que devo registrar
- acompanhar hábito
- meus dados mostram
- registro demais
- não sei se melhorou
decision_questions:
- Qual decisão concreta poderá mudar depois de observar este registro?
- Qual variável mínima e qual janela distinguem mudança de oscilação comum?
- Que dado ausente tornaria a conclusão pouco confiável?
source_ids:
- src-bcttv1-2013
- src-self-regulation-2020
supported_claims:
- claim_id: monitoring-definition
  source_ids:
  - src-bcttv1-2013
  evidence_strength: canonical_framework
- claim_id: monitoring-evidence-limit
  source_ids:
  - src-self-regulation-2020
  evidence_strength: systematic_review
language: pt-BR
version: 2.0.1
status: machine_audited
requires_human_review: true
index_eligible: false
risk_level: low
created_at: '2026-07-13'
last_machine_audited_at: '2026-07-14'
---

# Automonitoramento mínimo orientado a decisão

## Definição operacional

Automonitoramento é registrar o comportamento ou resultado definido pela própria pessoa para responder a uma decisão futura. O registro deve ter variável, frequência e período de revisão explícitos.

## O que este conceito não significa

Não é vigilância contínua, coleta por precaução nem evidência causal. Mais granularidade pode aumentar carga, ansiedade e abandono.

## Evidências principais

A BCTTv1 define automonitoramento como método para a pessoa acompanhar comportamento ou resultado. A meta-revisão encontrou componentes de autorregulação promissores em alguns domínios, mas sem consistência universal e com qualidade variável.

## Mapeamento das evidências

- Afirmação: A taxonomia distingue automonitoramento de comportamento e de resultado.
  - Fonte: `src-bcttv1-2013`
  - Suporte/força: `canonical_framework`
- Afirmação: Automonitoramento apareceu entre componentes úteis, mas efeitos variaram por comportamento e população.
  - Fonte: `src-self-regulation-2020`
  - Suporte/força: `systematic_review`

## Decisão que este conhecimento apoia

Escolher a menor variável e período que permitem decidir manter, ajustar ou interromper uma estratégia.

## Dados necessários

Pergunta de decisão; variável observável; forma de coleta; carga; período; privacidade; possibilidade de dado ausente.

## Perguntas úteis para decidir

- Qual decisão concreta poderá mudar depois de observar este registro?
- Qual variável mínima e qual janela distinguem mudança de oscilação comum?
- Que dado ausente tornaria a conclusão pouco confiável?

## Sinais compatíveis

Discussão depende de frequência ou contexto desconhecidos; a pessoa usa impressão global contradita por episódios; registro atual não muda decisões.

## Explicações alternativas

Às vezes um único exemplo basta. Dados do aplicativo podem refletir falha de sincronização, não ausência do comportamento.

## Processo de aplicação

1. Escrever a decisão que o dado deve informar.
2. Escolher uma variável diretamente ligada a ela.
3. Definir registro de baixa fricção e dado ausente explícito.
4. Fixar período e data de revisão.
5. Comparar com alternativas e contexto.
6. Parar a coleta quando não muda mais a decisão ou gera custo desproporcional.

## Quando aplicar

Quando uma decisão depende de padrão e os dados existentes são insuficientes.

## Quando evitar

Evitar em comportamento compulsivo, alimentação, peso ou sofrimento quando o rastreio pode agravar risco; usar fluxo especializado.

## Aplicação pelo Alfred

Explica por que registrar e oferece uma forma mínima, sempre aceitando recusa.

## Aplicação pelo Feedbacker

Distingue zero, não conclusão e dado ausente; informa cobertura e período antes de qualquer padrão.

## Exemplo contextualizado

“Durante cinco dias, registre apenas a hora em que começou a primeira tarefa — não produtividade nem humor. Isso basta para verificar se o conflito está no horário planejado.”

## Limitações

Autorrelato e dados digitais têm erros. Monitoramento pode alterar o comportamento e não demonstra por que ele ocorreu.

## Fontes

`src-bcttv1-2013`, `src-self-regulation-2020`.
