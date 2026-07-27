# Changelog da reconstrução de qualidade

## 2026-07-13 — Fase 1 concluída

### Preservação e inventário

- Criado checkpoint integral pré-reconstrução em
  `.audit_checkpoints/rag-pre-rebuild-20260713.tar.gz`.
- Registrado SHA-256 do checkpoint:
  `a2a8e29412c5a923b9df291362dccdac7235265a9b9824189529b084be8044e4`.
- Inventariados 220 arquivos originais com tamanho e SHA-256 em
  `audit/baseline_file_inventory.jsonl`.
- Documentados volume, estados anteriores, fontes e repetição estrutural em
  `AUDIT_BASELINE.md`.
- Confirmado acesso externo funcional a fontes institucionais; não foi criado
  `INTERNET_ACCESS_REQUIRED.md`.

### Governança imediata

- Migrados 182 documentos Markdown para `status: generated`,
  `requires_human_review: true` e `index_eligible: false`.
- Migradas as 182 entradas do registro de documentos para os mesmos estados.
- Rebaixadas 31 fontes para `requires_human_review` e `active: false`, preservando
  o estado legado em `prior_verification_status`.
- Rebaixadas 56 citações para `attribution_uncertain` e `active: false`.
- Marcados 40 registros de técnicas e 120 registros de avaliação como gerados e
  inativos.
- Esvaziado o índice de produção; o inventário histórico permanece auditável.
- Desativado o gerador legado destrutivo que recriava boilerplate e estados não
  autorizados.
- Registradas 611 migrações em `audit/phase1_status_migration.jsonl`.

### Contratos e validação

- Padronizados os estados editoriais, bibliográficos e de citações nos schemas.
- Substituído o parser aproximado de frontmatter por parsing YAML real.
- Adicionadas regras contra promoção automática a `human_reviewed` e contra
  ativação/indexação de conteúdo não auditado.
- Validação concluída sem erros ou avisos; resultado em
  `audit/phase1_validation.json`.

### Fora do escopo desta fase

- Nenhum corpo temático foi reescrito.
- Nenhuma fonte foi cientificamente reverificada.
- Nenhum documento recebeu `research_verified`, `machine_audited` ou
  `human_reviewed`.

## 2026-07-13 — Fase 2 concluída

- Auditados 79 itens: 10 knowledge, 8 playbooks Alfred, 5 playbooks Feedbacker,
  10 casos, 10 técnicas, 15 citações, 10 cenários e os 11 documentos de
  segurança `high`/`critical`.
- Todos os itens ficaram abaixo de pelo menos um limiar obrigatório e continuam
  bloqueados para recuperação.
- Registradas notas nos dez critérios exigidos em
  `audit/sample_audit_scores.jsonl`.
- Documentados achados e padrões de correção em `SAMPLE_AUDIT_REPORT.md`.
- Nenhum corpo temático foi alterado antes do fechamento desta auditoria.
- Integridade estrutural e dos registries revalidada antes da Fase 3.

## 2026-07-13 — Fase 3 concluída

- Reverificadas 27 das 31 fontes em repositórios científicos, páginas de
  periódicos, instituições oficiais e texto legal primário.
- Adicionados, quando disponíveis, PMID, PMCID, volume, número, páginas,
  identificadores institucionais, URL de verificação e data de acesso.
- Corrigidas as URLs atuais do CDC, SAMU 192 e texto compilado da LGPD.
- Registradas limitações de escopo para impedir extrapolação indevida.
- As quatro fontes editoriais do Project Gutenberg permanecem inativas para a
  auditoria específica de citações da Fase 9.
- Mudanças registradas em `audit/phase3_source_verification.jsonl` e resumidas
  em `SOURCE_VERIFICATION_REPORT.md`.
- Validador passou a exigir ano, base de verificação e limitações para fontes
  ativas; integridade dos registries revalidada.

## 2026-07-13 — Fase 4 concluída

- Criados o padrão de conteúdo e a política formal de estados editoriais.
- Centralizadas regras universais de coaching, evidência, incerteza e contratos
  dos agentes em `shared/`, sem torná-las elegíveis para recuperação.
- Definidos gates mínimos de evidência, rastreabilidade, ação, unicidade e
  segurança.
- Adicionado schema específico para técnicas e suas origens.
- Fixada a distinção entre técnica científica e heurística interna.
- Integridade estrutural e dos registries revalidada antes da reconstrução de
  knowledge.

## 2026-07-13 — Fase 5 concluída

- Preservados os 48 arquivos anteriores em `quarantine/phase5_legacy_knowledge/`.
- Reconstruída uma coleção ativa mínima de 12 documentos; 36 IDs anteriores não
  receberam substituto por redundância ou suporte insuficiente.
