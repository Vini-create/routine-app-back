#!/usr/bin/env python3
"""Aplica a verificação bibliográfica documentada da Fase 3."""

from __future__ import annotations

import json
from pathlib import Path


RAG = Path(__file__).resolve().parents[1]
REGISTRY = RAG / "source_registry.jsonl"
AUDIT = RAG / "audit" / "phase3_source_verification.jsonl"
ACCESSED = "2026-07-13"


ACADEMIC = {
    "src-bcttv1-2013": {"pmid": "23512568", "volume": "46", "issue": "1", "pages": "81-95", "verification_url": "https://openaccess.city.ac.uk/id/eprint/3293/"},
    "src-bcto-2024": {"pmid": "37593567", "pmcid": "PMC10427801", "volume": "8", "article_number": "308", "verification_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC10427801/"},
    "src-ii-2006": {"volume": "38", "pages": "69-119", "verification_url": "https://www.sciencedirect.com/science/article/abs/pii/S0065260106380021"},
    "src-intention-behavior-2006": {"pmid": "16536643", "volume": "132", "issue": "2", "pages": "249-268", "verification_url": "https://pubmed.ncbi.nlm.nih.gov/16536643/"},
    "src-goal-setting-2017": {"pmid": "29189034", "volume": "85", "issue": "12", "pages": "1182-1198", "verification_url": "https://doi.org/10.1037/ccp0000260"},
    "src-self-regulation-2020": {"pmid": "31662031", "pmcid": "PMC7571594", "volume": "14", "issue": "1", "pages": "6-42", "verification_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC7571594/"},
    "src-sdt-rct-2020": {"pmid": "32437175", "volume": "88", "issue": "8", "pages": "726-737", "verification_url": "https://pubmed.ncbi.nlm.nih.gov/32437175/"},
    "src-sdt-techniques-2019": {"pmid": "30295176", "verification_url": "https://selfdeterminationtheory.org/wp-content/uploads/2019/03/2019_GillisonEtAl_HPR_MetaAnalysis.pdf"},
    "src-habit-lally-2010": {"volume": "40", "issue": "6", "pages": "998-1009", "verification_url": "https://openresearch.surrey.ac.uk/esploro/outputs/99783513802346"},
    "src-habit-review-2024": {"pmid": "39685110", "pmcid": "PMC11641623", "volume": "12", "issue": "23", "article_number": "2488", "verification_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC11641623/"},
    "src-context-stability-2022": {"pmid": "35756236", "pmcid": "PMC9226889", "volume": "13", "article_number": "883795", "verification_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC9226889/"},
    "src-procrastination-steel-2007": {"pmid": "17201571", "volume": "133", "issue": "1", "pages": "65-94", "verification_url": "https://pubmed.ncbi.nlm.nih.gov/17201571/"},
    "src-procrastination-treatment-2018": {"pmid": "30214421", "pmcid": "PMC6125391", "volume": "9", "article_number": "1588", "verification_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC6125391/"},
    "src-learning-dunlosky-2013": {"pmid": "26173288", "volume": "14", "issue": "1", "pages": "4-58", "verification_url": "https://pubmed.ncbi.nlm.nih.gov/26173288/"},
    "src-retrieval-meta-2021": {"pmid": "33683913", "volume": "147", "issue": "4", "pages": "399-435", "verification_url": "https://pubmed.ncbi.nlm.nih.gov/33683913/"},
    "src-spacing-review-2024": {"pmid": "37615780", "pmcid": "PMC11078833", "volume": "29", "issue": "2", "pages": "689-714", "verification_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC11078833/"},
    "src-sleep-aasm-2015": {"pmid": "25979105", "pmcid": "PMC4442216", "volume": "11", "issue": "6", "pages": "591-592", "verification_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC4442216/"},
    "src-sleep-nsf-2015": {"pmid": "29073398", "verification_url": "https://pubmed.ncbi.nlm.nih.gov/29073398/"},
    "src-self-compassion-2021": {"pmid": "31842689", "volume": "15", "issue": "1", "pages": "113-139", "verification_url": "https://pubmed.ncbi.nlm.nih.gov/31842689/"},
    "src-perfectionism-2024": {"pmid": "37955236", "volume": "53", "issue": "2", "pages": "121-132", "verification_url": "https://doi.org/10.1080/16506073.2023.2277121"},
}

INSTITUTIONAL = {
    "src-who-pa-2020": {"verification_url": "https://www.who.int/publications/i/item/9789240014886", "isbn": "978-92-4-001488-6"},
    "src-cdc-pa-adults": {"verification_url": "https://www.cdc.gov/physical-activity-basics/adding-adults/index.html", "url": "https://www.cdc.gov/physical-activity-basics/adding-adults/index.html", "publication_year": 2025},
    "src-who-suicide": {"verification_url": "https://www.who.int/news-room/questions-and-answers/item/suicide"},
    "src-nice-self-harm-2022": {"verification_url": "https://www.nice.org.uk/guidance/ng225", "guideline_id": "NG225"},
    "src-ms-suicide-br": {"verification_url": "https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/s/suicidio-prevencao/suicidio-prevencao"},
    "src-samu-192": {"verification_url": "https://www.gov.br/saude/pt-br/composicao/saes/samu-192/samu-192", "url": "https://www.gov.br/saude/pt-br/composicao/saes/samu-192/samu-192"},
    "src-lgpd": {"verification_url": "https://planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm", "url": "https://planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm", "legal_identifier": "Lei nº 13.709/2018"},
}

