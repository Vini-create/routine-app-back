---
id: pb-shared-agent-routing
title: Roteamento entre Alfred, Feedbacker e segurança
document_type: playbook
domain: communication
agents:
- alfred
- feedbacker
trigger_phrases: &id001
- qual agente responde
- análise ou conversa
- fluxo de segurança
use_when: *id001
source_ids: []
language: pt-BR
version: 2.0.0
status: machine_audited
requires_human_review: true
index_eligible: false
risk_level: low
last_machine_audited_at: '2026-07-13'
---

# Roteamento entre Alfred, Feedbacker e segurança

Alfred conduz objetivo conversacional; Feedbacker analisa registros estruturados; segurança interrompe ambos quando há gatilho crítico. Feedbacker não inventa contexto conversacional e Alfred não apresenta análise quantitativa sem dados. Regras críticas devem ser acionadas no código antes da recuperação vetorial.
