#!/usr/bin/env python3
"""Materializa a auditoria representativa da Fase 2 sem alterar o corpus."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import yaml


RAG = Path(__file__).resolve().parents[1]
OUT = RAG / "audit" / "sample_audit_scores.jsonl"
REPORT = RAG / "SAMPLE_AUDIT_REPORT.md"
CRITERIA = [
    "specificity", "scientific_support", "source_traceability",
    "operational_value", "naturalness", "retrieval_uniqueness",
    "agent_relevance", "safety", "metadata_quality", "copyright_safety",
]


SAMPLES = {
    "knowledge": [
        ("kd-goal-review", [2, 2, 1, 2, 1, 1, 3, 4, 3, 5], "Fontes plausíveis, mas sem mapeamento de afirmações; processo e exemplo são boilerplate."),
        ("kd-behavior-observable", [2, 2, 1, 2, 2, 1, 4, 4, 3, 5], "Conceito útil, porém definição, perguntas e aplicação se repetem em todo knowledge."),
        ("kd-goal-decomposition", [2, 2, 1, 2, 1, 1, 3, 4, 3, 5], "Não oferece algoritmo específico para decompor nem critérios de parada."),
        ("kd-habit-formation", [2, 3, 2, 2, 2, 2, 3, 4, 3, 5], "Tema e fontes são relevantes, mas a síntese não separa automaticidade de repetição."),
        ("kd-procrastination-map", [2, 2, 1, 2, 2, 2, 3, 3, 3, 5], "Não operacionaliza análise funcional nem diferencia adiamento de restrição real."),
        ("kd-spaced-practice", [2, 2, 1, 2, 2, 2, 3, 4, 3, 5], "Falta dose, horizonte, material e contraste com simples repetição."),
        ("kd-sleep-duration", [2, 2, 1, 1, 2, 2, 3, 2, 3, 5], "Recomendação de saúde sem rastreio por faixa etária e sem limites clínicos específicos."),
        ("kd-physical-activity-consistency", [2, 2, 1, 2, 2, 2, 3, 2, 3, 5], "Mistura organização e progressão física sem critérios de segurança suficientes."),
        ("kd-self-compassion-accountability", [2, 2, 1, 2, 2, 2, 3, 3, 3, 5], "Associação entre autocompaixão e ação é ampla demais para a fonte declarada."),
        ("kd-energy-overload", [1, 1, 1, 1, 2, 1, 3, 3, 3, 5], "Construto vago; não distingue sono, carga, doença, humor e conflito de agenda."),
    ],
    "alfred_playbook": [
        ("pb-a-cannot-start", [2, 1, 1, 2, 2, 1, 4, 4, 3, 5], "Resposta padrão não diferencia clareza, habilidade, medo, energia ou ambiente."),
        ("pb-a-tired", [2, 1, 1, 2, 2, 2, 4, 2, 3, 5], "Não faz triagem suficiente entre cansaço comum e sinal médico/privação grave."),
        ("pb-a-no-time", [2, 1, 1, 2, 2, 1, 4, 4, 3, 5], "Reduzir tarefa é resposta padrão; faltam conflito de prioridade e capacidade real."),
        ("pb-a-demotivated", [2, 1, 1, 2, 2, 1, 4, 3, 3, 5], "Não separa ambivalência, meta imposta, anedonia, energia e ausência de sentido."),
        ("pb-a-perfectionist", [2, 1, 1, 2, 2, 2, 4, 3, 3, 5], "Falta árvore entre padrão alto funcional, medo de avaliação e bloqueio de entrega."),
        ("pb-a-medical", [2, 1, 1, 2, 2, 2, 4, 2, 3, 5], "Limite existe, mas encaminhamento e sinais de urgência dependem de texto genérico."),
        ("pb-a-distress", [2, 1, 1, 2, 2, 2, 4, 2, 3, 5], "Não diferencia escuta, crise aguda e risco imediato com critérios operacionais."),
        ("pb-a-emergency", [2, 1, 1, 2, 2, 2, 4, 1, 3, 5], "Playbook crítico não pode depender do RAG e contém risco de ativação lexical frágil."),
    ],
    "feedbacker_playbook": [
        ("pb-f-no-data", [3, 1, 1, 3, 2, 3, 4, 4, 3, 5], "Decisão é distinta, mas ainda usa procedimento e linguagem idênticos aos demais."),
        ("pb-f-low-completion", [2, 1, 1, 2, 2, 1, 4, 4, 3, 5], "Não define denominador, janela, dado ausente nem alternativas ao desempenho baixo."),
        ("pb-f-good-overload", [3, 1, 1, 3, 2, 3, 4, 3, 3, 5], "Conflito útil, mas não define evidência favorável/contrária nem limiar clínico."),
        ("pb-f-incompatible-times", [3, 1, 1, 3, 2, 3, 4, 4, 3, 5], "Padrão observável, porém faltam regras para compromissos flexíveis e dados incompletos."),
        ("pb-f-missing-not-failure", [3, 1, 1, 3, 2, 3, 4, 4, 3, 5], "Distinção importante, mas o procedimento continua intercambiável com outros playbooks."),
    ],
    "case": [
        ("case-a-001", [3, 1, 1, 2, 2, 2, 4, 4, 2, 5], "Contexto concreto, mas a resposta ignora a organização de arquivos observada."),
        ("case-a-005", [2, 1, 1, 2, 2, 1, 3, 4, 2, 5], "Variação superficial com nota de avaliação idêntica."),
        ("case-a-009", [2, 1, 1, 2, 2, 2, 3, 2, 2, 5], "Cansaço não contém triagem nem hipóteses alternativas suficientes."),
        ("case-a-016", [2, 1, 1, 2, 2, 2, 4, 4, 2, 5], "Rejeição do usuário não testa consentimento, recusa ou mudança de objetivo."),
        ("case-a-020", [2, 1, 1, 2, 2, 2, 4, 4, 2, 5], "Pedido científico não testa fonte específica, limite ou modo de referência."),
        ("case-a-025", [2, 1, 1, 2, 2, 2, 4, 1, 2, 5], "Caso médico não declara sinais de urgência nem resposta segura verificável."),
        ("case-f-001", [2, 1, 1, 2, 2, 1, 4, 4, 2, 5], "Não fornece registros reais para calcular ou contestar baixa conclusão."),
        ("case-f-011", [3, 1, 1, 2, 2, 3, 4, 2, 2, 5], "Boa ambiguidade, mas sem série temporal ou evidência contrária."),
        ("case-e-005", [3, 1, 1, 2, 2, 3, 3, 2, 2, 5], "Conflito sobrecarga/privação existe, mas o resultado ideal é genérico."),
        ("case-s-006", [3, 1, 1, 2, 2, 3, 4, 1, 2, 5], "Risco imediato exige critérios e fluxo determinístico, ausentes no caso."),
    ],
    "technique": [
        ("tech-action-planning", [2, 2, 1, 2, 2, 2, 4, 4, 2, 5], "Nome plausível, mas passos genéricos não refletem a definição formal da técnica."),
        ("tech-implementation-intention", [2, 2, 1, 2, 2, 2, 4, 4, 2, 5], "Não documenta relação se–então, contingência, mecanismo nem condições de uso."),
        ("tech-graded-tasks", [2, 2, 1, 2, 2, 2, 4, 4, 2, 5], "Não define gradação, critério de avanço ou origem formal."),
        ("tech-goal-review", [2, 2, 1, 2, 2, 2, 4, 4, 2, 5], "Não distingue revisão do resultado, comportamento, plano ou meta."),
        ("tech-self-monitoring", [2, 2, 1, 2, 2, 2, 4, 3, 2, 5], "Não define variável, frequência, carga de registro nem risco de compulsão."),
        ("tech-retrieval-practice", [2, 2, 1, 2, 2, 3, 4, 4, 2, 5], "Técnica educacional aparece no mesmo molde das técnicas comportamentais."),
        ("tech-minimum-viable-habit", [2, 1, 1, 2, 2, 2, 4, 4, 2, 5], "Heurística interna parece técnica científica; origem não é declarada."),
        ("tech-capacity-budget", [2, 1, 1, 2, 2, 2, 4, 4, 2, 5], "Heurística interna sem definição de capacidade ou base de decisão."),
        ("tech-ask-before-advice", [2, 1, 1, 2, 3, 2, 4, 4, 2, 5], "Política conversacional é rotulada como técnica sem declarar origem interna."),
        ("tech-confidence-calibration", [2, 1, 1, 2, 2, 2, 4, 4, 2, 5], "Não define política low/moderate/high nem evidência necessária."),
    ],
    "quote": [
        (qid, [2, 1, 1, 1, 2, 2, 1, 3, 3, 3], note)
        for qid, note in [
            ("qt-001", "Localização é vaga e tradução própria não foi revisada."),
            ("qt-002", "Texto e edição não foram reverificados; uso temático é amplo."),
            ("qt-008", "Frase pode ser verificável, mas capítulo/página e contexto faltam."),
            ("qt-009", "Tradução depende de edição inglesa intermediária."),
            ("qt-015", "Atribuição precisa ser conferida na edição oficial indicada."),
            ("qt-017", "Ano registrado parece ser da tradução, não da obra original."),
            ("qt-022", "Localização genérica impede rastreabilidade."),
            ("qt-024", "Contexto filosófico pode não sustentar uso comportamental."),
            ("qt-029", "Texto curto, mas tradução e posição na obra não foram auditadas."),
            ("qt-033", "Trecho depende de tradução histórica; contexto ausente."),
            ("qt-036", "Pertinência a motivação foi atribuída editorialmente sem contexto."),
            ("qt-043", "Uso em resiliência pode distorcer o contexto original."),
            ("qt-045", "Autor é introdução anônima, não Marco Aurélio; alto risco editorial."),
            ("qt-050", "Tradução própria e edição intermediária exigem revisão."),
            ("qt-055", "Texto é rastreável em princípio, mas localização continua vaga."),
        ]
    ],
    "evaluation": [
        ("eval-a-001", [2, 1, 1, 2, 2, 2, 4, 3, 2, 5], "Critérios são genéricos e não definem recuperações proibidas."),
        ("eval-a-005", [3, 1, 1, 2, 2, 3, 4, 2, 2, 5], "Tema de privação é relevante, mas o pass/fail de segurança é vago."),
        ("eval-a-006", [3, 1, 1, 2, 2, 3, 4, 1, 2, 5], "Não testa sinais de urgência nem proibição de prescrição."),
        ("eval-a-008", [3, 1, 1, 2, 2, 3, 4, 4, 2, 5], "Pedido de evidência não especifica afirmação ou fonte aceitável."),
        ("eval-a-011", [2, 1, 1, 1, 2, 2, 4, 1, 2, 5], "Frase ambígua exige triagem explícita que o cenário não formaliza."),
        ("eval-f-001", [2, 1, 1, 2, 2, 2, 4, 4, 2, 5], "Não fornece denominador, janela ou dados que permitam análise."),
        ("eval-f-011", [3, 1, 1, 2, 2, 3, 4, 2, 2, 5], "Boa tensão, mas ausência de série temporal impede critério verificável."),
        ("eval-s-001", [3, 1, 1, 2, 2, 3, 4, 1, 2, 5], "Deve testar fluxo determinístico, urgência e linguagem brasileira específica."),
        ("eval-s-004", [3, 1, 1, 2, 2, 3, 4, 1, 2, 5], "Não define resposta segura para comportamento compensatório."),
        ("eval-s-007", [3, 1, 1, 2, 2, 3, 4, 2, 2, 5], "Dependência emocional precisa de critérios de resposta e reincidência."),
    ],
    "safety": [
        ("safety-eating-compulsion", [2, 1, 1, 2, 2, 3, 4, 1, 3, 5], "Fluxo crítico amplo, fonte não reverificada e ausência de sinais/encaminhamento específicos."),
        ("safety-deterministic-candidates", [3, 1, 1, 3, 2, 4, 5, 2, 3, 5], "Reconhece necessidade de código, mas não fornece contrato implementável completo."),
        ("safety-professional-boundaries", [2, 1, 1, 2, 2, 2, 4, 2, 3, 5], "Limites são genéricos e misturam domínios com riscos diferentes."),
        ("safety-self-harm-immediate", [3, 1, 1, 3, 2, 4, 5, 1, 3, 5], "Conteúdo crítico ainda não foi confrontado com diretriz atual e contexto brasileiro."),
        ("safety-privacy-data", [2, 1, 1, 2, 2, 3, 4, 2, 3, 5], "LGPD e retenção precisam de revisão jurídica e requisitos de produto."),
        ("safety-mental-health-distress", [2, 1, 1, 2, 2, 3, 4, 1, 3, 5], "Não separa sofrimento intenso de risco imediato de forma testável."),
        ("safety-sleep-deprivation", [2, 1, 1, 2, 2, 3, 4, 1, 3, 5], "Não cobre direção, máquinas, duração acordado e sinais médicos."),
        ("safety-emergency-general", [2, 1, 1, 2, 2, 3, 5, 1, 3, 5], "Emergência geral ampla demais; contatos e gatilhos precisam de fonte oficial."),
        ("safety-exercise-pain", [2, 1, 1, 2, 2, 3, 4, 1, 3, 5], "Não diferencia desconforto comum, lesão e sinais de urgência."),
        ("safety-medical-boundary", [2, 1, 1, 2, 2, 3, 4, 1, 3, 5], "Proibição é adequada, mas decisão de escalonamento não é operacional."),
        ("safety-minors", [2, 1, 1, 2, 2, 3, 4, 1, 3, 5], "Proteção de menores exige validação jurídica e fluxos específicos por risco."),
    ],
}


def all_ids() -> set[str]:
    found = set()
    for root in ("knowledge", "playbooks", "cases", "safety"):
        for path in (RAG / root).rglob("*.md"):
            fm = yaml.safe_load(path.read_text(encoding="utf-8").split("---", 2)[1])
            found.add(fm.get("id") or fm.get("case_id"))
    for root in ("techniques", "quotes", "evaluation"):
        for path in (RAG / root).glob("*.jsonl"):
            for line in path.read_text(encoding="utf-8").splitlines():
                row = json.loads(line)
                for key in ("technique_id", "quote_id", "scenario_id"):
                    if row.get(key):
                        found.add(row[key])
    return found


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("Auditoria amostral já existe; não sobrescrever sem decisão registrada.")
    existing = all_ids()
    rows = []
    for collection, items in SAMPLES.items():
        for item_id, values, finding in items:
            if item_id not in existing:
                raise SystemExit(f"ID da amostra não encontrado: {item_id}")
            scores = dict(zip(CRITERIA, values, strict=True))
            rows.append({
                "item_id": item_id,
                "collection": collection,
                "scores": scores,
                "mean_score": round(sum(values) / len(values), 2),
                "blocking": any(scores[key] < 4 for key in ("scientific_support", "source_traceability", "safety"))
                or any(scores[key] < 4 for key in ("specificity", "operational_value", "retrieval_uniqueness")),
                "finding": finding,
                "audited_at": "2026-07-13",
                "audit_method": "machine_audit_content_and_metadata_inspection",
                "requires_human_review": True,
            })
    OUT.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    counts = Counter(row["collection"] for row in rows)
    averages = {key: round(sum(row["scores"][key] for row in rows) / len(rows), 2) for key in CRITERIA}
    table = [
        f"| `{row['item_id']}` | {row['collection']} | {row['mean_score']:.2f} | "
        f"{row['scores']['specificity']} | {row['scores']['scientific_support']} | "
        f"{row['scores']['source_traceability']} | {row['scores']['operational_value']} | "
        f"{row['scores']['retrieval_uniqueness']} | {'bloqueado' if row['blocking'] else 'utilizável'} | {row['finding']} |"
        for row in rows
    ]
    report = f"""# Auditoria amostral — Fase 2

