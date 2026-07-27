# Baseline da auditoria da base RAG

Snapshot: `2026-07-13T20:42:41-03:00`  
Branch: `master`  
HEAD anterior: `b808d0f rag demo added`

## Checkpoint de segurança

- Arquivo: `.audit_checkpoints/rag-pre-rebuild-20260713.tar.gz`
- SHA-256: `a2a8e29412c5a923b9df291362dccdac7235265a9b9824189529b084be8044e4`
- Tamanho: `184620 bytes`
- Escopo: cópia integral dos 220 arquivos existentes em `rag/` antes da reconstrução.
- Inventário com hash por arquivo: `rag/audit/baseline_file_inventory.jsonl`.

As alterações preexistentes fora de `rag/` não foram incluídas no checkpoint:

- `M demo-agents/main.py`
- ` M main.py`
- `?? .python-version`
- `?? Alfred/`
- `?? README.md`
- `?? feedbacker/`
- `?? langgraph_flow.txt`
- `?? pyproject.toml`
- `?? uv.lock`

## Inventário

- Arquivos: **220**
- Bytes lógicos: **962176**
- Documentos no registro: **182**
- Fontes no registro: **31**

### Por área

| Área | Arquivos |
|---|---:|
| `INDEX.md` | 1 |
| `MISSING_TOPICS.md` | 1 |
| `QUALITY_REPORT.md` | 1 |
| `README.md` | 1 |
| `REVIEW_REQUIRED.md` | 1 |
| `cases` | 75 |
| `document_registry.jsonl` | 1 |
| `evaluation` | 6 |
| `knowledge` | 48 |
| `playbooks` | 47 |
| `quotes` | 8 |
| `safety` | 12 |
| `schemas` | 5 |
| `scripts` | 4 |
| `source_registry.jsonl` | 1 |
| `sources` | 4 |
| `techniques` | 4 |

### Por extensão

| Extensão | Arquivos |
|---|---:|
| `.json` | 5 |
| `.jsonl` | 19 |
| `.md` | 189 |
| `.py` | 2 |
| `.pyc` | 2 |
| `<sem extensão>` | 3 |

### Conteúdo temático e operacional

| Coleção | Quantidade anterior |
|---|---:|
| Knowledge | 48 |
| Playbooks Alfred | 28 |
| Playbooks Feedbacker | 16 |
| Playbooks compartilhados | 3 |
| Casos Alfred | 30 |
| Casos Feedbacker | 20 |
| Casos de segurança | 15 |
| Edge cases | 10 |
| Documentos de segurança | 12 |
| Citações | 56 |
| Técnicas | 40 |
| Cenários de avaliação | 52 |

## Estados encontrados

### Frontmatter Markdown

- `reviewed`: 95
- `human_review_required`: 12
- sem `status`: 82

### `document_registry.jsonl`

- `reviewed`: 170
- `human_review_required`: 12

### `source_registry.jsonl`

- `verified`: 31

Esses estados são apenas o que a geração anterior declarava. Nenhum deles constitui revisão humana ou reverificação científica na reconstrução atual. Todo conteúdo anterior passa a ser tratado como `unverified_generated_draft` até decisão posterior.

## Acesso externo

O acesso à internet foi confirmado em 2026-07-13T20:42:41-03:00: páginas institucionais da OMS e do NICE abriram integralmente. O PubMed direto apresentou desafio anti-bot; nas fases científicas serão usados resultados indexados, PMC, APIs/repositórios NCBI ou páginas do periódico. A pesquisa científica pode prosseguir sem simulação.

## Problemas estruturais iniciais

- 48 ocorrências: Princípio central idêntico em todos os documentos de knowledge.
- 48 ocorrências: Mesmo bloco de sinais, hipóteses e dados ausentes em knowledge.
- 48 ocorrências: Mesmas três perguntas em knowledge, independentemente do conceito.
- 48 ocorrências: Mesmos textos de aplicação por Alfred e Feedbacker em knowledge.
- 28 ocorrências: Mesma estrutura de resposta e perguntas nos playbooks do Alfred.
- 16 ocorrências: Mesmo procedimento de teste de sete dias nos playbooks do Feedbacker.
- 75 ocorrências: Mesma nota de avaliação nos casos.

Outros riscos observados:

- `reviewed` foi aplicado sem revisão humana demonstrável.
- O registro de fontes usa um estado genérico `verified`, incompatível com os estados bibliográficos exigidos agora.
- O validador anterior verifica estrutura e contagens, mas não qualidade científica, unicidade semântica ou autorização de `human_reviewed`.
- `source_ids` aparecem associados ao documento inteiro, sem mapeamento de afirmações.
- Casos e exemplos compartilham boilerplate e testam poucas decisões realmente distintas.
- Existem arquivos `__pycache__` dentro da árvore RAG, inadequados para o corpus e para versionamento.
- O gerador anterior pode reintroduzir status e boilerplate se executado sem ser corrigido.

