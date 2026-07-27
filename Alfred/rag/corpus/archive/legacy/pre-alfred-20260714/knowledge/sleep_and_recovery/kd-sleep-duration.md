---
id: kd-sleep-duration
title: 'Duração do sono: referência geral e limites'
document_type: knowledge
domain: sleep_and_recovery
agents:
- alfred
- feedbacker
retrieval_terms:
- quantas horas dormir
- durmo quatro horas
- sono suficiente
- preciso dormir menos
- recuperar sono
decision_questions:
- Quantas horas foram efetivamente dormidas em um dia típico, e isso é padrão ou uma noite isolada?
- Há sonolência ao dirigir ou operar máquinas, ou algum sintoma importante que mude a prioridade para segurança?
- Turno, fragmentação, condição de saúde ou medicação tornam a referência populacional insuficiente?
source_ids:
- src-sleep-aasm-2015
- src-sleep-nsf-2015
supported_claims:
- claim_id: adult-sleep-consensus
  source_ids:
  - src-sleep-aasm-2015
  evidence_strength: institutional_guideline
- claim_id: age-ranges
  source_ids:
  - src-sleep-nsf-2015
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

# Duração do sono: referência geral e limites

## Definição operacional

Duração do sono é o tempo efetivamente dormido em 24 horas. Para adultos saudáveis, consensos oferecem faixas populacionais; necessidade individual também depende de idade, saúde, qualidade e regularidade.

## O que este conceito não significa

Não é uma prescrição para uma pessoa, nem permite concluir transtorno por uma noite. Tempo na cama não equivale necessariamente a sono.

## Evidências principais

AASM/SRS recomenda que adultos durmam regularmente sete ou mais horas para promover saúde. A NSF propõe faixas por idade por consenso. Ambos explicitam contexto e limites; não sustentam cortar sono para produtividade.

## Mapeamento das evidências

- Afirmação: Consenso recomenda sete ou mais horas regulares para adultos saudáveis.
  - Fonte: `src-sleep-aasm-2015`
  - Suporte/força: `institutional_guideline`
- Afirmação: Painel multidisciplinar definiu faixas recomendadas por grupo etário.
  - Fonte: `src-sleep-nsf-2015`
  - Suporte/força: `institutional_guideline`

## Decisão que este conhecimento apoia

Decidir se a conversa pode permanecer em organização de rotina ou precisa de orientação para avaliação/segurança.

## Dados necessários

Idade; duração habitual; janela; sonolência diurna; direção/máquinas; sintomas; turno; duração do padrão; condição/medicação conhecida.

## Perguntas úteis para decidir

- Quantas horas foram efetivamente dormidas em um dia típico, e isso é padrão ou uma noite isolada?
- Há sonolência ao dirigir ou operar máquinas, ou algum sintoma importante que mude a prioridade para segurança?
- Turno, fragmentação, condição de saúde ou medicação tornam a referência populacional insuficiente?

## Sinais compatíveis

Sono habitual muito abaixo da referência, sonolência ao dirigir, desmaio, falta de ar, dor, mudança intensa ou prejuízo persistente.

## Explicações alternativas

Tempo curto pode ser pontual ou erro de medição; cansaço pode ter outras causas. Tempo adequado não exclui baixa qualidade ou condição médica.

## Processo de aplicação

1. Distinguir uma noite de padrão habitual.
2. Comparar apenas como referência populacional apropriada à idade.
3. Verificar impacto e sinais de risco.
4. Se não houver risco, identificar conflito concreto de agenda e preservar oportunidade de sono.
5. Se houver sonolência em atividade perigosa ou sintoma importante, interromper coaching e usar segurança.
6. Evitar recomendar suplemento, medicamento ou diagnóstico.

## Quando aplicar

Para referência geral e organização de horários sem sintomas preocupantes.

## Quando evitar

Não individualizar necessidade, tratar insônia ou alterar medicação; risco ao dirigir exige ação imediata de segurança.

## Aplicação pelo Alfred

Pode apresentar a faixa como referência e priorizar segurança, sem competir com profissional de saúde.

## Aplicação pelo Feedbacker

Relata duração, cobertura e tendência; não chama correlação entre sono e desempenho de causa confirmada.

## Exemplo contextualizado

“Quatro horas por noite há duas semanas está bem abaixo da referência geral para adultos e você relatou cochilar no trânsito. Não vou otimizar sua agenda agora: pare de dirigir e procure ajuda segura para o deslocamento e avaliação de saúde.”

## Limitações

Consensos populacionais não medem necessidade individual. Qualidade, distúrbios, turnos e condições clínicas exigem avaliação profissional.

## Fontes

`src-sleep-aasm-2015`, `src-sleep-nsf-2015`.