Data: 2026-07-13  
Método: inspeção de conteúdo e metadados por modelo; não equivale a revisão humana.

## Escopo

Foram avaliados **{len(rows)} itens**: {', '.join(f'{value} {key}' for key, value in sorted(counts.items()))}.
Todos os documentos de segurança com risco `high` ou `critical` foram incluídos.

## Resultado

- Itens abaixo de pelo menos um limiar obrigatório: **{sum(row['blocking'] for row in rows)} de {len(rows)}**.
- Nenhum item da amostra pode ser ativado sem correção.
- A falha dominante é a combinação de fonte associada ao tema, mas não à afirmação, com conteúdo operacional intercambiável.
- O problema é sistêmico; portanto, quantidade anterior não será usada como meta de preservação.

### Médias por critério

| Critério | Média / 5 |
|---|---:|
{chr(10).join(f'| {key} | {value:.2f} |' for key, value in averages.items())}

## Notas por item

| ID | Coleção | Média | Especificidade | Evidência | Rastreabilidade | Operacional | Unicidade | Decisão | Achado principal |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
{chr(10).join(table)}

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
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps({"status": "ok", "items": len(rows), "blocked": sum(row["blocking"] for row in rows), "counts": counts}, ensure_ascii=False, default=dict))


if __name__ == "__main__":
    main()
