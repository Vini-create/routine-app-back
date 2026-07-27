#!/usr/bin/env python3
"""Gera o inventário e o baseline imutável da reconstrução de qualidade.

Este script documenta o conteúdo capturado no checkpoint anterior à auditoria.
Ele não avalia mérito científico e não promove nenhum status editorial.
"""

from __future__ import annotations

import collections
import hashlib
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RAG = ROOT / "rag"
AUDIT = RAG / "audit"
CHECKPOINT = ROOT / ".audit_checkpoints" / "rag-pre-rebuild-20260713.tar.gz"
CHECKPOINT_SHA256 = "a2a8e29412c5a923b9df291362dccdac7235265a9b9824189529b084be8044e4"
SNAPSHOT_AT = "2026-07-13T20:42:41-03:00"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def baseline_files() -> list[Path]:
    excluded = {
        "scripts/audit_phase1.py",
        "AUDIT_BASELINE.md",
        "CHANGELOG.md",
    }
    return sorted(
        p
        for p in RAG.rglob("*")
        if p.is_file()
        and p.relative_to(RAG).as_posix() not in excluded
        and not p.is_relative_to(AUDIT)
    )


def extract_status(text: str) -> str | None:
    match = re.search(r'^status:\s*["\']?([^"\'\n]+)', text, re.MULTILINE)
    return match.group(1).strip() if match else None


