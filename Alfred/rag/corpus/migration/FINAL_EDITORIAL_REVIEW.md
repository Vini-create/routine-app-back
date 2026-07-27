# Final editorial review

## Arquivos revisados e modificados

Revisados:

- `rag/INDEX.md`, `rag/RETRIEVAL_CONTRACT.md`, `rag/CHUNKING_SPEC.md` e `rag/COVERAGE_MATRIX.md`;
- `rag/document_registry.jsonl`, `rag/concept_registry.jsonl` e `rag/source_registry.jsonl`;
- 9 arquivos `rag/canonical/*/topic.yaml`;
- 28 documentos ativos de knowledge e 17 playbooks ativos;
- 36 registros de fontes efetivamente usados pelos documentos de knowledge.

Modificados:

- `rag/source_registry.jsonl`;
- `rag/concept_registry.jsonl`;
- `rag/canonical/habits/topic.yaml`;
- `rag/canonical/planning/topic.yaml`;
- `rag/canonical/goals/knowledge/goal-specificity.md`;
- `rag/canonical/habits/knowledge/environmental-cues-and-friction.md`;
- `rag/canonical/habits/knowledge/habit-formation.md`;
- `rag/canonical/motivation/knowledge/goal-autonomy.md`;
- `rag/canonical/motivation/knowledge/motivation-variability.md`;
- `rag/canonical/goals/playbooks/user-set-unrealistic-goal.md`;
- `rag/canonical/planning/playbooks/user-reports-insufficient-capacity.md`;
- `rag/canonical/procrastination/playbooks/standards-block-completion.md`;
- `rag/canonical/procrastination/playbooks/user-cannot-start.md`;
- `rag/canonical/procrastination/playbooks/user-stops-after-starting.md`;
- `rag/canonical/sleep-and-recovery/playbooks/user-reports-tiredness.md`;
- `rag/migration/DEDUPLICATION_REPORT.md`;
- `rag/migration/FINAL_EDITORIAL_REVIEW.md`.

## Principais correções

- Removida de goal specificity uma generalização sobre revisões aplicadas que não estava sustentada pelos `source_ids` do documento.
- Separada linguagem causal de associação prospectiva em motivation variability.
- Corrigida a síntese de goal autonomy: um artigo sustenta pequenos efeitos comportamentais médios de intervenções SDT, enquanto o outro avalia suporte à autonomia, satisfação de necessidades e motivação, não efeitos comportamentais isolados de cada técnica.
- Corrigida a descrição do desenho de context stability para refletir um estudo longitudinal com manipulação e um estudo longitudinal observacional.
- Tornadas explícitas, no playbook de dificuldade para iniciar, as rotas distintas para ambiguidade, pré-requisito, capacidade, recompensa imediata, ameaça avaliativa e fricção ambiental.
- Acrescentadas relações operacionais ausentes para evaluative avoidance, environmental cues, temporal discounting, time estimation, sleep regularity e goal difficulty; removida a relação ampla entre sleep regularity e irregular schedule que poderia contaminar recuperação entre tópicos.
- Acrescentados termos específicos para excesso de hábitos, compensação e sobrecarga por compromissos, sem adicionar termos genéricos de alta dominância.
- Verificadas online as 36 fontes usadas. Sete registros receberam correções objetivas: título completo da BCTTv1; título e autores da meta-análise SDT com DOI `10.1037/ccp0000501`; nomes dos autores da revisão SDT de 2019; classificação do desenho de context stability; autores da meta-análise de retrieval practice; URL e ISBN da diretriz completa da WHO; e título atual da página do CDC. Nenhum dado ausente foi inventado.
- Atualizado o relatório de duplicação para o corpus final de 45 documentos.

## Quantidade final

- Knowledge: 28.
- Playbooks: 17.
- Documentos ativos: 45.
- Tópicos: 9.
- Fontes usadas: 36.
- Citações: 0.

## Resultado das validações

- `rag/scripts/validate_rag.py`: `status: ok`, 0 erros e 0 warnings.
- Contagens validadas: 9 tópicos, 28 knowledge, 17 playbooks, 45 documentos de produção e 36 fontes de produção.
- Duplicação: 45 documentos, 990 pares comparados, 0 pares com similaridade normalizada maior ou igual a 0,45 e 0 blocos repetidos de pelo menos 100 caracteres normalizados.
- Identidade editorial: todos os 45 documentos permanecem `machine_audited`, `requires_human_review: true` e `index_in_production: true`.
- Escopo: nenhum arquivo legado foi restaurado; embeddings e FAISS não foram gerados; nenhuma citação foi criada.

## Cobertura dos 26 cenários

