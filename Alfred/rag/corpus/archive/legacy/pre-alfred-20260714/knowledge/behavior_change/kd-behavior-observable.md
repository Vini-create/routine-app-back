---
id: kd-behavior-observable
title: Do rótulo ao comportamento observável
document_type: knowledge
domain: behavior_change
agents:
- alfred
- feedbacker
retrieval_terms:
- sou indisciplinado
- não consigo manter nada
- sempre falho
- o que exatamente aconteceu
decision_questions:
- Qual foi o episódio mais recente em que a ação planejada não aconteceu?
- O que você fez nos minutos imediatamente antes e depois desse momento?
- Qual detalhe observável distinguiria falta de oportunidade de escolha por outra ação?
source_ids:
- src-bcto-2024
- src-bcttv1-2013
supported_claims:
- claim_id: observable-definition
  source_ids:
  - src-bcto-2024
  evidence_strength: canonical_framework
- claim_id: taxonomy-purpose
  source_ids:
  - src-bcttv1-2013
  evidence_strength: canonical_framework
language: pt-BR
version: 2.0.1
status: machine_audited
requires_human_review: true
index_eligible: false
risk_level: low
created_at: '2026-07-13'
last_machine_audited_at: '2026-07-14'
---

# Do rótulo ao comportamento observável

## Definição operacional

Traduzir uma avaliação global da pessoa em uma descrição que outra pessoa poderia reconhecer: ação ou ausência de ação, contexto, frequência, duração e consequência próxima. A unidade é o episódio comportamental, não a personalidade.

## O que este conceito não significa

Não significa negar emoções, reduzir a pessoa a métricas ou exigir registro exaustivo. Também não autoriza concluir a função do comportamento apenas por descrevê-lo.

## Evidências principais

BCTO e BCTTv1 oferecem vocabulário para descrever conteúdo observável e replicável de intervenções. São estruturas de descrição, não testes de causalidade nem instrumentos diagnósticos.

## Mapeamento das evidências

- Afirmação: A BCT é descrita como componente observável e replicável de uma intervenção.
  - Fonte: `src-bcto-2024`
  - Suporte/força: `canonical_framework`
- Afirmação: A taxonomia padroniza a especificação do conteúdo de intervenções.
  - Fonte: `src-bcttv1-2013`
  - Suporte/força: `canonical_framework`

## Decisão que este conhecimento apoia

Decidir se já existe informação suficiente para escolher um playbook ou se é necessário pedir um único exemplo recente.

## Dados necessários

Um episódio recente; o que a pessoa pretendia fazer; o que ocorreu; horário/local quando relevante; consequência imediata. Frequência só quando a decisão depender de padrão.

## Perguntas úteis para decidir

- Qual foi o episódio mais recente em que a ação planejada não aconteceu?
- O que você fez nos minutos imediatamente antes e depois desse momento?
- Qual detalhe observável distinguiria falta de oportunidade de escolha por outra ação?

## Sinais compatíveis

Rótulos como “preguiçoso”, “sem disciplina” ou “incapaz”, sem ação identificável; relato de intenção sem descrição do momento de execução.

## Explicações alternativas

A ação pode não ter ocorrido por falta de tempo, habilidade, energia, clareza, acesso, segurança ou prioridade. A descrição não escolhe entre essas explicações.

## Processo de aplicação

1. Localizar uma frase que julga a pessoa.
2. Pedir ou extrair um episódio concreto.
3. Registrar comportamento, contexto e resultado sem explicar a causa.
4. Verificar qual dado ausente realmente muda a próxima decisão.
5. Encaminhar ao knowledge ou playbook específico; não permanecer indefinidamente na coleta.

## Quando aplicar

Quando o relato é principalmente um rótulo ou quando duas hipóteses dependem de comportamentos diferentes.

## Quando evitar

Quando o comportamento e o risco já estão claros; em crise, a coleta não deve atrasar o fluxo de segurança.

## Aplicação pelo Alfred

Pode dizer: “Quero separar o julgamento do que aconteceu. Ontem, qual foi o momento em que você pretendia começar e o que fez em seguida?” Depois usa a resposta, sem repetir um interrogatório.

## Aplicação pelo Feedbacker

Deve manter campos separados para evento observado e interpretação. Ausência de registro é dado ausente, não comportamento de falha.

## Exemplo contextualizado

“Você não descreveu falta de disciplina; descreveu três noites em que abriu o material depois das 22h e adormeceu. Isso aponta primeiro para horário e sono, não para caráter.”

## Limitações

Descrições dependem do relato e podem omitir contexto. Ser observável não torna o dado completo nem causal.

## Fontes

`src-bcto-2024`, `src-bcttv1-2013`.