LIMITATIONS = {
    "src-bcttv1-2013": "Taxonomia padroniza descrição de componentes; não prova eficácia isolada de cada técnica.",
    "src-bcto-2024": "Ontologia de descrição em evolução; não é guia de eficácia clínica.",
    "src-goal-setting-2017": "Efeito médio pequeno e heterogêneo; moderadores não garantem resultado individual.",
    "src-habit-lally-2010": "Estudo observacional pequeno; tempo de formação variou amplamente e não define prazo universal.",
    "src-habit-review-2024": "A maioria dos estudos incluídos teve alto risco de viés; comportamentos avaliados foram limitados.",
    "src-context-stability-2022": "Dois estudos específicos não justificam causalidade universal em todos os comportamentos.",
    "src-procrastination-treatment-2018": "Poucos ensaios, heterogeneidade e algum risco de viés; não sustenta prescrição clínica pelo produto.",
    "src-self-regulation-2020": "Meta-análises subjacentes tinham qualidade variável e poucos testes diretos de mecanismo.",
    "src-sdt-rct-2020": "Efeitos médios pequenos e com viés de publicação/amostras pequenas.",
    "src-learning-dunlosky-2013": "Utilidade varia por material, estudante, tarefa e condição de aprendizagem.",
    "src-retrieval-meta-2021": "Efeito depende de formato, feedback, correspondência do material e desenho.",
    "src-spacing-review-2024": "Escopo é educação de profissões da saúde e os estudos são heterogêneos.",
    "src-self-compassion-2021": "Grande parte da síntese é associacional; intervenções de sessão única não tiveram efeito significativo.",
    "src-perfectionism-2024": "Associação com sintomas não autoriza diagnóstico individual.",
    "src-sleep-aasm-2015": "Recomendação de consenso para adultos saudáveis; não individualiza necessidade nem substitui avaliação.",
    "src-sleep-nsf-2015": "Faixas de consenso por idade não são prescrição individual.",
    "src-who-pa-2020": "Diretriz populacional; progressão e contraindicações individuais exigem avaliação adequada.",
    "src-cdc-pa-adults": "Orientação geral para adultos; condições crônicas e atividade vigorosa exigem cautela.",
    "src-who-suicide": "Material informativo global; contatos e fluxos devem ser localizados para o Brasil.",
    "src-nice-self-harm-2022": "Diretriz para profissionais e sistema britânico; adaptar serviços e legislação ao Brasil.",
    "src-ms-suicide-br": "Página pública brasileira; sinais não devem ser usados isoladamente como predição.",
    "src-samu-192": "Define o serviço brasileiro; disponibilidade e cobertura local ainda podem variar.",
    "src-lgpd": "Texto legal exige interpretação e revisão jurídica para decisões de produto.",
}


def main() -> None:
    if AUDIT.exists():
        raise SystemExit("Verificação da Fase 3 já registrada; não sobrescrever.")
    rows = [json.loads(line) for line in REGISTRY.read_text(encoding="utf-8").splitlines() if line]
    changes = []
    targets = set(ACADEMIC) | set(INSTITUTIONAL)
    for row in rows:
        sid = row["source_id"]
        before = {key: row.get(key) for key in ("verification_status", "url", "publication_year", "active")}
        if sid in ACADEMIC:
            row.update(ACADEMIC[sid])
            row["verification_status"] = "verified_official_repository"
            row["verification_basis"] = "publisher_or_scientific_repository_metadata"
            row["active"] = True
        elif sid in INSTITUTIONAL:
            row.update(INSTITUTIONAL[sid])
            row["verification_status"] = "verified_primary"
            row["verification_basis"] = "official_institutional_or_legal_source"
            row["active"] = True
        else:
            row["verification_status"] = "requires_human_review"
            row["active"] = False
            row["verification_basis"] = "deferred_to_quote_audit_phase_9"
        row["last_verified_at"] = ACCESSED if sid in targets else None
        row["accessed_at"] = ACCESSED if sid in targets else row.get("accessed_at")
        row["verified_by"] = "machine_research"
        row["requires_human_review"] = True
        if sid in LIMITATIONS:
            row["scope_limitations"] = LIMITATIONS[sid]
        changes.append({
            "source_id": sid,
            "before": before,
            "after": {key: row.get(key) for key in ("verification_status", "url", "publication_year", "active", "verification_url", "pmid", "pmcid")},
            "decision": "verified" if sid in targets else "deferred",
            "requires_human_review": True,
        })
    if set(row["source_id"] for row in rows) != set(ACADEMIC) | set(INSTITUTIONAL) | {"src-marcus-gutenberg", "src-epictetus-gutenberg", "src-james-gutenberg", "src-dewey-gutenberg"}:
        raise SystemExit("Mapa de verificação não cobre exatamente o registro atual.")
    REGISTRY.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    AUDIT.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in changes), encoding="utf-8")
    print(json.dumps({"status": "ok", "verified": len(targets), "deferred": len(rows) - len(targets)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
