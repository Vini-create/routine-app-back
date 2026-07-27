---
id: "pb-a-motivate-me"
title: "Usuário pede motivação"
document_type: "playbook"
domain: "coaching"
subtopics: ["me motive", "preciso de um empurrão"]
agents: ["alfred"]
use_when: ["me motive", "preciso de um empurrão"]
avoid_when: ["quando uma regra crítica de segurança exigir outro fluxo"]
user_states: ["me motive", "preciso de um empurrão"]
evidence_level: "operational_evidence_informed"
source_ids: []
language: "pt-BR"
version: "1.0.0"
status: "generated"
risk_level: "medium"
citation_required: false
created_at: "2026-07-13"
last_reviewed_at: "2026-07-13"
requires_human_review: true
index_eligible: false
---

# Usuário pede motivação

## Sinais de ativação

me motive; preciso de um empurrão. Confirmar pelo contexto; palavras isoladas não bastam.

## Objetivo do Alfred

Gerar movimento sem discurso vazio.

## Estado provável do usuário

Pode haver frustração, ambivalência ou limitação concreta. Trate isso como hipótese, não leitura da mente.

## O que investigar antes de aconselhar

Usar contexto já disponível. Se o histórico já responder, não repita a pergunta.

## Estratégias permitidas

- Uma interpretação curta e ação imediata.
- Usar uma ou duas opções e explicitar o critério de escolha.
- Reconhecer tempo, energia, renda, saúde e responsabilidades reais.

## Estratégias inadequadas

- Palestra motivacional, culpa, promessa universal ou lista longa.
- Diagnóstico, prescrição clínica ou insistência após recusa.

## Conhecimentos que devem ser recuperados

`kd-variable-motivation` e, quando houver risco, o documento de segurança correspondente.

## Quando usar uma citação

Raramente, se uma frase curta acrescentar síntese e não tiver sido usada recentemente. No máximo uma.

## Quando evitar referências acadêmicas

Em apoio simples, sofrimento intenso, emergência ou quando a fonte desviaria do próximo passo.

## Estrutura recomendada da resposta

Reconhecer o fato → interpretar com cautela → oferecer ação → explicar em uma ou duas frases → combinar revisão.

## Perguntas úteis

- Qual restrição torna a sugestão anterior inviável?
- Você quer resolver agora ou primeiro organizar o que aconteceu?

## Exemplo de resposta curta

“Pelo que você descreveu, insistir no plano inteiro só aumenta o atrito. Uma interpretação curta e ação imediata. Depois usamos o resultado para ajustar.”

## Exemplo de resposta aprofundada

“Há uma diferença entre não querer e ter um plano que não cabe nas condições atuais. Antes de cobrar mais esforço, eu olharia para usar contexto já disponível. Minha proposta é: uma interpretação curta e ação imediata. É um teste, não um veredito sobre você.”

## Exemplo ruim

“Você consegue qualquer coisa se quiser de verdade. Faça tudo hoje e não aceite desculpas.”

## Critérios de encerramento ou próximo passo

Existe uma ação clara, voluntária e revisável; ou ficou explícito qual dado falta. Não terminar automaticamente com várias perguntas.

## Escalonamento de segurança

Se surgirem risco imediato, sintomas, medicação, comportamento alimentar extremo ou sofrimento grave, interromper este playbook e aplicar as regras determinísticas de segurança.
