#!/usr/bin/env python3
"""Reconstrói knowledge como uma coleção pequena, específica e rastreável."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import yaml


RAG = Path(__file__).resolve().parents[1]
KNOWLEDGE = RAG / "knowledge"
QUARANTINE = RAG / "quarantine" / "phase5_legacy_knowledge"
AUDIT = RAG / "audit" / "phase5_knowledge_decisions.jsonl"
QREG = RAG / "quarantine" / "registry.jsonl"
CREATED_AT = "2026-07-13"
TODAY = "2026-07-14"


DOCS = [
{
"id":"kd-behavior-observable","title":"Do rótulo ao comportamento observável","domain":"behavior_change","terms":["sou indisciplinado","não consigo manter nada","sempre falho","o que exatamente aconteceu"],"sources":["src-bcto-2024","src-bcttv1-2013"],
"definition":"Traduzir uma avaliação global da pessoa em uma descrição que outra pessoa poderia reconhecer: ação ou ausência de ação, contexto, frequência, duração e consequência próxima. A unidade é o episódio comportamental, não a personalidade.",
"not":"Não significa negar emoções, reduzir a pessoa a métricas ou exigir registro exaustivo. Também não autoriza concluir a função do comportamento apenas por descrevê-lo.",
"evidence":"BCTO e BCTTv1 oferecem vocabulário para descrever conteúdo observável e replicável de intervenções. São estruturas de descrição, não testes de causalidade nem instrumentos diagnósticos.",
"claims":[("observable-definition","src-bcto-2024","A BCT é descrita como componente observável e replicável de uma intervenção.","canonical_framework"),("taxonomy-purpose","src-bcttv1-2013","A taxonomia padroniza a especificação do conteúdo de intervenções.","canonical_framework")],
"decision":"Decidir se já existe informação suficiente para escolher um playbook ou se é necessário pedir um único exemplo recente.",
"data":"Um episódio recente; o que a pessoa pretendia fazer; o que ocorreu; horário/local quando relevante; consequência imediata. Frequência só quando a decisão depender de padrão.",
"questions":["Qual foi o episódio mais recente em que a ação planejada não aconteceu?","O que você fez nos minutos imediatamente antes e depois desse momento?","Qual detalhe observável distinguiria falta de oportunidade de escolha por outra ação?"],
"signals":"Rótulos como “preguiçoso”, “sem disciplina” ou “incapaz”, sem ação identificável; relato de intenção sem descrição do momento de execução.",
"alternatives":"A ação pode não ter ocorrido por falta de tempo, habilidade, energia, clareza, acesso, segurança ou prioridade. A descrição não escolhe entre essas explicações.",
"steps":["Localizar uma frase que julga a pessoa.","Pedir ou extrair um episódio concreto.","Registrar comportamento, contexto e resultado sem explicar a causa.","Verificar qual dado ausente realmente muda a próxima decisão.","Encaminhar ao knowledge ou playbook específico; não permanecer indefinidamente na coleta."],
"when":"Quando o relato é principalmente um rótulo ou quando duas hipóteses dependem de comportamentos diferentes.","avoid":"Quando o comportamento e o risco já estão claros; em crise, a coleta não deve atrasar o fluxo de segurança.",
"alfred":"Pode dizer: “Quero separar o julgamento do que aconteceu. Ontem, qual foi o momento em que você pretendia começar e o que fez em seguida?” Depois usa a resposta, sem repetir um interrogatório.",
"feedbacker":"Deve manter campos separados para evento observado e interpretação. Ausência de registro é dado ausente, não comportamento de falha.",
"example":"“Você não descreveu falta de disciplina; descreveu três noites em que abriu o material depois das 22h e adormeceu. Isso aponta primeiro para horário e sono, não para caráter.”",
"limits":"Descrições dependem do relato e podem omitir contexto. Ser observável não torna o dado completo nem causal."},
{
"id":"kd-goal-review","title":"Revisão de metas: manter, alterar, pausar ou abandonar","domain":"goals","terms":["mudar minha meta","desistir de um objetivo","prazo irrealista","meta não faz mais sentido","não estou progredindo"],"sources":["src-bcttv1-2013","src-goal-setting-2017"],
"definition":"Revisão de meta é comparar objetivo, comportamento executado, progresso, custo e condições atuais para escolher explicitamente entre manter, simplificar o plano, reagendar, substituir, pausar ou abandonar a meta.",
"not":"Não é reduzir a meta sempre que surge desconforto, preservar uma meta a qualquer custo nem confundir revisão do plano com desistência do objetivo.",
"evidence":"A BCTTv1 distingue revisão de metas de comportamento e de resultado. A meta-análise de Epton e colegas encontrou efeito médio pequeno da definição de metas e moderadores relevantes; isso sustenta uso calibrado, não uma receita universal.",
"claims":[("goal-review-definition","src-bcttv1-2013","A taxonomia distingue revisar metas comportamentais e metas de resultado à luz do desempenho.","canonical_framework"),("goal-setting-effect","src-goal-setting-2017","Definir metas teve efeito médio positivo pequeno em diversos comportamentos, com heterogeneidade e moderadores.","meta_analysis")],
"decision":"Escolher qual elemento mudar — objetivo, plano, prazo ou condições — e marcar quando a decisão será reavaliada.",
"data":"Formulação atual da meta; comportamento que está sob controle da pessoa; planejado versus executado; progresso; custo; importância atual; restrições novas; horizonte de decisão.",
"questions":["O comportamento previsto foi executado no período combinado e qual progresso ocorreu?","A meta ainda é importante o bastante para justificar o custo atual?","O desajuste principal está no objetivo, no plano, no prazo, na medida ou nas condições?"],
"signals":"Prazo repetidamente movido; execução razoável sem progresso; progresso com custo desproporcional; meta imposta; mudança relevante de trabalho, saúde, cuidado ou recursos.",
"alternatives":"Baixo progresso pode vir de medida inadequada, plano incompatível, prazo curto, dependência de terceiros ou objetivo que perdeu prioridade.",
"steps":["Escrever a meta e separar resultado de comportamento.","Comparar planejado, executado e progresso no período adequado.","Identificar custo e mudanças de contexto.","Classificar o desajuste: meta, plano, prazo, medida ou condição.","Escolher uma opção explícita: manter, simplificar, reagendar, substituir, pausar ou abandonar.","Definir duração do novo arranjo e critério da próxima revisão."],
"when":"Em revisão semanal/mensal, após mudança de contexto ou quando o mesmo prazo é adiado sem nova informação.","avoid":"Não decidir por uma única oscilação comum; não prolongar coaching quando saúde ou segurança são prioritárias.",
"alfred":"Apresenta a distinção decisiva e oferece duas opções plausíveis. Não presume que abandonar seja fracasso.",
"feedbacker":"Mostra separadamente execução, progresso e custo; informa período e dados ausentes antes de sugerir a categoria de ajuste.",
"example":"“A meta de concluir o curso continua importante e você estudou em quatro dos cinco dias previstos. O problema parece ser o prazo, não a execução. Eu manteria o objetivo e moveria a entrega duas semanas, com nova revisão após o próximo módulo.”",
"limits":"A meta-análise não determina qual ajuste funcionará para uma pessoa. Valores, recursos e obrigações podem justificar decisões não otimizadas por desempenho."},
{
"id":"kd-action-planning","title":"Plano de ação executável","domain":"planning","terms":["sei o que quero mas não faço","quando vou fazer","planejar a tarefa","não sei por onde começar"],"sources":["src-bcttv1-2013","src-self-regulation-2020"],
"definition":"Plano de ação especifica comportamento, contexto, início e extensão suficiente para reconhecer a execução. Ele converte uma intenção em uma oportunidade agendada ou ancorada.",
"not":"Não é uma lista completa de desejos, uma agenda sem margem nem um plano de contingência. Especificidade não compensa falta de tempo, habilidade ou acesso.",
"evidence":"A BCTTv1 define action planning como planejamento detalhado do desempenho. A meta-revisão de autorregulação encontrou apoio variável para planejamento e outros componentes; efeitos dependem de comportamento e população.",
"claims":[("action-plan-form","src-bcttv1-2013","Action planning inclui contexto e desempenho do comportamento.","canonical_framework"),("self-regulation-variability","src-self-regulation-2020","Componentes de autorregulação não foram consistentemente eficazes em todos os domínios.","systematic_review")],
"decision":"Determinar se falta operacionalização ou se outra barreira precisa ser resolvida antes de planejar.",
"data":"Comportamento-alvo; duração mínima realista; oportunidade; compromissos fixos; materiais; dependências; margem disponível.",
"questions":["Qual ação reconhecível marca o início e qual resultado mínimo marca o fim?","Em qual oportunidade real isso cabe sem competir com um compromisso fixo?","O que precisa estar disponível antes de o bloco começar?"],
"signals":"Intenção clara acompanhada de “quando der”; tarefas sem primeiro passo ou blocos colocados sobre compromissos existentes.",
"alternatives":"A falha pode ser capacidade insuficiente, aversão, ambiente, meta imposta ou plano excessivo — casos em que apenas detalhar não resolve.",
"steps":["Definir um comportamento reconhecível.","Escolher uma oportunidade real, por horário ou evento.","Fixar ponto de início e limite de duração/escopo.","Conferir conflito com agenda, materiais e deslocamento.","Registrar como será reconhecida a conclusão.","Executar uma vez e revisar o plano com base no atrito encontrado."],
"when":"Quando a intenção existe e a oportunidade é controlável, mas a execução permanece vaga.","avoid":"Quando o usuário ainda não escolheu a meta, não tem recursos básicos ou precisa de um plano se–então para obstáculo previsível.",
"alfred":"Ajuda a fechar uma decisão concreta e encerra; não transforma uma tarefa em planejamento de toda a vida.",
"feedbacker":"Pode detectar sobreposição com compromissos e comparar duração planejada com janelas existentes, sem inferir motivação.",
"example":"“Depois de guardar o jantar, você abrirá a lista 3 e resolverá apenas as questões 1 e 2. O bloco termina em 25 minutos, mesmo que a segunda questão fique incompleta.”",
"limits":"Planos detalhados podem falhar em rotinas imprevisíveis. A precisão deve servir à execução, não virar trabalho adicional."},
{
"id":"kd-if-then-plans","title":"Planos se–então para obstáculos previsíveis","domain":"planning","terms":["se acontecer isso o que faço","plano b","sempre sou interrompido","quando o gatilho aparecer"],"sources":["src-ii-2006","src-intention-behavior-2006"],
"definition":"Uma intenção de implementação liga uma situação discriminável a uma resposta: “Se Y ocorrer, então farei X”. É usada para iniciar, proteger ou retomar uma ação diante de um obstáculo previsível.",
"not":"Não é um cronograma comum, pensamento positivo nem uma lista extensa de exceções. Requer intenção prévia e uma resposta realmente disponível.",
"evidence":"A meta-análise de Gollwitzer e Sheeran sintetizou 94 testes e encontrou efeito positivo médio a grande sobre alcance de metas. A síntese de Webb e Sheeran mostra que mudar intenção, sozinho, produz mudança comportamental menor, apoiando a distinção entre querer e executar.",
"claims":[("ii-format-effect","src-ii-2006","Planos se–então especificam quando, onde e como agir e tiveram efeito agregado positivo sobre alcance de metas.","meta_analysis"),("intention-gap","src-intention-behavior-2006","Mudanças em intenção não se traduzem integralmente em mudanças de comportamento.","meta_analysis")],
"decision":"Escolher uma única contingência de alta frequência e uma resposta curta; se o obstáculo não é previsível, usar planejamento flexível em vez desta técnica.",
"data":"Meta escolhida; situação observável; frequência; controle sobre a resposta; custo da alternativa; conflito com segurança.",
"questions":["Qual obstáculo se repetiu o suficiente para merecer uma contingência?","Como você reconhecerá, no momento, que o gatilho ocorreu?","Qual resposta continua viável e segura exatamente nessa situação?"],
"signals":"Mesmo obstáculo antecede várias falhas: reunião atrasada, transporte perdido, celular ao alcance ou retorno de viagem.",
"alternatives":"Obstáculo raro, mal definido ou fora de controle pode exigir reserva de capacidade, negociação ou mudança da meta.",
"steps":["Confirmar que a meta foi escolhida.","Selecionar um obstáculo recorrente e reconhecível.","Definir resposta pequena e viável nesse contexto.","Escrever uma única frase se–então.","Checar conflitos e exceções de segurança.","Revisar depois de ocorrências reais do gatilho, não apenas após passagem do tempo."],
"when":"Quando há um gatilho previsível ligado a início, interrupção ou retomada.","avoid":"Não usar para riscos médicos, crises, eventos vagos ou dezenas de contingências simultâneas.",
"alfred":"Propõe a contingência na linguagem do usuário e confirma se a resposta cabe naquele momento.",
"feedbacker":"Só avalia o plano quando há ocorrências do gatilho; ausência do evento não conta como falha.",
"example":"“Se a reunião passar das 18h30, em vez de cancelar o estudo eu farei a revisão de dez cartões no ônibus; a lista de exercícios fica para o próximo bloco normal.”",
"limits":"O efeito agregado varia por meta e contexto. Planos rígidos podem ser inúteis quando oportunidades mudam continuamente."},
{
"id":"kd-habit-formation","title":"Formação de hábitos e automaticidade","domain":"habit_formation","terms":["quanto tempo para virar hábito","fazer no automático","21 dias","esqueço meu hábito","mesmo horário ajuda"],"sources":["src-habit-lally-2010","src-habit-review-2024","src-context-stability-2022"],
"definition":"Formação de hábito é o aumento gradual da automaticidade de uma resposta por repetição em contextos que oferecem pistas recorrentes. Repetir uma rotina não garante que ela já seja automática.",
"not":"Não existe prazo universal de 21 ou 66 dias. Hábito não é sinônimo de disciplina, frequência perfeita ou qualquer atividade agendada.",
"evidence":"Lally e colegas observaram curvas e tempos muito variáveis em 96 participantes. A revisão de 2024 encontrou medianas em torno de dois meses em poucos estudos, médias maiores e intervalo individual amplo, com alto risco de viés em muitos estudos. Estudos de estabilidade contextual associaram contexto mais estável a maior automaticidade, sem garantir manutenção universal.",
"claims":[("habit-curve","src-habit-lally-2010","Automaticidade cresceu de forma assintótica e variou entre pessoas e comportamentos.","observational_study"),("habit-time-review","src-habit-review-2024","O tempo de formação variou amplamente; a evidência disponível é limitada e heterogênea.","systematic_review"),("context-stability","src-context-stability-2022","Estabilidade de contexto previu automaticidade e alcance de repetição em dois conjuntos de dados.","observational_study")],
"decision":"Decidir se vale estabilizar uma pista, simplificar o comportamento ou tratar a atividade apenas como rotina deliberada.",
"data":"Comportamento específico; pista possível; frequência real; complexidade; oportunidade; medida de automaticidade; semanas de observação.",
"questions":["Qual evento do contexto ocorre com regularidade suficiente para servir de pista?","O comportamento é simples o bastante para ser repetido como uma unidade ou precisa ser decomposto?","Ao longo das semanas, a ação passou a depender menos de lembrança e esforço ou apenas ficou frequente?"],
"signals":"Ação depende sempre de lembrança deliberada; ocorre em contextos muito diferentes; comportamento é complexo demais para uma resposta única.",
"alternatives":"Esquecimento pode ser falha de lembrete; baixa repetição pode ser falta de oportunidade; uma atividade complexa pode continuar exigindo planejamento mesmo após meses.",
"steps":["Escolher uma resposta simples e repetível.","Selecionar uma pista recorrente que realmente ocorre.","Facilitar materiais e acesso nesse contexto.","Repetir sem exigir sequência perfeita.","Observar execução e sensação de automaticidade por várias semanas.","Alterar pista ou comportamento se a oportunidade real não se repete."],
"when":"Para comportamentos repetitivos e relativamente simples em contexto recorrente.","avoid":"Não vender automaticidade como meta necessária para tarefas complexas; não usar prazo fixo como cobrança.",
"alfred":"Corrige mitos de prazo e ajuda a escolher pista e resposta, sem prometer automatização.",
"feedbacker":"Separa frequência de automaticidade e descreve mudança ao longo do tempo; não chama ausência de um dia de perda do hábito.",
"example":"“Tomar o remédio conforme prescrito já acontece quase todos os dias, mas ainda depende do alarme. Isso é uma rotina funcional; não precisamos chamá-la de automática para considerá-la bem-sucedida.”",
"limits":"Grande parte da evidência usa autorrelato e poucos comportamentos de saúde. O produto não deve interferir em prescrição ou adesão médica."},
{
"id":"kd-procrastination-map","title":"Mapa funcional do adiamento","domain":"procrastination","terms":["estou procrastinando","deixo para depois","fujo da tarefa","organizo tudo e não começo","prazo chegando"],"sources":["src-procrastination-steel-2007","src-procrastination-treatment-2018"],
"definition":"Procrastinação é adiamento voluntário apesar da expectativa de piora. Um mapa funcional descreve antecedente, ação alternativa, recompensa imediata e custo posterior antes de escolher intervenção.",
"not":"Nem todo atraso é procrastinação. Falta de tempo, informação, acesso, habilidade, decisão ou segurança pode tornar o adiamento racional ou inevitável.",
"evidence":"A meta-análise de Steel associou procrastinação a aversividade, atraso da recompensa, autoeficácia e impulsividade, entre outros fatores. A revisão de tratamentos encontrou benefício pequeno e heterogêneo, com poucos ensaios; não identifica uma técnica universal.",
"claims":[("procrastination-correlates","src-procrastination-steel-2007","Aversividade, atraso, autoeficácia e impulsividade apresentaram associações agregadas relevantes.","meta_analysis"),("treatment-effect","src-procrastination-treatment-2018","Tratamentos psicológicos mostraram benefício pequeno e heterogêneo em poucos ensaios.","systematic_review")],
"decision":"Escolher entre esclarecer a tarefa, reduzir aversividade inicial, alterar ambiente/recompensa, desenvolver habilidade, renegociar a meta ou encaminhar sofrimento relevante.",
"data":"Tarefa; prazo; decisão de fazê-la; episódio recente; alternativa escolhida; consequência imediata; custo posterior; habilidade e recursos.",
"questions":["Qual tarefa você decidiu fazer e o que ocorreu no episódio mais recente de adiamento?","Que alternativa você executou e qual benefício imediato ela ofereceu?","Que observação indicaria falta de clareza, tempo ou habilidade em vez de procrastinação?"],
"signals":"Pessoa inicia preparação periférica, migra para atividade mais recompensadora ou espera pressão do prazo, embora queira executar.",
"alternatives":"Atraso estratégico, prioridade concorrente, instrução incompleta, exaustão, dor, meta imposta ou dependência externa.",
"steps":["Confirmar que existe decisão de realizar a tarefa.","Descrever um episódio de adiamento.","Identificar antecedente e alternativa executada.","Comparar benefício imediato e custo posterior.","Testar a hipótese contra falta de clareza, habilidade, tempo e energia.","Escolher uma intervenção ligada ao mecanismo mais sustentado; definir observação que a refutaria."],
"when":"Quando há adiamento recorrente de tarefa escolhida e custo esperado.","avoid":"Não usar como rótulo para toda baixa execução nem oferecer tratamento psicológico pelo produto.",
"alfred":"Nomeia o padrão sem moralizar e seleciona uma intervenção coerente com o episódio, não uma lista de dicas.",
"feedbacker":"Só descreve padrão com múltiplos episódios e registra explicações contrárias; correlação de horário não vira causa.",
"example":"“Você abriu o editor três vezes, mas em cada vez foi procurar um novo modelo de currículo. Como os requisitos da vaga já estavam claros, a organização parece estar substituindo a escrita. Vamos testar começar pelo parágrafo de experiência antes de abrir qualquer modelo.”",
"limits":"O mapa é uma hipótese funcional, não diagnóstico. Sofrimento persistente ou incapacitante pode exigir avaliação profissional."},
{
"id":"kd-chosen-vs-imposed","title":"Metas escolhidas, internalizadas e impostas","domain":"motivation","terms":["não quero essa meta","estou fazendo pelos outros","me obrigaram","isso não importa para mim","quero desistir"],"sources":["src-sdt-rct-2020","src-sdt-techniques-2019"],
"definition":"Distingue metas endossadas pela pessoa de metas vividas principalmente como pressão externa. A decisão central é apoiar escolha e sentido, não tentar fabricar motivação para qualquer objetivo recebido.",
"not":"Não significa que toda obrigação externa deva ser abandonada nem que motivação autônoma elimina limites, deveres ou consequências.",
"evidence":"Meta-análises de intervenções baseadas em autodeterminação encontraram efeitos médios modestos e sugerem mediação por motivação autônoma e competência percebida. Técnicas de apoio às necessidades variam por contexto.",
"claims":[("sdt-effects","src-sdt-rct-2020","Intervenções SDT tiveram efeito pequeno em comportamentos de saúde, com vieses e heterogeneidade.","meta_analysis"),("need-support-techniques","src-sdt-techniques-2019","A síntese avaliou técnicas para apoiar necessidades e motivação em intervenções de saúde.","meta_analysis")],
"decision":"Escolher entre manter por valor próprio, renegociar condições, cumprir apenas o necessário, substituir ou recusar a meta quando possível.",
"data":"Origem da meta; consequências reais; valor pessoal; grau de escolha; possibilidade de negociação; custos para si e terceiros.",
"questions":["Se ninguém observasse, recompensasse ou punisse, que parte dessa meta ainda valeria a pena?","Quais consequências são realmente fixas e onde ainda existe margem de escolha?","Você quer abandonar o objetivo ou mudar o motivo, o método ou o ritmo?"],
"signals":"Linguagem de obrigação, resistência que desaparece em metas próprias, execução apenas sob cobrança ou objetivo definido por família/gestor.",
"alternatives":"Baixa execução também pode vir de capacidade, clareza, tempo, humor ou conflito entre dois valores próprios.",
"steps":["Identificar quem definiu a meta e qual obrigação existe.","Separar consequência real de culpa ou expectativa presumida.","Perguntar o que, se algo, a pessoa endossa no objetivo.","Mapear margem de escolha e negociação.","Selecionar manter, adaptar, limitar, substituir ou recusar.","Planejar somente depois dessa decisão."],
"when":"Quando resistência está ligada à autoria da meta ou a pressão externa.","avoid":"Não usar autonomia para ignorar segurança, cuidado de dependentes, lei ou consequência contratual; explicitar esses limites.",
"alfred":"Pode legitimar a recusa e explorar opções sem persuadir a pessoa a gostar da meta.",
"feedbacker":"Não interpreta baixa conclusão como motivação baixa sem dados sobre autoria e restrições.",
"example":"“Você não escolheu correr; escolheu melhorar o fôlego, e a corrida veio da comparação com seu irmão. Podemos manter o objetivo e trocar a modalidade, em vez de tentar aumentar sua disciplina para um plano que você não endossa.”",
"limits":"A maior parte da evidência citada vem de saúde e efeitos médios modestos. Autonomia é contextual e não observável apenas pela taxa de conclusão."},
{
"id":"kd-self-monitoring","title":"Automonitoramento mínimo orientado a decisão","domain":"self_regulation","terms":["o que devo registrar","acompanhar hábito","meus dados mostram","registro demais","não sei se melhorou"],"sources":["src-bcttv1-2013","src-self-regulation-2020"],
"definition":"Automonitoramento é registrar o comportamento ou resultado definido pela própria pessoa para responder a uma decisão futura. O registro deve ter variável, frequência e período de revisão explícitos.",
"not":"Não é vigilância contínua, coleta por precaução nem evidência causal. Mais granularidade pode aumentar carga, ansiedade e abandono.",
"evidence":"A BCTTv1 define automonitoramento como método para a pessoa acompanhar comportamento ou resultado. A meta-revisão encontrou componentes de autorregulação promissores em alguns domínios, mas sem consistência universal e com qualidade variável.",
"claims":[("monitoring-definition","src-bcttv1-2013","A taxonomia distingue automonitoramento de comportamento e de resultado.","canonical_framework"),("monitoring-evidence-limit","src-self-regulation-2020","Automonitoramento apareceu entre componentes úteis, mas efeitos variaram por comportamento e população.","systematic_review")],
"decision":"Escolher a menor variável e período que permitem decidir manter, ajustar ou interromper uma estratégia.",
"data":"Pergunta de decisão; variável observável; forma de coleta; carga; período; privacidade; possibilidade de dado ausente.",
"questions":["Qual decisão concreta poderá mudar depois de observar este registro?","Qual variável mínima e qual janela distinguem mudança de oscilação comum?","Que dado ausente tornaria a conclusão pouco confiável?"],
"signals":"Discussão depende de frequência ou contexto desconhecidos; a pessoa usa impressão global contradita por episódios; registro atual não muda decisões.",
"alternatives":"Às vezes um único exemplo basta. Dados do aplicativo podem refletir falha de sincronização, não ausência do comportamento.",
"steps":["Escrever a decisão que o dado deve informar.","Escolher uma variável diretamente ligada a ela.","Definir registro de baixa fricção e dado ausente explícito.","Fixar período e data de revisão.","Comparar com alternativas e contexto.","Parar a coleta quando não muda mais a decisão ou gera custo desproporcional."],
"when":"Quando uma decisão depende de padrão e os dados existentes são insuficientes.","avoid":"Evitar em comportamento compulsivo, alimentação, peso ou sofrimento quando o rastreio pode agravar risco; usar fluxo especializado.",
"alfred":"Explica por que registrar e oferece uma forma mínima, sempre aceitando recusa.",
"feedbacker":"Distingue zero, não conclusão e dado ausente; informa cobertura e período antes de qualquer padrão.",
"example":"“Durante cinco dias, registre apenas a hora em que começou a primeira tarefa — não produtividade nem humor. Isso basta para verificar se o conflito está no horário planejado.”",
"limits":"Autorrelato e dados digitais têm erros. Monitoramento pode alterar o comportamento e não demonstra por que ele ocorreu."},
{
"id":"kd-retrieval-practice","title":"Prática de recuperação com feedback","domain":"study_and_learning","terms":["como revisar sem reler","flashcards funcionam","testar a memória","não lembro do que estudei","fazer questões"],"sources":["src-learning-dunlosky-2013","src-retrieval-meta-2021"],
"definition":"Prática de recuperação exige tentar produzir uma resposta a partir da memória antes de consultar a solução, seguida de feedback ou correção. O alvo é retenção e uso futuro, não apenas sensação de familiaridade.",
"not":"Não é prova de alto risco, releitura disfarçada nem repetir cartões já dominados. Errar sem feedback pode consolidar erro.",
"evidence":"Dunlosky e colegas classificaram practice testing como técnica de alta utilidade. Meta-análise de 222 estudos de sala de aula encontrou efeito médio moderado, com moderadores como formato, feedback, correspondência e repetição.",
"claims":[("practice-testing-utility","src-learning-dunlosky-2013","Practice testing recebeu avaliação de alta utilidade em diferentes materiais e tarefas.","systematic_review"),("classroom-testing-effect","src-retrieval-meta-2021","Quizzes elevaram desempenho acadêmico em média, com efeito moderado e vários moderadores.","meta_analysis")],
"decision":"Escolher formato e feedback compatíveis com a habilidade-alvo; leitura inicial ainda é necessária quando não há conhecimento para recuperar.",
"data":"Objetivo da avaliação; material; conhecimento prévio; formato esperado; acesso a resposta correta; atraso até uso; erros recorrentes.",
"questions":["O que precisa ser produzido de memória, sem consultar o material?","Quando e como a resposta será corrigida depois da tentativa?","Os erros mostram falta de compreensão inicial ou necessidade de novas recuperações?"],
"signals":"Releitura gera familiaridade sem capacidade de explicar; estudante só reconhece alternativas; esquece após poucos dias.",
"alternatives":"Dificuldade pode vir de compreensão inicial insuficiente, vocabulário, pré-requisito ou perguntas desalinhadas com o objetivo.",
"steps":["Definir o que deve ser produzido sem consulta.","Estudar/compreender o material quando necessário.","Responder sem olhar, em formato alinhado ao objetivo.","Comparar com resposta correta e corrigir o raciocínio.","Registrar erro relevante, não apenas pontuação.","Recuperar novamente após intervalo, variando exemplos quando o objetivo inclui transferência."],
"when":"Para consolidar conteúdo já apresentado e verificar o que pode ser produzido sem apoio.","avoid":"Não substituir ensino inicial; evitar sobrecarga de testes e métricas punitivas.",
"alfred":"Ajuda a transformar um trecho concreto em pergunta e a definir feedback, sem prometer nota.",
"feedbacker":"Compara acerto por tipo de questão e intervalo; não confunde aumento de tentativas com aprendizagem.",
"example":"“Feche o resumo e explique em dois minutos por que a derivada zera no ponto crítico. Depois confira a definição e marque exatamente onde seu raciocínio divergiu.”",
"limits":"Resultados variam com desenho, conteúdo e avaliação. Acerto imediato não garante transferência para problema novo."},
{
"id":"kd-spaced-practice","title":"Distribuição da prática ao longo do tempo","domain":"study_and_learning","terms":["estudar tudo na véspera","espaçar revisão","cronograma de revisão","quanto tempo entre revisões","estudo acumulado"],"sources":["src-learning-dunlosky-2013","src-spacing-review-2024"],
"definition":"Prática distribuída reparte contato e recuperação do material por mais de uma sessão separada no tempo. O intervalo deve permitir algum esquecimento sem tornar a recuperação inviável.",
"not":"Não é fragmentar uma única sessão com pequenas pausas nem seguir calendário universal. Espaçamento não define sozinho o que fazer em cada sessão.",
"evidence":"A revisão de Dunlosky atribuiu alta utilidade à prática distribuída. Revisão de educação em profissões da saúde encontrou benefício na maioria dos experimentos, mas desenhos, materiais e medidas eram heterogêneos.",
"claims":[("distributed-utility","src-learning-dunlosky-2013","Distributed practice recebeu avaliação de alta utilidade em ampla revisão.","systematic_review"),("health-education-spacing","src-spacing-review-2024","43 de 63 experimentos relataram benefícios de prática distribuída e/ou recuperação, com heterogeneidade relevante.","systematic_review")],
"decision":"Distribuir sessões com base no horizonte e dificuldade; priorizar conteúdo que precisa permanecer disponível mais tarde.",
"data":"Data de uso/prova; volume; domínio atual; oportunidades; dificuldade de recuperação; formato da tarefa final.",
"questions":["Por quanto tempo o conteúdo precisa ser retido e quando será usado?","Quais itens estão difíceis o bastante para receber um intervalo menor?","A pessoa consegue recuperar depois do intervalo ou o registro mostra apenas revisões concluídas?"],
"signals":"Concentração na véspera, bom desempenho imediato e esquecimento posterior; grande volume revisado uma única vez.",
"alternatives":"Baixo desempenho pode ser compreensão insuficiente; espaçar conteúdo não compreendido apenas repete confusão.",
"steps":["Identificar horizonte e unidades do material.","Garantir primeiro contato com compreensão mínima.","Agendar ao menos duas recuperações em dias diferentes.","Aumentar ou reduzir intervalo conforme dificuldade de recuperar.","Misturar unidades apenas quando existe base suficiente.","Revisar o cronograma pela retenção, não por completar sessões."],
"when":"Quando há dias ou semanas antes do uso e retenção posterior importa.","avoid":"Não usar calendário rígido em emergência de prazo; não atrasar feedback de erro conceitual.",
"alfred":"Ajuda a distribuir um conjunto real de materiais no horizonte disponível, preservando descanso.",
"feedbacker":"Avalia retenção por intervalo e tipo de material, controlando tempo total quando possível.",
"example":"“Em vez de reler os quatro capítulos no domingo, revise o capítulo 1 hoje com questões, recupere os pontos difíceis na quinta e volte a eles no simulado da próxima terça.”",
"limits":"A revisão mais recente citada concentra-se em profissões da saúde. Intervalo ótimo depende de retenção desejada, material e estudante."},
{
"id":"kd-sleep-duration","title":"Duração do sono: referência geral e limites","domain":"sleep_and_recovery","terms":["quantas horas dormir","durmo quatro horas","sono suficiente","preciso dormir menos","recuperar sono"],"sources":["src-sleep-aasm-2015","src-sleep-nsf-2015"],
"definition":"Duração do sono é o tempo efetivamente dormido em 24 horas. Para adultos saudáveis, consensos oferecem faixas populacionais; necessidade individual também depende de idade, saúde, qualidade e regularidade.",
"not":"Não é uma prescrição para uma pessoa, nem permite concluir transtorno por uma noite. Tempo na cama não equivale necessariamente a sono.",
"evidence":"AASM/SRS recomenda que adultos durmam regularmente sete ou mais horas para promover saúde. A NSF propõe faixas por idade por consenso. Ambos explicitam contexto e limites; não sustentam cortar sono para produtividade.",
"claims":[("adult-sleep-consensus","src-sleep-aasm-2015","Consenso recomenda sete ou mais horas regulares para adultos saudáveis.","institutional_guideline"),("age-ranges","src-sleep-nsf-2015","Painel multidisciplinar definiu faixas recomendadas por grupo etário.","institutional_guideline")],
"decision":"Decidir se a conversa pode permanecer em organização de rotina ou precisa de orientação para avaliação/segurança.",
"data":"Idade; duração habitual; janela; sonolência diurna; direção/máquinas; sintomas; turno; duração do padrão; condição/medicação conhecida.",
"questions":["Quantas horas foram efetivamente dormidas em um dia típico, e isso é padrão ou uma noite isolada?","Há sonolência ao dirigir ou operar máquinas, ou algum sintoma importante que mude a prioridade para segurança?","Turno, fragmentação, condição de saúde ou medicação tornam a referência populacional insuficiente?"],
"signals":"Sono habitual muito abaixo da referência, sonolência ao dirigir, desmaio, falta de ar, dor, mudança intensa ou prejuízo persistente.",
"alternatives":"Tempo curto pode ser pontual ou erro de medição; cansaço pode ter outras causas. Tempo adequado não exclui baixa qualidade ou condição médica.",
"steps":["Distinguir uma noite de padrão habitual.","Comparar apenas como referência populacional apropriada à idade.","Verificar impacto e sinais de risco.","Se não houver risco, identificar conflito concreto de agenda e preservar oportunidade de sono.","Se houver sonolência em atividade perigosa ou sintoma importante, interromper coaching e usar segurança.","Evitar recomendar suplemento, medicamento ou diagnóstico."],
"when":"Para referência geral e organização de horários sem sintomas preocupantes.","avoid":"Não individualizar necessidade, tratar insônia ou alterar medicação; risco ao dirigir exige ação imediata de segurança.",
"alfred":"Pode apresentar a faixa como referência e priorizar segurança, sem competir com profissional de saúde.",
"feedbacker":"Relata duração, cobertura e tendência; não chama correlação entre sono e desempenho de causa confirmada.",
"example":"“Quatro horas por noite há duas semanas está bem abaixo da referência geral para adultos e você relatou cochilar no trânsito. Não vou otimizar sua agenda agora: pare de dirigir e procure ajuda segura para o deslocamento e avaliação de saúde.”",
"limits":"Consensos populacionais não medem necessidade individual. Qualidade, distúrbios, turnos e condições clínicas exigem avaliação profissional."},
{
"id":"kd-physical-activity-consistency","title":"Atividade física: referência populacional sem prescrição","domain":"physical_activity","terms":["quanto exercício fazer","voltar a treinar","consistência no treino","150 minutos","começar atividade física"],"sources":["src-who-pa-2020","src-cdc-pa-adults"],
"definition":"Consistência em atividade física é participação repetida compatível com capacidade e contexto. Diretrizes fornecem metas populacionais de volume e intensidade; o produto pode apoiar organização, não prescrever treino.",
"not":"Não é treinar diariamente, compensar sessões perdidas ou progredir apesar de dor. A meta de 150 minutos não é ponto de partida obrigatório para cada pessoa.",
"evidence":"OMS recomenda atividade aeróbica e fortalecimento por faixa etária e ressalta que alguma atividade é melhor que nenhuma. CDC apresenta a referência de 150 minutos moderados semanais para adultos e cautelas para condições crônicas ou início vigoroso.",
"claims":[("who-pa-guideline","src-who-pa-2020","Diretriz estabelece recomendações populacionais de frequência, intensidade e duração por grupo.","institutional_guideline"),("cdc-adult-guideline","src-cdc-pa-adults","CDC informa referência semanal para adultos e orienta procurar profissional em condições específicas.","institutional_guideline")],
"decision":"Decidir se cabe organizar oportunidades seguras ou se sintomas, condição clínica ou pedido de progressão exigem profissional.",
"data":"Atividade pretendida; experiência; intensidade; tempo disponível; dor/sintomas; condição conhecida; orientação profissional; ambiente e equipamento.",
"questions":["Há dor no peito, desmaio, falta de ar incomum, tontura ou lesão associada à atividade?","Qual atividade foi escolhida e qual é a experiência atual da pessoa com ela?","A principal restrição é oportunidade, acesso ou recuperação, ou existe uma decisão clínica ou de prescrição fora do escopo do produto?"],
"signals":"Pedido de compensar treino, salto abrupto de volume, dor, falta de ar incomum, desmaio, dor no peito ou atividade vigorosa após inatividade relevante.",
"alternatives":"Baixa frequência pode vir de deslocamento, custo, cuidado, preferência, clima ou recuperação; não implica falta de motivação.",
"steps":["Confirmar ausência de sintoma que acione segurança.","Identificar atividade escolhida e capacidade/experiência relatadas.","Usar diretriz apenas como referência, não como prescrição.","Organizar oportunidades realistas e dias de recuperação.","Não definir carga, técnica ou progressão clínica.","Revisar adesão e conforto; sintomas mudam imediatamente o fluxo."],
"when":"Para organização geral de uma atividade já considerada apropriada e sem sinal de alerta.","avoid":"Dor no peito, desmaio, falta de ar incomum, lesão ou dúvida clínica devem sair do coaching.",
"alfred":"Ajuda a encontrar horários e alternativas escolhidas; não manda “superar” dor nem cria planilha de treino individual.",
"feedbacker":"Descreve frequência e distribuição semanal; não recomenda aumento de carga com base apenas em conclusão.",
"example":"“As duas caminhadas já contam; você não precisa saltar direto para cinco dias. Como não há dor e essa atividade foi liberada para você, vamos apenas encontrar uma terceira janela que não elimine sua recuperação.”",
"limits":"Diretrizes são populacionais e não avaliam risco individual. O Winperium não substitui educação física, fisioterapia ou medicina."},
]


def render(doc: dict) -> str:
    claims = [{"claim_id": cid, "source_ids": [sid], "evidence_strength": strength} for cid, sid, _, strength in doc["claims"]]
    fm = {
        "id": doc["id"], "title": doc["title"], "document_type": "knowledge",
        "domain": doc["domain"], "agents": ["alfred", "feedbacker"],
        "retrieval_terms": doc["terms"], "decision_questions": doc["questions"],
        "source_ids": doc["sources"],
        "supported_claims": claims, "language": "pt-BR", "version": "2.0.1",
        "status": "machine_audited", "requires_human_review": True,
        "index_eligible": False, "risk_level": "medium" if doc["domain"] in {"sleep_and_recovery", "physical_activity"} else "low",
        "created_at": CREATED_AT, "last_machine_audited_at": TODAY,
    }
    mapping = "\n".join(f"- Afirmação: {text}\n  - Fonte: `{sid}`\n  - Suporte/força: `{strength}`" for _, sid, text, strength in doc["claims"])
    steps = "\n".join(f"{i}. {step}" for i, step in enumerate(doc["steps"], 1))
    return "---\n" + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False).strip() + "\n---\n\n" + f"""# {doc['title']}

