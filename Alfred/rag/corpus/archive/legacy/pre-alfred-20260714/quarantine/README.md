# Quarentena

Os arquivos sob esta pasta são versões históricas preservadas para auditoria.
Eles têm `active: false` ou `index_eligible: false` no registro de quarentena e
não podem alimentar indexação, embeddings ou recuperação dos agentes.

Para conteúdo vigente, use somente os caminhos registrados em
`rag/document_registry.jsonl`. Em particular,
`phase5_legacy_knowledge/` contém os 48 documentos anteriores à reconstrução da
Fase 5, inclusive as antigas perguntas genéricas repetidas.