| # | Situação | Tópico esperado | Playbook esperado | Concept IDs esperados | Cobertura |
|---:|---|---|---|---|---|
| 1 | user cannot start | procrastination | `user-cannot-start` | `procrastination-pattern`, `observable-behavior`, `action-planning` | good |
| 2 | user starts and abandons | procrastination | `user-stops-after-starting` | `observable-behavior`, `task-aversiveness`, `graded-task-progression` | good |
| 3 | user missed multiple days | habits | `user-missed-several-days` | `lapse-recovery`, `habit-formation`, `self-monitoring` | good |
| 4 | user is overwhelmed | planning | `user-reports-insufficient-capacity` | `goal-review`, `action-planning`, `time-estimation` | acceptable |
| 5 | user created too many habits | habits | `user-created-too-many-habits` | `goal-conflict`, `graded-task-progression`, `goal-review` | good |
| 6 | user lacks time | planning | `user-reports-insufficient-capacity` | `goal-review`, `action-planning`, `time-estimation` | good |
| 7 | user has low energy | sleep-and-recovery | `user-reports-tiredness` after the Security Gate | `sleep-duration`, `sleep-regularity`, `observable-behavior` | good |
| 8 | user is waiting for motivation | motivation | `user-waits-for-motivation` | `motivation-variability`, `goal-autonomy`, `action-planning` | good |
| 9 | user is perfectionistic | procrastination | `standards-block-completion` | `evaluative-avoidance`, `procrastination-pattern`, `goal-difficulty` | good |
| 10 | user fears failure | procrastination | `standards-block-completion` or `user-cannot-start`, according to the blocked stage | `evaluative-avoidance`, `task-aversiveness`, `goal-difficulty` | acceptable |
| 11 | user has a vague goal | goals | `user-has-vague-goal` | `goal-specificity`, `behavior-vs-outcome-goals`, `action-planning` | good |
| 12 | user has an unrealistic goal | goals | `user-set-unrealistic-goal` | `goal-difficulty`, `goal-review`, `time-estimation` | good |
| 13 | user has conflicting goals | goals | `user-has-conflicting-goals` | `goal-conflict`, `goal-autonomy`, `goal-review` | good |
| 14 | user cannot prioritize | goals or planning, according to whether goals or capacity conflict | `user-has-conflicting-goals` or `user-reports-insufficient-capacity` | `goal-conflict`, `goal-review`, `time-estimation` | acceptable |
| 15 | user wants to compensate for missed work | habits | `user-wants-to-compensate` | `lapse-recovery`, `graded-task-progression`, `goal-review` | good |
| 16 | user repeatedly postpones | procrastination | `user-cannot-start` or `user-stops-after-starting`, according to the latest episode | `procrastination-pattern`, `task-aversiveness`, `temporal-discounting` | acceptable |
| 17 | user rejects suggestions | motivation | `user-rejects-suggestion` | `goal-autonomy`, `observable-behavior` | good |
| 18 | user only wants to be heard | no topical RAG expected | none | none | good |
| 19 | user is making sustainable progress | self-regulation | `user-is-progressing-sustainably` | `behavioral-feedback`, `self-monitoring`, `graded-task-progression` | good |
| 20 | user wants to increase difficulty too quickly | habits | `user-increases-difficulty-too-quickly` | `graded-task-progression`, `behavioral-feedback`, `physical-activity-consistency` | good |
| 21 | user's environment creates friction | habits | none; direct knowledge retrieval is expected | `environmental-cues-and-friction`, `habit-formation`, `action-planning` | acceptable |
| 22 | user's schedule conflicts with the habit | planning | `user-has-irregular-schedule` | `action-planning`, `implementation-intentions`, `habit-formation` | good |
| 23 | user lacks the required skill or clarity | procrastination | `user-cannot-start` | `action-planning`, `observable-behavior`, `procrastination-pattern` | good |
| 24 | user has inconsistent weekdays and weekends | planning | `user-has-irregular-schedule` | `action-planning`, `implementation-intentions`, `habit-formation` | good |
| 25 | user wants scientific evidence | topic and concepts depend on the scientific referent | none | query-dependent | acceptable |
| 26 | user asks how long habit formation takes | habits | none; direct knowledge retrieval is expected | `habit-formation` | good |

Totais: 20 good, 6 acceptable e 0 weak.

## Pendências que exigem revisão humana

- Revisão científica de texto completo das fontes cujo acesso automático ficou limitado a metadados ou resumo, com atenção especial às inferências de componentes isolados em intervenções multicomponentes.
- Aprovação clínica e de segurança dos limites dos documentos `medium`, especialmente tiredness, sleep, physical activity e graded progression, em conjunto com o Security Gate externo ao RAG.
- Avaliação humana de recuperação para os seis cenários `acceptable`, incluindo prompts adversariais que separam sobrecarga de sofrimento, medo de falhar de requisito real, prioridade de conflito de capacidade, adiamento de incapacidade de continuar, fricção ambiental de falta de recurso e pedido genérico de evidência.
- Aprovação editorial final do inglês e da voz comercial do Alfred antes de qualquer indexação; nenhum documento deve ser promovido a `human_reviewed` sem essa etapa.
