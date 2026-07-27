---
id: kd-if-then-plans
title: Planos se–então para obstáculos previsíveis
document_type: knowledge
domain: planning
agents:
- alfred
- feedbacker
retrieval_terms:
- se acontecer isso o que faço
- plano b
- sempre sou interrompido
- quando o gatilho aparecer
decision_questions:
- Qual obstáculo se repetiu o suficiente para merecer uma contingência?
- Como você reconhecerá, no momento, que o gatilho ocorreu?
- Qual resposta continua viável e segura exatamente nessa situação?
source_ids:
- src-ii-2006
- src-intention-behavior-2006
supported_claims:
- claim_id: ii-format-effect
  source_ids:
  - src-ii-2006
  evidence_strength: meta_analysis
- claim_id: intention-gap
  source_ids:
  - src-intention-behavior-2006
  evidence_strength: meta_analysis
language: pt-BR
version: 2.0.1
status: machine_audited
requires_human_review: true
index_eligible: false
risk_level: low
created_at: '2026-07-13'
last_machine_audited_at: '2026-07-14'
---

# Planos se–então para obstáculos previsíveis

## Definição operacional

Uma intenção de implementação liga uma situação discriminável a uma resposta: “Se Y ocorrer, então farei X”. É usada para iniciar, proteger ou retomar uma ação diante de um obstáculo previsível.

## O que este conceito não significa

Não é um cronograma comum, pensamento positivo nem uma lista extensa de exceções. Requer intenção prévia e uma resposta realmente disponível.

## Evidências principais

A meta-análise de Gollwitzer e Sheeran sintetizou 94 testes e encontrou efeito positivo médio a grande sobre alcance de metas. A síntese de Webb e Sheeran mostra que mudar intenção, sozinho, produz mudança comportamental menor, apoiando a distinção entre querer e executar.

## Mapeamento das evidências

- Afirmação: Planos se–então especificam quando, onde e como agir e tiveram efeito agregado positivo sobre alcance de metas.
  - Fonte: `src-ii-2006`
  - Suporte/força: `meta_analysis`
- Afirmação: Mudanças em intenção não se traduzem integralmente em mudanças de comportamento.
  - Fonte: `src-intention-behavior-2006`
  - Suporte/força: `meta_analysis`

## Decisão que este conhecimento apoia

Escolher uma única contingência de alta frequência e uma resposta curta; se o obstáculo não é previsível, usar planejamento flexível em vez desta técnica.

## Dados necessários

Meta escolhida; situação observável; frequência; controle sobre a resposta; custo da alternativa; conflito com segurança.

## Perguntas úteis para decidir

- Qual obstáculo se repetiu o suficiente para merecer uma contingência?
- Como você reconhecerá, no momento, que o gatilho ocorreu?
- Qual resposta continua viável e segura exatamente nessa situação?

## Sinais compatíveis

Mesmo obstáculo antecede várias falhas: reunião atrasada, transporte perdido, celular ao alcance ou retorno de viagem.

## Explicações alternativas

Obstáculo raro, mal definido ou fora de controle pode exigir reserva de capacidade, negociação ou mudança da meta.

## Processo de aplicação

1. Confirmar que a meta foi escolhida.
2. Selecionar um obstáculo recorrente e reconhecível.
3. Definir resposta pequena e viável nesse contexto.
4. Escrever uma única frase se–então.
5. Checar conflitos e exceções de segurança.
6. Revisar depois de ocorrências reais do gatilho, não apenas após passagem do tempo.

## Quando aplicar

Quando há um gatilho previsível ligado a início, interrupção ou retomada.

## Quando evitar

Não usar para riscos médicos, crises, eventos vagos ou dezenas de contingências simultâneas.

## Aplicação pelo Alfred

Propõe a contingência na linguagem do usuário e confirma se a resposta cabe naquele momento.

## Aplicação pelo Feedbacker

Só avalia o plano quando há ocorrências do gatilho; ausência do evento não conta como falha.

## Exemplo contextualizado

“Se a reunião passar das 18h30, em vez de cancelar o estudo eu farei a revisão de dez cartões no ônibus; a lista de exercícios fica para o próximo bloco normal.”

## Limitações

O efeito agregado varia por meta e contexto. Planos rígidos podem ser inúteis quando oportunidades mudam continuamente.

## Fontes

`src-ii-2006`, `src-intention-behavior-2006`.
