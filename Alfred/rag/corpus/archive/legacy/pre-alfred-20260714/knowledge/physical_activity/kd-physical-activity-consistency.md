---
id: kd-physical-activity-consistency
title: 'Atividade física: referência populacional sem prescrição'
document_type: knowledge
domain: physical_activity
agents:
- alfred
- feedbacker
retrieval_terms:
- quanto exercício fazer
- voltar a treinar
- consistência no treino
- 150 minutos
- começar atividade física
decision_questions:
- Há dor no peito, desmaio, falta de ar incomum, tontura ou lesão associada à atividade?
- Qual atividade foi escolhida e qual é a experiência atual da pessoa com ela?
- A principal restrição é oportunidade, acesso ou recuperação, ou existe uma decisão clínica ou de prescrição fora do escopo do produto?
source_ids:
- src-who-pa-2020
- src-cdc-pa-adults
supported_claims:
- claim_id: who-pa-guideline
  source_ids:
  - src-who-pa-2020
  evidence_strength: institutional_guideline
- claim_id: cdc-adult-guideline
  source_ids:
  - src-cdc-pa-adults
  evidence_strength: institutional_guideline
language: pt-BR
version: 2.0.1
status: machine_audited
requires_human_review: true
index_eligible: false
risk_level: medium
created_at: '2026-07-13'
last_machine_audited_at: '2026-07-14'
---

# Atividade física: referência populacional sem prescrição

## Definição operacional

Consistência em atividade física é participação repetida compatível com capacidade e contexto. Diretrizes fornecem metas populacionais de volume e intensidade; o produto pode apoiar organização, não prescrever treino.

## O que este conceito não significa

Não é treinar diariamente, compensar sessões perdidas ou progredir apesar de dor. A meta de 150 minutos não é ponto de partida obrigatório para cada pessoa.

## Evidências principais

OMS recomenda atividade aeróbica e fortalecimento por faixa etária e ressalta que alguma atividade é melhor que nenhuma. CDC apresenta a referência de 150 minutos moderados semanais para adultos e cautelas para condições crônicas ou início vigoroso.

## Mapeamento das evidências

- Afirmação: Diretriz estabelece recomendações populacionais de frequência, intensidade e duração por grupo.
  - Fonte: `src-who-pa-2020`
  - Suporte/força: `institutional_guideline`
- Afirmação: CDC informa referência semanal para adultos e orienta procurar profissional em condições específicas.
  - Fonte: `src-cdc-pa-adults`
  - Suporte/força: `institutional_guideline`

## Decisão que este conhecimento apoia

Decidir se cabe organizar oportunidades seguras ou se sintomas, condição clínica ou pedido de progressão exigem profissional.

## Dados necessários

Atividade pretendida; experiência; intensidade; tempo disponível; dor/sintomas; condição conhecida; orientação profissional; ambiente e equipamento.

## Perguntas úteis para decidir

- Há dor no peito, desmaio, falta de ar incomum, tontura ou lesão associada à atividade?
- Qual atividade foi escolhida e qual é a experiência atual da pessoa com ela?
- A principal restrição é oportunidade, acesso ou recuperação, ou existe uma decisão clínica ou de prescrição fora do escopo do produto?

## Sinais compatíveis

Pedido de compensar treino, salto abrupto de volume, dor, falta de ar incomum, desmaio, dor no peito ou atividade vigorosa após inatividade relevante.

## Explicações alternativas

Baixa frequência pode vir de deslocamento, custo, cuidado, preferência, clima ou recuperação; não implica falta de motivação.

## Processo de aplicação

1. Confirmar ausência de sintoma que acione segurança.
2. Identificar atividade escolhida e capacidade/experiência relatadas.
3. Usar diretriz apenas como referência, não como prescrição.
4. Organizar oportunidades realistas e dias de recuperação.
5. Não definir carga, técnica ou progressão clínica.
6. Revisar adesão e conforto; sintomas mudam imediatamente o fluxo.

## Quando aplicar

Para organização geral de uma atividade já considerada apropriada e sem sinal de alerta.

## Quando evitar

Dor no peito, desmaio, falta de ar incomum, lesão ou dúvida clínica devem sair do coaching.

## Aplicação pelo Alfred

Ajuda a encontrar horários e alternativas escolhidas; não manda “superar” dor nem cria planilha de treino individual.

## Aplicação pelo Feedbacker

Descreve frequência e distribuição semanal; não recomenda aumento de carga com base apenas em conclusão.

## Exemplo contextualizado

“As duas caminhadas já contam; você não precisa saltar direto para cinco dias. Como não há dor e essa atividade foi liberada para você, vamos apenas encontrar uma terceira janela que não elimine sua recuperação.”

## Limitações

Diretrizes são populacionais e não avaliam risco individual. O Winperium não substitui educação física, fisioterapia ou medicina.

## Fontes

`src-who-pa-2020`, `src-cdc-pa-adults`.
