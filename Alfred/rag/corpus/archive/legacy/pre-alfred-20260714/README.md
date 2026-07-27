# Base RAG do Winperium

Esta pasta separa identidade, política crítica, conhecimento recuperável, aplicação operacional, exemplos, citações e avaliação. É uma biblioteca para Alfred e Feedbacker, não um roteiro obrigatório.

## Arquitetura de execução

`system prompt enxuto + contexto autorizado + histórico recente + RAG científico + RAG operacional + regras determinísticas de segurança + memória de conteúdo recente`.

Filtros recomendados: agente, tipo, domínio, risco, status e idioma. Segurança crítica deve rodar antes e depois da recuperação. O Feedbacker recebe dados estruturados e o Alfred recebe somente o contexto necessário.

## Convenções

IDs são estáveis (`src-`, `kd-`, `pb-`, `case-`, `tech-`, `qt-`, `eval-`). Markdown possui frontmatter. JSONL contém um objeto por linha. `source_ids` aponta para `source_registry.jsonl`; documentos sem fonte científica são explicitamente normas internas.

## Manutenção e governança

1. Verifique a fonte primária ou registro institucional; nunca preencha DOI por memória.
2. Registre licença, acesso, nível de evidência e data de verificação.
3. Escreva paráfrase original, com incerteza e escopo da evidência.
4. Rode `python rag/scripts/validate_rag.py`.
5. Exija revisão humana para segurança, saúde, menores, privacidade e traduções de citações.
6. Atualize índices e relatórios; depreque sem apagar IDs usados em logs.

A distribuição e a função das fontes no corpus reconstruído estão documentadas
em `SOURCE_DIVERSITY_REPORT.md`.

Duplicação deve ser evitada por busca de ID, título normalizado e sobreposição semântica. Uma nova fonte não exige novo documento quando apenas reforça o mesmo princípio; atualize o documento e registre a revisão.

## Preparação para embeddings

Não gere embeddings do corpus atual: na Fase 1, todo conteúdo está inelegível.
Quando houver documentos aprovados pelo fluxo editorial, faça chunking por
seções, mantendo frontmatter, título e `source_ids`; preserve regras
determinísticas fora do índice vetorial.

## Direitos autorais

Não há PDFs armazenados. A base usa paráfrases, metadados e citações curtas de textos em domínio público. Livros comerciais não foram copiados. Antes de uso comercial, revise as licenças e a política de cada fonte.
