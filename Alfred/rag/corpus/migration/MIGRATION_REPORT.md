# Relatório final da migração Alfred-only

Data: 2026-07-14  
Estado máximo atribuído: `machine_audited`  
Revisão humana: obrigatória

## Resultado executivo

A base foi reduzida a uma camada canônica em inglês, exclusiva do Alfred e
organizada por tópico. O corpus de produção contém 12 documentos científicos e
sete playbooks situacionais. Não há citações ativas porque nenhuma das 56
citações legadas atende ao gate de verificação.

A migração não aumentou o conteúdo científico: os mesmos 12 conceitos
machine-audited foram editorialmente adaptados, com fontes e mapeamento de
afirmações preservados. A nova estrutura está preparada para gerar registros
FAISS tipados, mas esta tarefa não criou embeddings nem alterou o system prompt
ou o Security Gate do produto.

## Inventário e checkpoint

- Arquivos baseline analisados: 338.
- Diretórios baseline: 66.
- Tamanho baseline: 2.048.579 bytes.
- Checkpoint: `.audit_checkpoints/rag-pre-alfred-migration-20260714T000000-0300.tar.gz`.
- SHA-256: `91523448296784fbb5af7629950f4691d7a63a0438cdb2d4ad20702802650e94`.
- Integridade confirmada para os 338 hashes antes da primeira movimentação.

## Corpus ativo final

- Tópicos: 9.
- Knowledge: 12.
- Playbooks do Alfred: 7.
- Coleções de citações: 0.
- Documentos marcados `index_in_production: true`: 19.
- Fontes no registro: 31.
- Fontes usadas pelo corpus de produção: 20.
- Fontes ativas e verificadas no registro: 27.

Tópicos finais:

`habits`, `goals`, `planning`, `motivation`, `procrastination`,
`self-regulation`, `study-and-learning`, `sleep-and-recovery` e
`physical-activity`.

Não foram criados tópicos vazios para `productivity`,
`consistency-and-relapse`, `overload-and-energy` ou `decision-making`.

## Movimentações

- Linhas em `FILE_MAPPING.jsonl`: 370.
- Movimentos físicos para archive: 333.
- Consolidações/merges de conteúdo: 37.
- Arquivos removidos: 0.
- Arquivos baseline preservados no lugar como metadados/armazenamento de fonte: 5.
- Todos os 333 arquivos arquivados estão em
  `archive/legacy/pre-alfred-20260714/`.
- Todos os destinos registrados existem.

Os caminhos de README, INDEX, registry, schemas e validador foram reutilizados
somente depois de suas versões anteriores terem sido preservadas no archive.

## Conteúdo retirado da produção

- 55 caminhos de Feedbacker, considerando coleções atuais e históricas, foram
  preservados no archive; 19 arquivos atuais foram classificados diretamente
  como Feedbacker antes da movimentação.
- Os 12 documentos de segurança e o antigo safety-handoff saíram do RAG. Regras
  candidatas foram consolidadas em `non_indexed/security_gate_candidates.md`.
- Casos, avaliações, técnicas, geradores, auditorias antigas e quarentenas não
  participam mais da camada ativa.
- As oito coleções com 56 citações `attribution_uncertain` foram arquivadas.
- Fontes originais, registries, relatórios e artefatos de migração não são
  entradas de embeddings.

## Separação de responsabilidades

- Knowledge contém conceito, mecanismos, evidência, mapeamento, alternativas,
  informação necessária, implicações e limitações.
- Playbook contém ativação, exclusões, hipóteses, informação ausente, objetivo,
  caminhos de decisão, condições e próximo passo.
- Citação permanece um tipo opcional e atualmente vazio.
- Dezessete regras epistemológicas/conversacionais foram consolidadas como
  candidatas de system prompt fora do índice.
- Dezoito regras/rotas foram consolidadas como candidatas de Security Gate fora
  do índice.

Nenhum arquivo de knowledge contém scripts do Alfred ou Feedbacker. Playbooks
referenciam conceitos por ID e não repetem explicações científicas extensas.

## Deduplicação

- Blocos canônicos de prosa repetidos com pelo menos 100 caracteres normalizados: 0.
- Tópicos vazios: 0.
- IDs documentais ativos duplicados: 0.
- IDs de conceito duplicados: 0.
- IDs de playbook duplicados: 0.
- Nomes de arquivo canônicos duplicados: 0.

Observable behavior foi incorporado a `self-regulation`; capacidade foi
incorporada a `planning`; tiredness foi associado a `sleep-and-recovery`.
Conceitos próximos foram mantidos separados somente quando produzem decisões
diferentes.

## Registries e relações

- `concept_registry.jsonl`: 12 linhas, uma por conceito.
- `document_registry.jsonl`: 19 linhas, uma por documento de produção.
- Todo playbook possui pelo menos um `related_concept_id` existente.
- Todo knowledge possui pelo menos duas fontes ativas existentes.
- `source_registry.jsonl` ganhou `used_in_production_documents` sincronizado com
  os documentos canônicos.
- Nenhum caminho de archive, migration, non_indexed, sources, Feedbacker ou
  safety está marcado para produção.

## Recuperação e chunking

`RETRIEVAL_CONTRACT.md` exige:

- no máximo um playbook;
- até três chunks de knowledge;
- zero ou uma citação verificada;
- `null`/lista vazia quando confiança ou tipo são insuficientes;
- seleção por tópico e relações, não top-k sem tipo.

`CHUNKING_SPEC.md` define chunks científicos de 250–650 tokens, playbooks
inteiros de 300–900 tokens e sidecar obrigatório de metadados para FAISS.

## Validações executadas

Comando:

```bash
PYTHONDONTWRITEBYTECODE=1 python rag/scripts/validate_rag.py
```

O validador conferiu sintaxe JSON/JSONL/YAML, IDs, caminhos, tópicos, conceitos,
playbooks, fontes, registries, idioma canônico, citações, exclusões de produção,
mapeamento de migração, duplicação literal, diretórios vazios e valor mínimo de
recuperação.

Primeira execução: 10 erros, todos corrigidos.  
Execução após correções: 0 erros e 0 avisos.  
Erros restantes: 0.

O resultado estruturado está em `migration/VALIDATION_REPORT.json`.

## Itens que exigem revisão humana

- Aprovar editorialmente os 19 documentos antes da operação comercial.
- Revisar as adaptações canônicas em inglês contra as fontes e o produto.
- Definir limiares de relevância com um conjunto de avaliação real antes de
  gerar o índice FAISS.
- Revisar clinicamente, legalmente e regionalmente os candidatos do Security
  Gate; eles não são uma implementação pronta.
- Revisar e integrar, se desejado, os candidatos de system prompt.
- Manter as 56 citações fora de produção até verificação em um estado permitido.
- Rever periodicamente atualidade, licença e aplicabilidade das 20 fontes usadas
  em produção.

## Conclusão

Os critérios técnicos da migração foram atendidos. A base está estruturalmente
pronta para a etapa posterior de geração e avaliação de um índice FAISS
balanceado. Ela permanece `machine_audited`, e não deve ser tratada como
`human_reviewed` até a aprovação externa indicada acima.
