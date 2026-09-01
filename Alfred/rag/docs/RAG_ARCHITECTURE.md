# Arquitetura RAG do Alfred — implementação unificada

> **Implementação canônica:** `app/ai/retrieval/` e
> `app/ai/graph/nodes/retrieval.py`. Os módulos Python antigos em
> `Alfred/rag/` documentam o protótipo FAISS/OpenAI anterior; o corpus
> editorial em `Alfred/rag/corpus/` continua sendo a fonte de conhecimento.

## Visão geral

O Alfred utiliza uma camada de Retrieval-Augmented Generation (RAG) para
recuperar conhecimento curado antes de produzir determinadas respostas. O
objetivo é complementar o modelo conversacional com conteúdo rastreável e
adequado ao contexto, sem transformar toda interação em uma consulta à base
vetorial.

A arquitetura separa quatro responsabilidades:

1. preparação e governança do corpus;
2. carregamento do índice FAISS auditado e embedding da consulta;
3. classificação e recuperação de contexto;
4. orquestração conversacional no grafo LangGraph da aplicação.

O RAG é um componente do fluxo do Alfred, não o agente completo. Mensagens que
não precisam de conhecimento especializado podem seguir sem recuperação, e
consultas com baixa confiança podem retornar contexto vazio.

> Esta documentação pública descreve a arquitetura em alto nível. Prompts,
> credenciais, critérios detalhados de segurança, limiares operacionais e
> regras internas de decisão não são incluídos.

## Organização do corpus

O corpus é composto por documentos canônicos, versionados e registrados antes
de qualquer indexação. Somente documentos explicitamente aprovados para uso em
produção podem gerar vetores.

Existem duas unidades principais de recuperação:

- **Knowledge:** conteúdo conceitual ou científico organizado por tópico e
  conceito, mantendo referências e limitações relevantes.
- **Playbook:** orientação situacional usada para apoiar a escolha de uma linha
  de resposta diante de um cenário reconhecido.

Arquivos de tópicos organizam vocabulário de roteamento e relações entre
conceitos. Eles ajudam a encontrar a região correta do corpus, mas não são
tratados como evidência científica.

## Pipeline de preparação e indexação

O pipeline editorial transforma os documentos canônicos em um artefato JSONL
reproduzível e em índices FAISS versionados. No runtime, os vetores dos
documentos são apenas carregados e validados:

```text
documentos canônicos
→ registro e validação estrutural
→ carregamento de conteúdo e metadados
→ chunking determinístico
→ validação pelo tokenizer do modelo de embeddings
→ artefato JSONL de chunks
→ validação de hash e cardinalidade
→ embeddings de documentos com text-embedding-3-small
→ índices FAISS e sidecars de metadados versionados
→ matriz densa validada e índice BM25 em memória
```

### Carregamento

O loader consulta o registro de documentos e carrega somente o conteúdo
permitido. Durante essa etapa, IDs, caminhos e metadados do arquivo são
comparados para impedir que um documento incorreto entre silenciosamente no
índice.

### Chunking

Cada chunk contém o texto que será vetorizado e os metadados necessários para
rastrear sua origem. Os IDs são determinísticos: reconstruir um corpus
inalterado produz as mesmas identidades.

O chunking respeita fronteiras semânticas do Markdown e limites medidos pelo
tokenizer do modelo de embeddings. Quando um documento canônico já representa
uma unidade coerente e cabe no intervalo definido, ele pode permanecer inteiro.

### Artefato intermediário

Antes de chamar o provedor de embeddings, os chunks são serializados em JSONL.
Essa separação permite inspecionar exatamente o conteúdo indexável e evita
acoplar a preparação editorial à infraestrutura vetorial.

### Embeddings e índices

Os textos são convertidos em vetores de dimensão consistente. Antes da escrita,
o pipeline valida quantidade, dimensão e integridade numérica dos embeddings.

Os vetores dos 45 documentos foram gerados com
`text-embedding-3-small`, normalizados e persistidos em dois namespaces FAISS:
knowledge e playbooks. O runtime valida hash do corpus, modelo, dimensão,
cardinalidade e IDs antes de aceitar a matriz.

Somente a consulta curta do usuário é vetorizada em runtime, com a mesma
`OPENAI_API_KEY` já usada pelos modelos do Alfred. Isso elimina Torch,
Transformers e o modelo local residente em memória. A chamada de embedding é
limitada às rotas RAG e permanece separada das chamadas de LLM.

O JSONL e o manifesto continuam versionados. Antes da indexação, o loader
confere SHA-256, cardinalidade, IDs únicos, idioma, status editorial e tipos
permitidos. Arquivos de archive/quarantine não são descobertos por glob.

## Fluxo de recuperação em runtime

O retriever recebe uma consulta já preparada pelas etapas anteriores do fluxo
conversacional:

