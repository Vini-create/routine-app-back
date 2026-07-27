# Padrão de conteúdo corrigido

Versão: 2.0.1  
Status: `machine_audited`  
Revisão humana: obrigatória

## Unidade editorial

Um documento existe para apoiar uma decisão recuperável distinta. Título ou
domínio diferente não justificam um novo arquivo se entrada, decisão e saída
forem as mesmas.

Todo documento ativo deve responder, com conteúdo próprio:

1. qual situação observável o ativa;
2. quais situações parecidas não o ativam;
3. qual decisão ele ajuda o agente a tomar;
4. quais dados são necessários;
5. quais hipóteses concorrentes devem permanecer abertas;
6. qual procedimento concreto pode ser executado;
7. qual resultado faz manter, alterar, interromper ou escalar;
8. quais fontes sustentam cada afirmação científica.

## Evidência

Uma lista de `source_ids` não é rastreabilidade suficiente. Knowledge e técnica
científica devem conter `supported_claims`, e o corpo deve apresentar
“Mapeamento das evidências” com afirmação, fonte, suporte e força.

Forças permitidas:

- `institutional_guideline`
- `systematic_review`
- `meta_analysis`
- `randomized_trial`
- `observational_study`
- `seminal_theory`
- `canonical_framework`
- `academic_textbook`
- `expert_interpretation`
- `internal_heuristic`
- `popular_book`

`internal_heuristic` e `popular_book` não constituem comprovação científica.
Resultados agregados não explicam automaticamente um caso individual.

## Operação e exemplos

Procedimentos usam verbos e critérios verificáveis: identificar, comparar,
classificar, selecionar, registrar, interromper e revisar. Expressões como
“aplicar o princípio” não contam como passo.

Exemplos precisam conter contexto, decisão e justificativa curta. Não podem
recitar a definição, terminar obrigatoriamente com pergunta ou repetir uma
estrutura fixa entre documentos.

Perguntas úteis devem existir para discriminar alternativas ou coletar o dado
que muda a decisão do documento. Não podem ser copiadas como template entre
temas. A lista é um conjunto de candidatas: o agente seleciona somente a
pergunta necessária para o próximo passo, salvo quando o usuário pedir uma
avaliação estruturada.

## Recuperação

Cada unidade ativa deve incluir linguagem real em `retrieval_terms` ou
`trigger_phrases`, além de relações e contrastes apenas com IDs existentes.

Somente `machine_audited` e `human_reviewed` podem ser indexados. Nesta
reconstrução, o máximo é `machine_audited` com
`requires_human_review: true`.

## Gate de ativação

Notas mínimas:

- specificity ≥ 4
- traceability ≥ 4
- actionability ≥ 4
- retrieval_value ≥ 4
- safety ≥ 4
- evidence ≥ 4 para conteúdo científico

Item abaixo do limite deve ser reescrito, fundido, depreciado ou colocado em
quarentena. Quantidade não é critério de qualidade.