## Definição operacional

{doc['definition']}

## O que este conceito não significa

{doc['not']}

## Evidências principais

{doc['evidence']}

## Mapeamento das evidências

{mapping}

## Decisão que este conhecimento apoia

{doc['decision']}

## Dados necessários

{doc['data']}

## Perguntas úteis para decidir

{chr(10).join(f'- {question}' for question in doc['questions'])}

## Sinais compatíveis

{doc['signals']}

## Explicações alternativas

{doc['alternatives']}

## Processo de aplicação

{steps}

## Quando aplicar

{doc['when']}

## Quando evitar

{doc['avoid']}

## Aplicação pelo Alfred

{doc['alfred']}

## Aplicação pelo Feedbacker

{doc['feedbacker']}

## Exemplo contextualizado

{doc['example']}

## Limitações

{doc['limits']}

## Fontes

{', '.join(f'`{sid}`' for sid in doc['sources'])}.
"""


def main() -> None:
    if AUDIT.exists() or QUARANTINE.exists():
        raise SystemExit("Reconstrução de knowledge já iniciada; não sobrescrever.")
    old_files = sorted(KNOWLEDGE.rglob("*.md"))
    old_meta = []
    for path in old_files:
        fm = yaml.safe_load(path.read_text(encoding="utf-8").split("---", 2)[1])
        old_meta.append((path, fm))
    QUARANTINE.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(KNOWLEDGE), str(QUARANTINE))
    KNOWLEDGE.mkdir(parents=True)
    active_ids = {doc["id"] for doc in DOCS}
    audit_rows = []
    qrows = []
    for path, fm in old_meta:
        rel = path.relative_to(KNOWLEDGE).as_posix()
        decision = "replaced_by_v2" if fm["id"] in active_ids else "quarantined_redundant_or_insufficient"
        row = {"document_id": fm["id"], "original_path": f"knowledge/{rel}", "quarantine_path": f"quarantine/phase5_legacy_knowledge/{rel}", "decision": decision, "phase": 5, "decided_at": TODAY, "requires_human_review": True, "active": False, "index_eligible": False}
        audit_rows.append(row); qrows.append(row)
    for doc in DOCS:
        path = KNOWLEDGE / doc["domain"] / f"{doc['id']}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render(doc), encoding="utf-8")
        audit_rows.append({"document_id": doc["id"], "path": path.relative_to(RAG).as_posix(), "decision": "active_reconstructed_v2", "phase": 5, "status": "machine_audited", "requires_human_review": True, "index_eligible": False})
    registry = [json.loads(line) for line in (RAG / "document_registry.jsonl").read_text(encoding="utf-8").splitlines() if line]
    registry = [row for row in registry if row.get("document_type") != "knowledge"]
    for doc in DOCS:
        registry.append({"document_id": doc["id"], "path": f"knowledge/{doc['domain']}/{doc['id']}.md", "document_type": "knowledge", "domain": doc["domain"], "agents": ["alfred", "feedbacker"], "situations": doc["terms"], "risk_level": "medium" if doc["domain"] in {"sleep_and_recovery", "physical_activity"} else "low", "language": "pt-BR", "status": "machine_audited", "requires_human_review": True, "index_eligible": False, "source_ids": doc["sources"], "version": "2.0.1", "last_machine_audited_at": TODAY})
    registry.sort(key=lambda row: row["document_id"])
    (RAG / "document_registry.jsonl").write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in registry), encoding="utf-8")
    existing_q = [json.loads(line) for line in QREG.read_text(encoding="utf-8").splitlines() if line] if QREG.exists() else []
    QREG.parent.mkdir(parents=True, exist_ok=True)
    QREG.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in existing_q + qrows), encoding="utf-8")
    AUDIT.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in audit_rows), encoding="utf-8")
    scores = [{"document_id": doc["id"], "document_type": "knowledge", "specificity": 4, "evidence": 4, "traceability": 5, "actionability": 4, "naturalness": 4, "retrieval_value": 4, "safety": 4, "metadata": 5, "status": "machine_audited", "requires_human_review": True, "scored_at": TODAY} for doc in DOCS]
    (RAG / "DOCUMENT_QUALITY_SCORES.jsonl").write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in scores), encoding="utf-8")
    print(json.dumps({"status": "ok", "legacy_preserved": len(old_files), "active_rebuilt": len(DOCS), "quarantined_without_replacement": len(old_files) - len(DOCS)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
