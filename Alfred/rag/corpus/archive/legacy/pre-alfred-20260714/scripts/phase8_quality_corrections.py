#!/usr/bin/env python3
"""Remove boilerplate residual encontrado no fechamento das Fases 7–8."""

import json
from pathlib import Path
import yaml

RAG=Path(__file__).resolve().parents[1]; LOG=RAG/"audit"/"phase8_quality_corrections.jsonl"
if LOG.exists(): raise SystemExit("Correções de qualidade já aplicadas.")

alfred_safety={
"pb-a-cannot-start":"Escalonar somente se o episódio trouxer sofrimento agudo, sintoma ou perigo; dificuldade de início isolada não é crise.",
"pb-a-no-time":"Não sugerir cortar sono, cuidado essencial, tratamento ou medida de segurança para fazer a agenda caber.",
"pb-a-tired":"Sonolência ao dirigir, desmaio, dor no peito ou falta de ar interrompem este playbook e acionam segurança.",
"pb-a-demotivated":"Perda ampla de interesse com sofrimento importante não deve ser tratada como simples escolha motivacional.",
"pb-a-perfectionist":"Compulsão intensa, alimentação, autoagressão ou prejuízo grave saem do escopo de critério de pronto.",
"pb-a-listen":"O pedido de escuta não impede uma checagem breve quando houver indício concreto de perigo imediato.",
"pb-a-rejects":"Respeitar recusa não significa omitir uma ação de segurança necessária diante de perigo concreto.",
"pb-a-science":"Em saúde e risco, priorizar diretriz institucional atual e não transformar estudo em aconselhamento individual.",
"pb-a-irregular-schedule":"Turnos com sonolência perigosa ou privação importante exigem triagem antes de qualquer âncora de rotina.",
"pb-a-safety-handoff":"Este playbook apenas interrompe coaching; a resposta concreta pertence à camada determinística validada e localizada.",
}
empty_tech={
"pb-a-tired":"Nenhuma antes da triagem; organização de rotina só pode voltar depois de afastado o risco imediato.",
"pb-a-listen":"Nenhuma enquanto o pedido explícito continuar sendo apenas escuta.",
"pb-a-science":"Nenhuma por padrão; responder primeiro à afirmação e à evidência solicitada.",
"pb-a-safety-handoff":"Nenhuma técnica de coaching é permitida durante o handoff de segurança.",
}
feedback_limits={
"pb-f-confidence-guide":"A confiança qualifica suporte nos registros, nunca chance clínica, verdade subjetiva ou causalidade.",
"pb-f-data-coverage":"Sem cobertura representativa, o Feedbacker deve se abster de classificar desempenho.",
"pb-f-low-completion":"Uma taxa descreve ocorrências válidas e não explica capacidade, intenção ou caráter.",
"pb-f-capacity-mismatch":"Confiança alta pode valer para a sobreposição observada, não para o motivo de ela ter sido criada.",
"pb-f-day-pattern":"Diferença entre dias não identifica qual variável contextual produziu a diferença.",
"pb-f-good-overload":"Métricas de conclusão não podem neutralizar sintomas, privação ou outro sinal de segurança.",
"pb-f-postponed":"Reagendamento repetido sustenta revisão da decisão, não diagnóstico de motivação.",
"pb-f-goal-no-actions":"Ausência de ação no sistema pode refletir integração; conferir antes de atribuir omissão ao usuário.",
"pb-f-recovery-trend":"Melhora temporal após uma mudança não demonstra que a mudança causou a melhora.",
}
changes=[]
for path in sorted((RAG/"playbooks").rglob("*.md")):
    text=path.read_text(encoding="utf-8"); fm=yaml.safe_load(text.split("---",2)[1]); pid=fm["id"]; old=text
    if pid in alfred_safety:
        text=text.replace("Aplicar a camada determinística antes do RAG sempre que houver gatilho crítico; este playbook não substitui triagem profissional.",alfred_safety[pid])
    if pid in empty_tech:
        text=text.replace("Nenhuma técnica de coaching deve ser aplicada neste fluxo.",empty_tech[pid])
    if pid in feedback_limits:
        text=text.replace("Confiança qualitativa não prova causalidade e não autoriza diagnóstico.",feedback_limits[pid])
    if text!=old:
        path.write_text(text,encoding="utf-8"); changes.append({"document_id":pid,"path":path.relative_to(RAG).as_posix(),"change":"centralize_universal_rule_and_keep_specific_limit"})
LOG.write_text("".join(json.dumps(x,ensure_ascii=False)+"\n" for x in changes),encoding="utf-8")
print(json.dumps({"status":"ok","documents_corrected":len(changes)}))
