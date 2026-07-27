# Auditoria amostral — Fase 2

Data: 2026-07-13  
Método: inspeção de conteúdo e metadados por modelo; não equivale a revisão humana.

## Escopo

Foram avaliados **79 itens**: 8 alfred_playbook, 10 case, 10 evaluation, 5 feedbacker_playbook, 10 knowledge, 15 quote, 11 safety, 10 technique.
Todos os documentos de segurança com risco `high` ou `critical` foram incluídos.

## Resultado

- Itens abaixo de pelo menos um limiar obrigatório: **79 de 79**.
- Nenhum item da amostra pode ser ativado sem correção.
- A falha dominante é a combinação de fonte associada ao tema, mas não à afirmação, com conteúdo operacional intercambiável.
- O problema é sistêmico; portanto, quantidade anterior não será usada como meta de preservação.

### Médias por critério

| Critério | Média / 5 |
|---|---:|
| specificity | 2.20 |
| scientific_support | 1.20 |
| source_traceability | 1.01 |
| operational_value | 1.85 |
| naturalness | 1.99 |
| retrieval_uniqueness | 2.22 |
| agent_relevance | 3.32 |
| safety | 2.78 |
| metadata_quality | 2.62 |
| copyright_safety | 4.62 |

## Notas por item

| ID | Coleção | Média | Especificidade | Evidência | Rastreabilidade | Operacional | Unicidade | Decisão | Achado principal |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| `kd-goal-review` | knowledge | 2.40 | 2 | 2 | 1 | 2 | 1 | bloqueado | Fontes plausíveis, mas sem mapeamento de afirmações; processo e exemplo são boilerplate. |
| `kd-behavior-observable` | knowledge | 2.60 | 2 | 2 | 1 | 2 | 1 | bloqueado | Conceito útil, porém definição, perguntas e aplicação se repetem em todo knowledge. |
| `kd-goal-decomposition` | knowledge | 2.40 | 2 | 2 | 1 | 2 | 1 | bloqueado | Não oferece algoritmo específico para decompor nem critérios de parada. |
| `kd-habit-formation` | knowledge | 2.80 | 2 | 3 | 2 | 2 | 2 | bloqueado | Tema e fontes são relevantes, mas a síntese não separa automaticidade de repetição. |
| `kd-procrastination-map` | knowledge | 2.50 | 2 | 2 | 1 | 2 | 2 | bloqueado | Não operacionaliza análise funcional nem diferencia adiamento de restrição real. |
| `kd-spaced-practice` | knowledge | 2.60 | 2 | 2 | 1 | 2 | 2 | bloqueado | Falta dose, horizonte, material e contraste com simples repetição. |
| `kd-sleep-duration` | knowledge | 2.30 | 2 | 2 | 1 | 1 | 2 | bloqueado | Recomendação de saúde sem rastreio por faixa etária e sem limites clínicos específicos. |
| `kd-physical-activity-consistency` | knowledge | 2.40 | 2 | 2 | 1 | 2 | 2 | bloqueado | Mistura organização e progressão física sem critérios de segurança suficientes. |
| `kd-self-compassion-accountability` | knowledge | 2.50 | 2 | 2 | 1 | 2 | 2 | bloqueado | Associação entre autocompaixão e ação é ampla demais para a fonte declarada. |
| `kd-energy-overload` | knowledge | 2.10 | 1 | 1 | 1 | 1 | 1 | bloqueado | Construto vago; não distingue sono, carga, doença, humor e conflito de agenda. |
| `pb-a-cannot-start` | alfred_playbook | 2.50 | 2 | 1 | 1 | 2 | 1 | bloqueado | Resposta padrão não diferencia clareza, habilidade, medo, energia ou ambiente. |
| `pb-a-tired` | alfred_playbook | 2.40 | 2 | 1 | 1 | 2 | 2 | bloqueado | Não faz triagem suficiente entre cansaço comum e sinal médico/privação grave. |
| `pb-a-no-time` | alfred_playbook | 2.50 | 2 | 1 | 1 | 2 | 1 | bloqueado | Reduzir tarefa é resposta padrão; faltam conflito de prioridade e capacidade real. |
| `pb-a-demotivated` | alfred_playbook | 2.40 | 2 | 1 | 1 | 2 | 1 | bloqueado | Não separa ambivalência, meta imposta, anedonia, energia e ausência de sentido. |
| `pb-a-perfectionist` | alfred_playbook | 2.50 | 2 | 1 | 1 | 2 | 2 | bloqueado | Falta árvore entre padrão alto funcional, medo de avaliação e bloqueio de entrega. |
| `pb-a-medical` | alfred_playbook | 2.40 | 2 | 1 | 1 | 2 | 2 | bloqueado | Limite existe, mas encaminhamento e sinais de urgência dependem de texto genérico. |
| `pb-a-distress` | alfred_playbook | 2.40 | 2 | 1 | 1 | 2 | 2 | bloqueado | Não diferencia escuta, crise aguda e risco imediato com critérios operacionais. |
| `pb-a-emergency` | alfred_playbook | 2.30 | 2 | 1 | 1 | 2 | 2 | bloqueado | Playbook crítico não pode depender do RAG e contém risco de ativação lexical frágil. |
| `pb-f-no-data` | feedbacker_playbook | 2.90 | 3 | 1 | 1 | 3 | 3 | bloqueado | Decisão é distinta, mas ainda usa procedimento e linguagem idênticos aos demais. |
| `pb-f-low-completion` | feedbacker_playbook | 2.50 | 2 | 1 | 1 | 2 | 1 | bloqueado | Não define denominador, janela, dado ausente nem alternativas ao desempenho baixo. |
| `pb-f-good-overload` | feedbacker_playbook | 2.80 | 3 | 1 | 1 | 3 | 3 | bloqueado | Conflito útil, mas não define evidência favorável/contrária nem limiar clínico. |
| `pb-f-incompatible-times` | feedbacker_playbook | 2.90 | 3 | 1 | 1 | 3 | 3 | bloqueado | Padrão observável, porém faltam regras para compromissos flexíveis e dados incompletos. |
| `pb-f-missing-not-failure` | feedbacker_playbook | 2.90 | 3 | 1 | 1 | 3 | 3 | bloqueado | Distinção importante, mas o procedimento continua intercambiável com outros playbooks. |
| `case-a-001` | case | 2.60 | 3 | 1 | 1 | 2 | 2 | bloqueado | Contexto concreto, mas a resposta ignora a organização de arquivos observada. |
| `case-a-005` | case | 2.30 | 2 | 1 | 1 | 2 | 1 | bloqueado | Variação superficial com nota de avaliação idêntica. |
| `case-a-009` | case | 2.20 | 2 | 1 | 1 | 2 | 2 | bloqueado | Cansaço não contém triagem nem hipóteses alternativas suficientes. |
| `case-a-016` | case | 2.50 | 2 | 1 | 1 | 2 | 2 | bloqueado | Rejeição do usuário não testa consentimento, recusa ou mudança de objetivo. |
| `case-a-020` | case | 2.50 | 2 | 1 | 1 | 2 | 2 | bloqueado | Pedido científico não testa fonte específica, limite ou modo de referência. |
| `case-a-025` | case | 2.20 | 2 | 1 | 1 | 2 | 2 | bloqueado | Caso médico não declara sinais de urgência nem resposta segura verificável. |
| `case-f-001` | case | 2.40 | 2 | 1 | 1 | 2 | 1 | bloqueado | Não fornece registros reais para calcular ou contestar baixa conclusão. |
| `case-f-011` | case | 2.50 | 3 | 1 | 1 | 2 | 3 | bloqueado | Boa ambiguidade, mas sem série temporal ou evidência contrária. |
| `case-e-005` | case | 2.40 | 3 | 1 | 1 | 2 | 3 | bloqueado | Conflito sobrecarga/privação existe, mas o resultado ideal é genérico. |
| `case-s-006` | case | 2.40 | 3 | 1 | 1 | 2 | 3 | bloqueado | Risco imediato exige critérios e fluxo determinístico, ausentes no caso. |
| `tech-action-planning` | technique | 2.60 | 2 | 2 | 1 | 2 | 2 | bloqueado | Nome plausível, mas passos genéricos não refletem a definição formal da técnica. |
| `tech-implementation-intention` | technique | 2.60 | 2 | 2 | 1 | 2 | 2 | bloqueado | Não documenta relação se–então, contingência, mecanismo nem condições de uso. |
| `tech-graded-tasks` | technique | 2.60 | 2 | 2 | 1 | 2 | 2 | bloqueado | Não define gradação, critério de avanço ou origem formal. |
| `tech-goal-review` | technique | 2.60 | 2 | 2 | 1 | 2 | 2 | bloqueado | Não distingue revisão do resultado, comportamento, plano ou meta. |
| `tech-self-monitoring` | technique | 2.50 | 2 | 2 | 1 | 2 | 2 | bloqueado | Não define variável, frequência, carga de registro nem risco de compulsão. |
| `tech-retrieval-practice` | technique | 2.70 | 2 | 2 | 1 | 2 | 3 | bloqueado | Técnica educacional aparece no mesmo molde das técnicas comportamentais. |
| `tech-minimum-viable-habit` | technique | 2.50 | 2 | 1 | 1 | 2 | 2 | bloqueado | Heurística interna parece técnica científica; origem não é declarada. |
| `tech-capacity-budget` | technique | 2.50 | 2 | 1 | 1 | 2 | 2 | bloqueado | Heurística interna sem definição de capacidade ou base de decisão. |
| `tech-ask-before-advice` | technique | 2.60 | 2 | 1 | 1 | 2 | 2 | bloqueado | Política conversacional é rotulada como técnica sem declarar origem interna. |
| `tech-confidence-calibration` | technique | 2.50 | 2 | 1 | 1 | 2 | 2 | bloqueado | Não define política low/moderate/high nem evidência necessária. |
| `qt-001` | quote | 1.90 | 2 | 1 | 1 | 1 | 2 | bloqueado | Localização é vaga e tradução própria não foi revisada. |
| `qt-002` | quote | 1.90 | 2 | 1 | 1 | 1 | 2 | bloqueado | Texto e edição não foram reverificados; uso temático é amplo. |
| `qt-008` | quote | 1.90 | 2 | 1 | 1 | 1 | 2 | bloqueado | Frase pode ser verificável, mas capítulo/página e contexto faltam. |
| `qt-009` | quote | 1.90 | 2 | 1 | 1 | 1 | 2 | bloqueado | Tradução depende de edição inglesa intermediária. |
| `qt-015` | quote | 1.90 | 2 | 1 | 1 | 1 | 2 | bloqueado | Atribuição precisa ser conferida na edição oficial indicada. |
| `qt-017` | quote | 1.90 | 2 | 1 | 1 | 1 | 2 | bloqueado | Ano registrado parece ser da tradução, não da obra original. |
| `qt-022` | quote | 1.90 | 2 | 1 | 1 | 1 | 2 | bloqueado | Localização genérica impede rastreabilidade. |
| `qt-024` | quote | 1.90 | 2 | 1 | 1 | 1 | 2 | bloqueado | Contexto filosófico pode não sustentar uso comportamental. |
| `qt-029` | quote | 1.90 | 2 | 1 | 1 | 1 | 2 | bloqueado | Texto curto, mas tradução e posição na obra não foram auditadas. |
| `qt-033` | quote | 1.90 | 2 | 1 | 1 | 1 | 2 | bloqueado | Trecho depende de tradução histórica; contexto ausente. |
| `qt-036` | quote | 1.90 | 2 | 1 | 1 | 1 | 2 | bloqueado | Pertinência a motivação foi atribuída editorialmente sem contexto. |
| `qt-043` | quote | 1.90 | 2 | 1 | 1 | 1 | 2 | bloqueado | Uso em resiliência pode distorcer o contexto original. |
| `qt-045` | quote | 1.90 | 2 | 1 | 1 | 1 | 2 | bloqueado | Autor é introdução anônima, não Marco Aurélio; alto risco editorial. |
| `qt-050` | quote | 1.90 | 2 | 1 | 1 | 1 | 2 | bloqueado | Tradução própria e edição intermediária exigem revisão. |
| `qt-055` | quote | 1.90 | 2 | 1 | 1 | 1 | 2 | bloqueado | Texto é rastreável em princípio, mas localização continua vaga. |
| `eval-a-001` | evaluation | 2.40 | 2 | 1 | 1 | 2 | 2 | bloqueado | Critérios são genéricos e não definem recuperações proibidas. |
| `eval-a-005` | evaluation | 2.50 | 3 | 1 | 1 | 2 | 3 | bloqueado | Tema de privação é relevante, mas o pass/fail de segurança é vago. |
| `eval-a-006` | evaluation | 2.40 | 3 | 1 | 1 | 2 | 3 | bloqueado | Não testa sinais de urgência nem proibição de prescrição. |
| `eval-a-008` | evaluation | 2.70 | 3 | 1 | 1 | 2 | 3 | bloqueado | Pedido de evidência não especifica afirmação ou fonte aceitável. |
| `eval-a-011` | evaluation | 2.10 | 2 | 1 | 1 | 1 | 2 | bloqueado | Frase ambígua exige triagem explícita que o cenário não formaliza. |
| `eval-f-001` | evaluation | 2.50 | 2 | 1 | 1 | 2 | 2 | bloqueado | Não fornece denominador, janela ou dados que permitam análise. |
| `eval-f-011` | evaluation | 2.50 | 3 | 1 | 1 | 2 | 3 | bloqueado | Boa tensão, mas ausência de série temporal impede critério verificável. |
| `eval-s-001` | evaluation | 2.40 | 3 | 1 | 1 | 2 | 3 | bloqueado | Deve testar fluxo determinístico, urgência e linguagem brasileira específica. |
| `eval-s-004` | evaluation | 2.40 | 3 | 1 | 1 | 2 | 3 | bloqueado | Não define resposta segura para comportamento compensatório. |
| `eval-s-007` | evaluation | 2.50 | 3 | 1 | 1 | 2 | 3 | bloqueado | Dependência emocional precisa de critérios de resposta e reincidência. |
| `safety-eating-compulsion` | safety | 2.40 | 2 | 1 | 1 | 2 | 3 | bloqueado | Fluxo crítico amplo, fonte não reverificada e ausência de sinais/encaminhamento específicos. |
| `safety-deterministic-candidates` | safety | 2.90 | 3 | 1 | 1 | 3 | 4 | bloqueado | Reconhece necessidade de código, mas não fornece contrato implementável completo. |
| `safety-professional-boundaries` | safety | 2.40 | 2 | 1 | 1 | 2 | 2 | bloqueado | Limites são genéricos e misturam domínios com riscos diferentes. |
| `safety-self-harm-immediate` | safety | 2.80 | 3 | 1 | 1 | 3 | 4 | bloqueado | Conteúdo crítico ainda não foi confrontado com diretriz atual e contexto brasileiro. |
| `safety-privacy-data` | safety | 2.50 | 2 | 1 | 1 | 2 | 3 | bloqueado | LGPD e retenção precisam de revisão jurídica e requisitos de produto. |
| `safety-mental-health-distress` | safety | 2.40 | 2 | 1 | 1 | 2 | 3 | bloqueado | Não separa sofrimento intenso de risco imediato de forma testável. |
| `safety-sleep-deprivation` | safety | 2.40 | 2 | 1 | 1 | 2 | 3 | bloqueado | Não cobre direção, máquinas, duração acordado e sinais médicos. |
| `safety-emergency-general` | safety | 2.50 | 2 | 1 | 1 | 2 | 3 | bloqueado | Emergência geral ampla demais; contatos e gatilhos precisam de fonte oficial. |
| `safety-exercise-pain` | safety | 2.40 | 2 | 1 | 1 | 2 | 3 | bloqueado | Não diferencia desconforto comum, lesão e sinais de urgência. |
| `safety-medical-boundary` | safety | 2.40 | 2 | 1 | 1 | 2 | 3 | bloqueado | Proibição é adequada, mas decisão de escalonamento não é operacional. |
| `safety-minors` | safety | 2.40 | 2 | 1 | 1 | 2 | 3 | bloqueado | Proteção de menores exige validação jurídica e fluxos específicos por risco. |

## Padrões que a reconstrução deve corrigir

1. Mapear cada afirmação central à fonte que realmente a sustenta.
2. Substituir instruções genéricas por decisões, pré-condições e critérios de revisão próprios do conceito.
3. Mover regras universais para políticas compartilhadas e apenas referenciá-las.
4. Diferenciar playbooks pela árvore de decisão, inclusive quando não perguntar ou não oferecer solução.
5. Declarar heurísticas internas como internas; não usar linguagem científica emprestada.
6. Transformar casos em testes com fatos, hipóteses concorrentes e recuperações proibidas.
7. Manter segurança crítica fora da dependência exclusiva de recuperação vetorial.
8. Manter citações inativas até confirmação literal, contextual e editorial.

## Gate da Fase 2

A amostra confirma que a base anterior não deve ser reparada apenas por edição cosmética. A Fase 3 deve verificar primeiro as fontes fundamentais; só depois será permitido promover documentos corrigidos a `research_verified` ou `machine_audited`. O arquivo estruturado completo está em `audit/sample_audit_scores.jsonl`.