- Cada documento ativo contém termos reais de recuperação, afirmações mapeadas,
  decisão, dados, hipóteses alternativas, processo e exemplo contextualizado.
- Todos os novos documentos usam fontes verificadas, estão
  `machine_audited`, mantêm revisão humana obrigatória e permanecem fora do
  índice até as fases finais.
- Criado `DOCUMENT_QUALITY_SCORES.jsonl` com o gate da coleção ativa.
- Decisões registradas em `audit/phase5_knowledge_decisions.jsonl` e no registro
  de quarentena.
- Validador passou a exigir `supported_claims`, termos de recuperação, fontes
  ativas por claim e seções operacionais em knowledge auditado.

## 2026-07-13 — Fase 6 concluída

- Preservados 40 registros anteriores em
  `quarantine/phase6_legacy_techniques/`.
- Reconstruídas 12 técnicas distintas; 28 registros anteriores ficaram sem
  substituto por serem heurísticas genéricas, políticas conversacionais ou
  duplicações sem origem suficiente.
- Cada técnica agora declara nome oficial, nome em português, origem,
  mecanismo proposto, evidência, pré-condições, contraindicações, passos,
  exemplo, agentes e fontes.
- Intenções de implementação e técnicas de aprendizagem foram separadas da
  BCTTv1 em vez de receberem filiação incorreta.
- Decisões registradas em `audit/phase6_technique_decisions.jsonl` e notas
  incorporadas a `DOCUMENT_QUALITY_SCORES.jsonl`.
- Schema e validador passaram a exigir o contrato completo e fontes ativas para
  técnicas auditadas.

## 2026-07-13 — Fase 7 concluída

- Preservados os 47 playbooks anteriores em
  `quarantine/phase7_legacy_playbooks/`.
- Reconstruídos 10 playbooks do Alfred, 9 do Feedbacker e 2 compartilhados.
- Alfred agora distingue clareza, capacidade, energia, autoria da meta,
  perfeccionismo, escuta, recusa, evidência, agenda variável e handoff de
  segurança.
- Feedbacker agora separa observação, padrão, hipótese, evidência favorável e
  contrária, dados ausentes, confiança qualitativa, teste e revisão.
- Criado `playbooks/feedbacker/CONFIDENCE_AND_EVIDENCE_GUIDE.md` com política
  `low`/`moderate`/`high` sem porcentagens arbitrárias.
- Relações de knowledge e técnicas foram limitadas a IDs ativos existentes.
- Decisões e notas registradas nos logs de auditoria, quarentena e qualidade.
- Validador passou a conferir referências e seções decisórias por agente.

## 2026-07-13 — Fase 8 concluída

- Preservados os 75 casos anteriores em `quarantine/phase8_legacy_cases/`.
- Reconstruídos 30 casos: 11 Alfred, 9 Feedbacker, 5 ambiguidades/edge cases e
  5 handoffs de segurança.
- Cada caso declara fatos observados, hipóteses concorrentes, dados ausentes,
  knowledge/playbooks corretos, recuperações proibidas, risco, comportamento
  ideal, variações aceitáveis e padrões proibidos.
- As 30 `decision_key` são únicas; cada caso testa uma decisão diferente.
- Incluídos conflitos entre motivação e sono, disciplina e clareza, desempenho e
  sobrecarga, ausência e falha, narrativa e registros, além de recusa, escuta,
  evidência e citação falsa.
- Decisões registradas em `audit/phase8_case_decisions.jsonl`, quarentena e
  `DOCUMENT_QUALITY_SCORES.jsonl`.
- Schema e validador passaram a conferir campos, risco e integridade de todas as
  relações dos casos.
- Gate de fechamento: 75/75 unidades auditadas possuem scores completos, 210
  registros estão inativos na quarentena e não restaram parágrafos literais
  repetidos no conteúdo reconstruído.
- Relatórios intermediários, índice e estado de revisão foram sincronizados com
  a conclusão da Fase 8.

## 2026-07-14 — Correção pós-Fase 8: perguntas e diversidade de fontes

- Adicionadas três perguntas de decisão específicas a cada um dos 12 documentos
  ativos de *knowledge*; o contrato central orienta o agente a escolher somente
  a pergunta que possa mudar a decisão, em vez de aplicar um questionário.
- O schema e o validador agora exigem exatamente três perguntas válidas por
  documento e rejeitam repetição literal dentro da coleção ativa.
- O gate de *knowledge* passou a exigir ao menos duas fontes distintas por
  documento auditado.
- Criado `SOURCE_DIVERSITY_REPORT.md`, separando diversidade bibliográfica da
  função da fonte e registrando a concentração da BCTTv1 nas técnicas.
- Os 48 arquivos com a antiga seção genérica de perguntas permanecem somente em
  `quarantine/phase5_legacy_knowledge/`, fora de indexação e embeddings.
