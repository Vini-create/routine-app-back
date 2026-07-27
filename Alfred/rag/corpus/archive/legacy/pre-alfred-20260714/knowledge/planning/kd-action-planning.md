---
id: kd-action-planning
title: Plano de ação executável
document_type: knowledge
domain: planning
agents:
- alfred
- feedbacker
retrieval_terms:
- sei o que quero mas não faço
- quando vou fazer
- planejar a tarefa
- não sei por onde começar
decision_questions:
- Qual ação reconhecível marca o início e qual resultado mínimo marca o fim?
- Em qual oportunidade real isso cabe sem competir com um compromisso fixo?
- O que precisa estar disponível antes de o bloco começar?
source_ids:
- src-bcttv1-2013
- src-self-regulation-2020
supported_claims:
- claim_id: action-plan-form
  source_ids:
  - src-bcttv1-2013
  evidence_strength: canonical_framework
- claim_id: self-regulation-variability
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

# Plano de ação executável

## Definição operacional

Plano de ação especifica comportamento, contexto, início e extensão suficiente para reconhecer a execução. Ele converte uma intenção em uma oportunidade agendada ou ancorada.

## O que este conceito não significa

Não é uma lista completa de desejos, uma agenda sem margem nem um plano de contingência. Especificidade não compensa falta de tempo, habilidade ou acesso.

## Evidências principais

A BCTTv1 define action planning como planejamento detalhado do desempenho. A meta-revisão de autorregulação encontrou apoio variável para planejamento e outros componentes; efeitos dependem de comportamento e população.

## Mapeamento das evidências

- Afirmação: Action planning inclui contexto e desempenho do comportamento.
  - Fonte: `src-bcttv1-2013`
  - Suporte/força: `canonical_framework`
- Afirmação: Componentes de autorregulação não foram consistentemente eficazes em todos os domínios.
  - Fonte: `src-self-regulation-2020`
  - Suporte/força: `systematic_review`

## Decisão que este conhecimento apoia

Determinar se falta operacionalização ou se outra barreira precisa ser resolvida antes de planejar.

## Dados necessários

Comportamento-alvo; duração mínima realista; oportunidade; compromissos fixos; materiais; dependências; margem disponível.

## Perguntas úteis para decidir

- Qual ação reconhecível marca o início e qual resultado mínimo marca o fim?
- Em qual oportunidade real isso cabe sem competir com um compromisso fixo?
- O que precisa estar disponível antes de o bloco começar?

## Sinais compatíveis

Intenção clara acompanhada de “quando der”; tarefas sem primeiro passo ou blocos colocados sobre compromissos existentes.

## Explicações alternativas

A falha pode ser capacidade insuficiente, aversão, ambiente, meta imposta ou plano excessivo — casos em que apenas detalhar não resolve.

## Processo de aplicação

1. Definir um comportamento reconhecível.
2. Escolher uma oportunidade real, por horário ou evento.
3. Fixar ponto de início e limite de duração/escopo.
4. Conferir conflito com agenda, materiais e deslocamento.
5. Registrar como será reconhecida a conclusão.
6. Executar uma vez e revisar o plano com base no atrito encontrado.

## Quando aplicar

Quando a intenção existe e a oportunidade é controlável, mas a execução permanece vaga.

## Quando evitar

Quando o usuário ainda não escolheu a meta, não tem recursos básicos ou precisa de um plano se–então para obstáculo previsível.

## Aplicação pelo Alfred

Ajuda a fechar uma decisão concreta e encerra; não transforma uma tarefa em planejamento de toda a vida.

## Aplicação pelo Feedbacker

Pode detectar sobreposição com compromissos e comparar duração planejada com janelas existentes, sem inferir motivação.

## Exemplo contextualizado

“Depois de guardar o jantar, você abrirá a lista 3 e resolverá apenas as questões 1 e 2. O bloco termina em 25 minutos, mesmo que a segunda questão fique incompleta.”

## Limitações

Planos detalhados podem falhar em rotinas imprevisíveis. A precisão deve servir à execução, não virar trabalho adicional.

## Fontes

`src-bcttv1-2013`, `src-self-regulation-2020`.
