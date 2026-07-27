# Relatório de qualidade

Data: 2026-07-13  
Fases concluídas: 1–8

## Resultado atual

A reconstrução intermediária passou nos gates das Fases 2–8, mas a base ainda
**não está aprovada para produção**.

- 75 documentos Markdown correspondem exatamente a 75 entradas do registro.
- 12 knowledge, 21 playbooks e 30 casos foram reconstruídos e auditados por
  máquina.
- 12 técnicas foram reconstruídas com origem e evidência declaradas.
- 27 de 31 fontes foram reverificadas; quatro fontes editoriais aguardam a
  auditoria de citações.
- 75 unidades `machine_audited` possuem score completo e atingem os limiares
  intermediários.
- 210 registros anteriores estão preservados e inativos em quarentena.
- Zero parágrafos literais repetidos no conteúdo reconstruído.
- Zero documentos ou registros elegíveis para produção.
- Zero estados `human_reviewed` atribuídos pelo processo automatizado.

## Validações

- `audit/phase8_structural_validation.json`: JSON, JSONL, YAML, estados, fontes,
  IDs, caminhos, registries e relações.
- `audit/phase8_quality_validation.json`: cobertura dos scores, limiares,
  quarentena e duplicação literal.
- Compilação de todos os scripts Python concluída sem erro.

## Limites restantes

- Citações não foram auditadas — Fase 9.
- Segurança crítica continua legada e inativa — Fase 10.
- Evaluation continua gerada e inativa — Fase 11.
- Similaridade semântica e decisões de fusão finais pertencem à Fase 12.
- Registries, índice e elegibilidade definitivos pertencem à Fase 13.
- Testes e relatórios finais pertencem às Fases 14–15.

Execute `.venv/bin/python rag/scripts/validate_rag.py` e
`.venv/bin/python rag/scripts/validate_phase2_8.py`.
