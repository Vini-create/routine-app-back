# Política de estados editoriais

## Estados de documento

- `draft`: rascunho humano ou misto incompleto.
- `generated`: material produzido por automação e ainda não verificado.
- `research_verified`: fontes e afirmações foram confrontadas, mas a unidade
  ainda não passou por todos os testes de qualidade.
- `machine_audited`: fontes, estrutura, relações, qualidade e segurança passaram
  nos gates automatizados e na inspeção por modelo.
- `human_reviewed`: somente uma pessoa autorizada pode aplicar.
- `deprecated`: preservado por histórico, excluído de recuperação.
- `quarantined`: decisão pendente ou risco não resolvido; excluído de registros
  ativos, índice e embeddings.

Durante esta reconstrução, `machine_audited` é o teto e sempre mantém
`requires_human_review: true`.

## Elegibilidade

`index_eligible: true` exige `machine_audited` ou `human_reviewed`, nota mínima
por arquivo, fontes suficientes e ausência de referência inválida. Quarentena e
depreciação são sempre inelegíveis.

## Autorização humana

Promoção a `human_reviewed` exige identidade do revisor, função, data, escopo e
registro externo de autorização. Ausência de qualquer campo invalida a promoção.
