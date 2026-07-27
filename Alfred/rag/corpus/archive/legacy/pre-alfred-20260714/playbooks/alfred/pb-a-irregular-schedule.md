---
id: pb-a-irregular-schedule
title: Rotina variável e oportunidades por evento
document_type: playbook
domain: coaching
agents:
- alfred
trigger_phrases: &id001
- meus horários mudam
- trabalho por turnos
- cada dia é diferente
- não consigo horário fixo
use_when: *id001
source_ids: []
language: pt-BR
version: 2.0.0
status: machine_audited
requires_human_review: true
index_eligible: false
risk_level: low
last_machine_audited_at: '2026-07-13'
related_knowledge:
- kd-action-planning
- kd-if-then-plans
- kd-habit-formation
candidate_techniques:
- tech-action-planning
- tech-implementation-intention
- tech-prompts-cues
---

# Rotina variável e oportunidades por evento

## Critérios de ativação

Horários variam, mas existem eventos, janelas ou tipos de dia reconhecíveis.

## Situações semelhantes que não devem ativá-lo

Não ativar quando a agenda está simplesmente sobrecarregada ou quando nenhum evento é controlável.

## O que pode estar acontecendo

Planejamento por relógio pode ser incompatível; âncoras por evento ou planos por tipo de dia podem funcionar melhor.

## O que ainda não sabemos

Eventos recorrentes; antecedência da escala; janelas mínimas; deslocamento; sono e recuperação.

## Árvore de decisão

- Se existe evento estável, ancorar uma ação curta a ele.
- Se há poucos tipos de dia, criar plano A/B em vez de sete rotinas.
- Se a escala chega tarde, planejar prioridade e capacidade, não horário fixo.
- Se turno compromete sono/segurança, priorizar fluxo apropriado.

## Conhecimentos relacionados

`kd-action-planning`, `kd-if-then-plans`, `kd-habit-formation`

## Técnicas candidatas e condições

`tech-action-planning`, `tech-implementation-intention`, `tech-prompts-cues`

## Como responder naturalmente

Reconhecer variabilidade real e evitar culpa por não manter horário fixo.

## Quando não fazer pergunta

Quando o evento recorrente e a ação já estão claros.

## Quando não oferecer solução

Quando o cronograma depende totalmente de terceiros e não há janela segura.

## Quando usar referência científica

Pode explicar estabilidade contextual sob pedido, deixando claro que não precisa ser horário idêntico.

## Quando encerrar ou mudar de fluxo

Encerrar com uma âncora ou regra por tipo de dia, não uma grade semanal fictícia.

## Segurança

Turnos com sonolência perigosa ou privação importante exigem triagem antes de qualquer âncora de rotina.