def main() -> None:
    AUDIT.mkdir(parents=True, exist_ok=True)
    inventory_path = AUDIT / "baseline_file_inventory.jsonl"
    report_path = RAG / "AUDIT_BASELINE.md"
    if inventory_path.exists() or report_path.exists():
        raise SystemExit(
            "BASELINE IMUTÁVEL JÁ EXISTE: remova-o somente mediante decisão "
            "editorial registrada e restauração consciente do checkpoint."
        )
    files = baseline_files()
    inventory = []
    for path in files:
        inventory.append(
            {
                "path": path.relative_to(RAG).as_posix(),
                "size_bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    inventory_path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in inventory),
        encoding="utf-8",
    )

    by_top = collections.Counter(row["path"].split("/", 1)[0] for row in inventory)
    by_suffix = collections.Counter(Path(row["path"]).suffix or "<sem extensão>" for row in inventory)
    markdown_status = collections.Counter()
    markdown_without_status = 0
    for path in files:
        if path.suffix != ".md":
            continue
        status = extract_status(path.read_text(encoding="utf-8"))
        if status:
            markdown_status[status] += 1
        else:
            markdown_without_status += 1

    sources = [json.loads(line) for line in (RAG / "source_registry.jsonl").read_text(encoding="utf-8").splitlines() if line]
    documents = [json.loads(line) for line in (RAG / "document_registry.jsonl").read_text(encoding="utf-8").splitlines() if line]
    source_states = collections.Counter(row.get("verification_status", "<ausente>") for row in sources)
    document_states = collections.Counter(row.get("status", "<ausente>") for row in documents)
    raw_git_status = subprocess.run(
        ["git", "status", "--short"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip().splitlines()
    git_status = [
        line
        for line in raw_git_status
        if not line.strip().endswith("rag/")
        and not line.strip().endswith(".audit_checkpoints/")
    ]

    repeat_findings = [
        (48, "Princípio central idêntico em todos os documentos de knowledge."),
        (48, "Mesmo bloco de sinais, hipóteses e dados ausentes em knowledge."),
        (48, "Mesmas três perguntas em knowledge, independentemente do conceito."),
        (48, "Mesmos textos de aplicação por Alfred e Feedbacker em knowledge."),
        (28, "Mesma estrutura de resposta e perguntas nos playbooks do Alfred."),
        (16, "Mesmo procedimento de teste de sete dias nos playbooks do Feedbacker."),
        (75, "Mesma nota de avaliação nos casos."),
    ]

    source_lines = [
        f"- `{row['source_id']}` — {row['title']} — estado anterior: `{row.get('verification_status', '<ausente>')}`"
        for row in sources
    ]
    top_lines = [f"| `{key}` | {value} |" for key, value in sorted(by_top.items())]
    suffix_lines = [f"| `{key}` | {value} |" for key, value in sorted(by_suffix.items())]
    git_lines = [f"- `{line}`" for line in git_status]
    repeat_lines = [f"- {count} ocorrências: {description}" for count, description in repeat_findings]

    report = f'''# Baseline da auditoria da base RAG

Snapshot: `{SNAPSHOT_AT}`  
Branch: `master`  
HEAD anterior: `b808d0f rag demo added`

## Checkpoint de segurança

- Arquivo: `.audit_checkpoints/rag-pre-rebuild-20260713.tar.gz`
- SHA-256: `{CHECKPOINT_SHA256}`
- Tamanho: `{CHECKPOINT.stat().st_size if CHECKPOINT.exists() else 'não encontrado'} bytes`
- Escopo: cópia integral dos 220 arquivos existentes em `rag/` antes da reconstrução.
- Inventário com hash por arquivo: `rag/audit/baseline_file_inventory.jsonl`.

As alterações preexistentes fora de `rag/` não foram incluídas no checkpoint:

{chr(10).join(git_lines)}

## Inventário

- Arquivos: **{len(inventory)}**
- Bytes lógicos: **{sum(row['size_bytes'] for row in inventory)}**
- Documentos no registro: **{len(documents)}**
- Fontes no registro: **{len(sources)}**

### Por área

| Área | Arquivos |
|---|---:|
{chr(10).join(top_lines)}

### Por extensão

| Extensão | Arquivos |
|---|---:|
{chr(10).join(suffix_lines)}

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

- `reviewed`: {markdown_status.get('reviewed', 0)}
- `human_review_required`: {markdown_status.get('human_review_required', 0)}
- sem `status`: {markdown_without_status}

### `document_registry.jsonl`

- `reviewed`: {document_states.get('reviewed', 0)}
- `human_review_required`: {document_states.get('human_review_required', 0)}

### `source_registry.jsonl`

- `verified`: {source_states.get('verified', 0)}

Esses estados são apenas o que a geração anterior declarava. Nenhum deles constitui revisão humana ou reverificação científica na reconstrução atual. Todo conteúdo anterior passa a ser tratado como `unverified_generated_draft` até decisão posterior.

## Acesso externo

O acesso à internet foi confirmado em {SNAPSHOT_AT}: páginas institucionais da OMS e do NICE abriram integralmente. O PubMed direto apresentou desafio anti-bot; nas fases científicas serão usados resultados indexados, PMC, APIs/repositórios NCBI ou páginas do periódico. A pesquisa científica pode prosseguir sem simulação.

## Problemas estruturais iniciais

{chr(10).join(repeat_lines)}

Outros riscos observados:

- `reviewed` foi aplicado sem revisão humana demonstrável.
- O registro de fontes usa um estado genérico `verified`, incompatível com os estados bibliográficos exigidos agora.
- O validador anterior verifica estrutura e contagens, mas não qualidade científica, unicidade semântica ou autorização de `human_reviewed`.
- `source_ids` aparecem associados ao documento inteiro, sem mapeamento de afirmações.
- Casos e exemplos compartilham boilerplate e testam poucas decisões realmente distintas.
- Existem arquivos `__pycache__` dentro da árvore RAG, inadequados para o corpus e para versionamento.
- O gerador anterior pode reintroduzir status e boilerplate se executado sem ser corrigido.

## Fontes registradas no baseline

{chr(10).join(source_lines)}

## Decisão da Fase 1

Nenhum arquivo tem qualidade presumida por estar bem formatado. Antes da amostra da Fase 2, os estados serão migrados para `generated` com `requires_human_review: true`; conteúdo não auditado ficará inelegível para indexação de produção.
'''
    report_path.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