```text
mensagem original no idioma do usuário
→ verificações anteriores ao RAG
→ pistas determinísticas de tópico
→ embedding da consulta compatível com o índice FAISS
→ busca densa + BM25 lexical
→ reciprocal-rank fusion
→ reranqueamento determinístico
→ filtro contra injeção indireta
→ confiança, cobertura e evidence pack
→ Alfred conversacional ou analítico
```

### Roteamento lexical

O primeiro sinal de roteamento compara a consulta com o vocabulário editorial
dos tópicos. Quando há uma correspondência clara, o tópico encontrado funciona
como um atalho determinístico.

Essa etapa não é a única responsável pela classificação. Usuários podem
descrever o mesmo problema com palavras completamente diferentes das presentes
no corpus.

### Fallback semântico

Quando o atalho lexical não encontra um tópico, o mesmo embedding que será
usado na recuperação consulta globalmente o namespace de knowledge. Os melhores
resultados são agrupados por tópico, produzindo uma decisão semântica.

A classificação pode resultar em:

- correspondência lexical;
- correspondência semântica;
- ambiguidade entre tópicos;
- baixa similaridade com o corpus;
- ausência de candidatos válidos.

Em vez de forçar sempre o primeiro resultado, o retriever pode retornar uma
decisão vazia. Em caso de ambiguidade, os principais tópicos candidatos são
preservados para que o grafo possa solicitar um esclarecimento ao usuário.

### Recuperação tipada

Depois de definir o tópico provável, a recuperação segue uma ordem explícita:

```text
tópico selecionado
→ candidatos de playbook no mesmo tópico
→ playbook mais relevante, quando disponível
→ candidatos de knowledge no mesmo tópico
→ priorização de conceitos relacionados ao playbook
→ conjunto limitado e deduplicado de contexto
```

A matriz densa realiza a busca por similaridade vetorial e o BM25 produz o
sinal lexical. Reciprocal Rank Fusion combina posições sem fingir que scores de
escalas diferentes são probabilidades. O evidence pack limita a saída a três
documentos científicos e um playbook.

Slots de recuperação representam limites máximos, não metas obrigatórias. O
resultado pode conter somente knowledge, menos chunks que o limite ou nenhum
contexto recuperado.

## Similaridade e metadados

Os vetores são normalizados para que o produto interno corresponda à
similaridade de cosseno. As posições da matriz são resolvidas contra os objetos
validados do JSONL para recuperar texto, fontes, tópico, conceito e demais
metadados.

Os scores são sinais de ranking, não probabilidades. A decisão final combina
similaridade, roteamento e regras de seleção, evitando apresentar um número de
proximidade como certeza sobre a intenção do usuário.

## Contrato de integração com o grafo

O retriever foi desenhado para funcionar como um componente isolado dentro do
grafo conversacional.

### Entrada esperada

- consulta não vazia;
- texto normalizado no idioma canônico de recuperação;
- verificações de segurança e necessidade de RAG executadas anteriormente.

### Saída fornecida

- tópico selecionado ou ausência de decisão;
- origem da decisão de tópico;
- motivo de baixa confiança, quando aplicável;
- tópicos candidatos em casos ambíguos;
- playbook opcional;
- chunks de knowledge;
- avisos de recuperação.

Essa interface permite que o grafo escolha entre responder com contexto,
seguir sem RAG, solicitar esclarecimento ou encaminhar a mensagem para outro
fluxo da aplicação.

## Confiabilidade e evolução

A implementação prioriza comportamento reproduzível e falhas explícitas:

- documentos e fontes possuem identidades rastreáveis;
- chunks mantêm IDs estáveis;
- índices e metadados precisam ter a mesma cardinalidade;
- consultas devem usar o mesmo modelo e dimensão do índice;
- builds registram sua origem por manifesto e hash;
- baixa confiança não é convertida automaticamente em contexto;
- testes automatizados cobrem chunking, roteamento e recuperação.

Os limiares de recuperação e as regras de confiança devem evoluir a partir de
cenários de avaliação representativos. A interface do retriever permanece
estável para que estratégias de ranking ou armazenamento possam ser alteradas
sem reescrever o grafo conversacional.

## Ferramentas utilizadas

- Python
- OpenAI `text-embedding-3-small` para consultas
- FAISS com vetores de documentos pré-computados
- NumPy
- LangChain OpenAI
- tiktoken
- PyYAML
- pytest
- Markdown, YAML e JSONL

## Técnicas utilizadas

- Retrieval-Augmented Generation
- corpus canônico com governança por registro
- chunking semântico e determinístico
- validação por tokenizer
- embeddings em lote
- busca vetorial com índice pré-computado
- BM25 e Reciprocal Rank Fusion
- similaridade de cosseno
- roteamento híbrido lexical e semântico
- fallback por confiança e margem entre candidatos
- filtragem por metadados
- deduplicação e limites por tipo de contexto
- sidecar de conteúdo e metadados
- versionamento de builds com manifesto e hash
- recuperação fail-safe com resultado vazio
- testes automatizados de componentes
