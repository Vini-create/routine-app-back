---
id: pb-shared-reference-modes
title: Modos de referência científica
document_type: playbook
domain: communication
agents:
- alfred
- feedbacker
trigger_phrases: &id001
- citar fonte
- quando mostrar estudo
- sem referência
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

# Modos de referência científica

`no_reference` para conversa comum; `indirect_reference` para síntese não controversa; `explicit_source_explanation` quando houver pedido, número ou recomendação contestável. Citação curta permanece desativada até a Fase 9. Nunca usar referência para decorar resposta ou vencer recusa.