## Fontes registradas no baseline

- `src-bcttv1-2013` — The Behavior Change Technique Taxonomy (v1) of 93 Hierarchically Clustered Techniques — estado anterior: `verified`
- `src-bcto-2024` — The Behaviour Change Technique Ontology: Transforming the Behaviour Change Technique Taxonomy v1 — estado anterior: `verified`
- `src-ii-2006` — Implementation Intentions and Goal Achievement: A Meta-Analysis of Effects and Processes — estado anterior: `verified`
- `src-intention-behavior-2006` — Does Changing Behavioral Intentions Engender Behavior Change? A Meta-Analysis of the Experimental Evidence — estado anterior: `verified`
- `src-goal-setting-2017` — Unique Effects of Setting Goals on Behavior Change: Systematic Review and Meta-Analysis — estado anterior: `verified`
- `src-self-regulation-2020` — Self-Regulation Mechanisms in Health Behavior Change: A Systematic Meta-Review of Meta-Analyses, 2006–2017 — estado anterior: `verified`
- `src-sdt-rct-2020` — Self-Determination Theory Interventions for Health Behavior Change — estado anterior: `verified`
- `src-sdt-techniques-2019` — A Meta-Analysis of Techniques to Promote Motivation for Health Behaviour Change from a Self-Determination Theory Perspective — estado anterior: `verified`
- `src-habit-lally-2010` — How Are Habits Formed: Modelling Habit Formation in the Real World — estado anterior: `verified`
- `src-habit-review-2024` — Time to Form a Habit: A Systematic Review and Meta-Analysis of Health Behaviour Habit Formation and Its Determinants — estado anterior: `verified`
- `src-context-stability-2022` — Context Stability in Habit Building Increases Automaticity and Goal Attainment — estado anterior: `verified`
- `src-procrastination-steel-2007` — The Nature of Procrastination: A Meta-Analytic and Theoretical Review of Quintessential Self-Regulatory Failure — estado anterior: `verified`
- `src-procrastination-treatment-2018` — Targeting Procrastination Using Psychological Treatments: A Systematic Review and Meta-Analysis — estado anterior: `verified`
- `src-learning-dunlosky-2013` — Improving Students' Learning With Effective Learning Techniques — estado anterior: `verified`
- `src-retrieval-meta-2021` — Testing (Quizzing) Boosts Classroom Learning: A Systematic and Meta-Analytic Review — estado anterior: `verified`
- `src-spacing-review-2024` — Systematic Review of Distributed Practice and Retrieval Practice in Health Professions Education — estado anterior: `verified`
- `src-sleep-aasm-2015` — Recommended Amount of Sleep for a Healthy Adult: A Joint Consensus Statement — estado anterior: `verified`
- `src-sleep-nsf-2015` — National Sleep Foundation's Updated Sleep Duration Recommendations: Final Report — estado anterior: `verified`
- `src-who-pa-2020` — WHO Guidelines on Physical Activity and Sedentary Behaviour — estado anterior: `verified`
- `src-cdc-pa-adults` — Adult Activity: An Overview — estado anterior: `verified`
- `src-self-compassion-2021` — Self-Compassion, Physical Health, and Health Behaviour: A Meta-Analysis — estado anterior: `verified`
- `src-perfectionism-2024` — Relationships Between Perfectionism and Symptoms of Depression, Anxiety and OCD in Adults — estado anterior: `verified`
- `src-who-suicide` — Suicide: Questions and Answers — estado anterior: `verified`
- `src-nice-self-harm-2022` — Self-Harm: Assessment, Management and Preventing Recurrence (NG225) — estado anterior: `verified`
- `src-ms-suicide-br` — Suicídio (Prevenção) — estado anterior: `verified`
- `src-samu-192` — Serviço de Atendimento Móvel de Urgência — SAMU 192 — estado anterior: `verified`
- `src-lgpd` — Lei nº 13.709, de 14 de agosto de 2018 — Lei Geral de Proteção de Dados Pessoais — estado anterior: `verified`
- `src-marcus-gutenberg` — Meditations (public-domain English translation) — estado anterior: `verified`
- `src-epictetus-gutenberg` — A Selection from the Discourses of Epictetus with the Encheiridion — estado anterior: `verified`
- `src-james-gutenberg` — Talks to Teachers on Psychology; and to Students on Some of Life's Ideals — estado anterior: `verified`
- `src-dewey-gutenberg` — How We Think — estado anterior: `verified`

## Decisão da Fase 1

Nenhum arquivo tem qualidade presumida por estar bem formatado. Antes da amostra da Fase 2, os estados serão migrados para `generated` com `requires_human_review: true`; conteúdo não auditado ficará inelegível para indexação de produção.
