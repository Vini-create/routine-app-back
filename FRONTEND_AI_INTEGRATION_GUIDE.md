# Winperium — Contrato de integração do frontend com Alfred

**Atualizado em:** 27 de julho de 2026
**Backend:** FastAPI + LangGraph  
**Prefixo público:** `/api/v1/ai`  
**Objetivo:** orientar a migração completa do frontend para o novo fluxo
unificado de IA.

## Instrução para o Codex do frontend

Use este arquivo como fonte de verdade para adaptar o frontend. Antes de editar:

1. inventarie os endpoints, tipos e componentes antigos de IA;
2. remova chamadas públicas diretas para Alfred antigo ou Feedbacker;
3. preserve autenticação e padrões visuais já existentes;
4. implemente os contratos TypeScript descritos aqui;
5. implemente primeiro `/invoke`; depois streaming, conversas, usage e HITL;
6. acrescente testes para cada estado descrito nos critérios de aceite;
7. não invente campos ou endpoints que não estejam neste documento.

O arquivo `graph_overview.md` explica a arquitetura interna. O frontend não
deve reproduzir o grafo nem escolher nodes internos.

---

# 1. Mudança conceitual

Existe um único produto público chamado **Alfred**.

O frontend envia:

- mensagem;
- conversa atual, quando existir;
- pista opcional de habilidade;
- contexto visual pequeno e não autoritativo;
- chave de idempotência.

O backend decide internamente entre:

```text
safe_response
deterministic
alfred
feedbacker
rag_then_alfred
rag_then_feedbacker
```

Esses valores podem ser recebidos em `response.route` para observabilidade e
apresentação, mas nunca devem ser usados pelo frontend para forçar o caminho.

Não existe endpoint público `/feedbacker`.

---

# 2. Autenticação e pré-condições

Todas as 11 rotas de IA exigem:

```http
Authorization: Bearer <access_token>
Accept: application/json
```

Requisições com body também exigem:

```http
Content-Type: application/json
```

Antes de executar uma rota, o backend valida:

- token válido;
- usuário ativo e não excluído;
- e-mail verificado;
- conta de billing existente;
- plano ativo ou em trial;
- entitlement da funcionalidade.

O frontend deve reutilizar o cliente HTTP autenticado atual e seu mecanismo de
refresh token. Não salve tokens dentro do estado específico do Alfred.

## Comportamento sugerido

| Situação | Ação do frontend |
|---|---|
| `401` | tentar refresh uma vez; se falhar, encerrar sessão |
| `403` com `Email not verified` | abrir fluxo de verificação |
| `403` com `plan_unavailable` | informar indisponibilidade do plano |
| `403` de ownership | não revelar existência de dados de outro usuário |

---

# 3. Rate limits e quotas

Rate limit HTTP:

| Classe | Limite |
|---|---:|
| `/invoke` e `/stream` | 12/minuto por IP |
| Leituras | 60/minuto por IP |
| Mutações | 20/minuto por IP |

Plano Free:

| Recurso | Limite |
|---|---:|
| Requisições padrão | 30/dia |
| Requisições com RAG | 15/dia |
| Análises profundas | 3/semana |
| Ritmo de execuções | 6/minuto por usuário |
| Streams simultâneos | 1 |

Não codifique esses números diretamente em componentes. Use
`GET /api/v1/ai/usage` para renderizar o estado real do usuário.

---

# 4. Inventário das rotas

| Método | Endpoint | Responsabilidade |
|---|---|---|
| `POST` | `/api/v1/ai/invoke` | executar Alfred sem streaming |
| `POST` | `/api/v1/ai/stream` | executar Alfred via SSE |
| `GET` | `/api/v1/ai/usage` | consultar quotas e resets |
| `GET` | `/api/v1/ai/capabilities` | consultar recursos do plano |
| `POST` | `/api/v1/ai/patches/{patch_id}/accept` | aceitar alteração |
| `POST` | `/api/v1/ai/patches/{patch_id}/reject` | rejeitar alteração |
| `POST` | `/api/v1/ai/patches/{patch_id}/edit` | editar e ressimular |
| `POST` | `/api/v1/ai/conversations` | criar conversa vazia |
| `GET` | `/api/v1/ai/conversations` | listar conversas |
| `GET` | `/api/v1/ai/conversations/{id}` | carregar conversa |
| `DELETE` | `/api/v1/ai/conversations/{id}` | excluir conversa |

---

# 5. Tipos TypeScript

Os tipos abaixo podem ser colocados em um arquivo como:

```text
src/features/alfred/api/alfred.types.ts
```

Adapte somente o caminho ao padrão do frontend.

```ts
export type UUID = string;
export type ISODateTime = string;

export type SelectedSkill =
  | "auto"
  | "conversar"
  | "analisar_progresso"
  | "reorganizar_rotina"
  | "criar_plano"
  | "consultar_conhecimento";

export type InternalRoute =
  | "safe_response"
  | "deterministic"
  | "alfred"
  | "feedbacker"
  | "rag_then_alfred"
  | "rag_then_feedbacker";

export type PatchEntityType =
  | "goal"
  | "habit"
  | "routine_item"
  | "profile";

export type PatchStatus =
  | "pending"
  | "applied"
  | "rejected"
  | "expired";

export interface AIInvokeRequest {
  conversation_id?: UUID | null;
  message: string;
  selected_skill?: SelectedSkill;
  screen_context?: Record<string, unknown> | null;
  idempotency_key?: UUID | null;
}

export interface AIUsage {
  plan: string;
  units_reserved: number;
  units_consumed: number;
  units_remaining: number | null;
}

export interface QuotaUsage {
  used: number;
  limit: number | null;
  remaining: number | null;
  reset_at: ISODateTime;
}

export interface AIUsageResponse {
  plan: string;
  weighted_units_today: QuotaUsage;
  standard_requests_today: QuotaUsage;
  rag_requests_today: QuotaUsage;
  deep_analyses_this_week: QuotaUsage;
  requests_per_minute: number;
}

export interface AICapabilitiesResponse {
  plan: string;
  capabilities: {
    conversation: boolean;
    deep_analysis: boolean;
    rag: boolean;
    patch_generation: boolean;
    memory: "basic" | "advanced" | string;
    streaming: boolean;
  };
}

export interface EvidenceReference {
  document_id: string;
  chunk_id: string;
  title: string;
  source: string;
  source_ids: string[];
  topic: string | null;
  supporting_excerpt: string | null;
  retrieval_score: number;
  rerank_score: number;
}

export interface ExecutionDiagnosis {
  summary: string;
  data_window: string;
  data_quality: number;
  observed_facts: string[];
}

export interface IdentifiedPattern {
  name: string;
  description: string;
  evidence: string[];
  confidence: number;
}

export interface RootCauseHypothesis {
  hypothesis: string;
  supporting_evidence: string[];
  alternative_explanations: string[];
  confidence: number;
  sensitive: boolean;
}

export interface Recommendation {
  priority: number;
  title: string;
  rationale: string;
  action: string;
}

export interface SuccessMetric {
  name: string;
  baseline: number | string | null;
  target: number | string;
  evaluation_window_days: number;
}

export interface AnalysisReport {
  diagnosis: ExecutionDiagnosis;
  patterns: IdentifiedPattern[];
  hypotheses: RootCauseHypothesis[];
  recommendations: Recommendation[];
  success_metrics: SuccessMetric[];
  metadata: Record<string, unknown>;
}

export interface PatchOperation {
  op: "add" | "remove" | "replace";
  path: `/${string}`;
  value?: string | number | boolean | null;
}

export interface PatchSimulation {
  status: "validated";
  before: Record<string, unknown>;
  after: Record<string, unknown>;
  changed_fields: string[];
}

export interface ProposedPatch {
  patch_id: UUID | null;
  entity_type: PatchEntityType;
  entity_id: UUID | null;
  operations: PatchOperation[];
  reason: string;
  simulation: PatchSimulation | null;
  success_metrics: Array<Record<string, unknown>>;
}

export interface AIInvokeResponse {
  request_id: UUID;
  conversation_id: UUID;
  route: InternalRoute;
  message: string;
  references: EvidenceReference[];
  analysis: AnalysisReport | null;
  proposed_patch: ProposedPatch | null;
  requires_confirmation: boolean;
  usage: AIUsage;
}

export interface AIErrorResponse {
  request_id: UUID;
  code: string;
  message: string;
  details: Record<string, unknown>;
}

export interface AIConversationSummary {
  id: UUID;
  title: string;
  summary_en: string | null;
  created_at: ISODateTime;
  updated_at: ISODateTime;
}

export interface AIMessage {
  id: UUID;
  role: "user" | "assistant" | "system";
  content: string;
  route: InternalRoute | null;
  analysis: AnalysisReport | null;
  references: EvidenceReference[] | null;
  proposed_patch: ProposedPatch | null;
  requires_confirmation: boolean | null;
  patch_status: PatchStatus | null;
  request_id: UUID;
  created_at: ISODateTime;
}

export interface AIConversationDetail extends AIConversationSummary {
  messages: AIMessage[];
}

export interface PatchResolutionResponse {
  patch_id: UUID;
  status: PatchStatus;
  proposed_patch: ProposedPatch;
  audit_id: UUID | null;
  requires_confirmation: boolean;
}
```

`summary_en` é memória técnica do backend. Não a apresente diretamente ao
usuário sem uma decisão explícita de produto.

---

# 6. Habilidades enviadas pelo frontend

## Default recomendado

```json
{
  "selected_skill": "auto"
}
```

`auto` deixa o classificador híbrido considerar texto, contexto, segurança,
complexidade e necessidade de conhecimento.

## Pistas opcionais

| Valor | Uso de interface |
|---|---|
| `conversar` | conversa e orientação geral |
| `analisar_progresso` | análise longitudinal |
| `reorganizar_rotina` | procurar ajustes na rotina |
| `criar_plano` | elaborar plano com base nos dados |
| `consultar_conhecimento` | buscar evidências no RAG |

Uma habilidade é apenas uma pista. O backend pode substituí-la se o texto
indicar outra intenção ou risco.

Valores proibidos no request:

```text
alfred
feedbacker
deterministic
rag_then_alfred
rag_then_feedbacker
safe_response
```

---

# 7. Execução sem streaming

## Endpoint

```http
POST /api/v1/ai/invoke
```

## Request

```json
{
  "conversation_id": null,
  "message": "Analise meu progresso desta semana.",
  "selected_skill": "auto",
  "screen_context": {
    "screen": "dashboard",
    "visible_period": "week"
  },
  "idempotency_key": "5b985db8-a421-4c59-84fb-0c11d2acd318"
}
```

Regras:

- `message`: 1 a 4.000 caracteres no plano Free;
- `screen_context`: JSON serializável com no máximo 8.000 bytes;
- campos desconhecidos produzem `422`;
- `conversation_id=null` cria uma conversa automaticamente;
- `selected_skill` omitido equivale a `auto`.

## Idempotência

Gere uma chave por ação do usuário:

```ts
const idempotencyKey = crypto.randomUUID();
```

Em retry causado por timeout ou queda de rede, reutilize a mesma chave. Para uma
nova mensagem intencional, gere outra.

Não gere uma nova chave automaticamente antes de saber se a tentativa anterior
chegou ao backend, pois isso pode duplicar consumo e mensagens.

O backend vincula a chave ao payload canônico. Reutilizá-la com texto,
conversa, habilidade ou contexto visual diferente retorna `409` com
`code="idempotency_key_reused"`; não trate esse erro como retry.

## Response

```json
{
  "request_id": "e3c78096-d452-4f77-8547-039a870c7460",
  "conversation_id": "1ec6210d-e66b-4eb7-a255-c553fe40c293",
  "route": "feedbacker",
  "message": "Encontrei alguns padrões...",
  "references": [],
  "analysis": {
    "diagnosis": {
      "summary": "4 de 7 ocorrências foram concluídas.",
      "data_window": "2026-07-20..2026-07-26",
      "data_quality": 0.7,
      "observed_facts": ["expected_occurrences=7"]
    },
    "patterns": [],
    "hypotheses": [],
    "recommendations": [],
    "success_metrics": [],
    "metadata": {}
  },
  "proposed_patch": null,
  "requires_confirmation": false,
  "usage": {
    "plan": "free",
    "units_reserved": 3,
    "units_consumed": 3,
    "units_remaining": null
  }
}
```

O exemplo é ilustrativo; não teste textos exatos da resposta da IA. Teste
schema, rota, estados e componentes condicionais.

## Renderização condicional

Sempre renderize:

```text
message
```

Renderize quando existir:

```text
analysis
references
proposed_patch
```

Se `requires_confirmation=true`, `proposed_patch` sempre existe e possui
`patch_id` persistido.

---

# 8. Streaming SSE

## Endpoint

```http
POST /api/v1/ai/stream
```

O body é o mesmo de `/invoke`.

Não use `EventSource`: ele não é adequado para este contrato porque o endpoint
é `POST`, recebe JSON e exige header `Authorization`.

Use `fetch`, `ReadableStream` e `TextDecoder`.

## Ordem possível dos eventos

```text
status
heartbeat   zero ou mais enquanto o grafo está processando
reference   zero ou mais
analysis    zero ou um
patch       zero ou um
token       uma palavra, preservando o espaço que a sucede quando houver
done        exatamente um em sucesso
```

Em falha durante o stream:

```text
status
error
```

Autenticação, plano e rate limit podem falhar antes de o stream começar; nesse
caso a resposta HTTP não será SSE.

## Payloads dos eventos

### `status`

```json
{
  "node": "iniciar_estado",
  "message": "Alfred iniciou a solicitação."
}
```

`node` é informativo. Não construa lógica de negócio baseada nele.

### `heartbeat`

```json
{}
```

Mantém a conexão ativa durante etapas mais longas, como RAG e Feedbacker.
O frontend deve ignorá-lo; ele não altera texto, status ou artefatos.

### `reference`

O payload é um `EvidenceReference`.

### `analysis`

O payload é um `AnalysisReport`.

### `patch`

```json
{
  "patch": {
    "patch_id": "uuid",
    "entity_type": "routine_item",
    "entity_id": "uuid",
    "operations": [
      {
        "op": "replace",
        "path": "/duration_minutes",
        "value": 45
      }
    ],
    "reason": "Motivo",
    "simulation": {
      "status": "validated",
      "before": {
        "duration_minutes": 60
      },
      "after": {
        "duration_minutes": 45
      },
      "changed_fields": ["duration_minutes"]
    },
    "success_metrics": []
  },
  "requires_confirmation": true
}
```

### `token`

```json
{
  "content": "trecho textual da resposta"
}
```

Uma palavra legível (não necessariamente um token do tokenizer). O backend
preserva a pontuação e os espaços originais; ao concatenar, não remova espaços
do fim de um chunk nem acrescente um segundo espaço.

### `done`

```json
{
  "request_id": "uuid",
  "conversation_id": "uuid",
  "route": "alfred",
  "usage": {
    "plan": "free",
    "units_reserved": 1,
    "units_consumed": 1,
    "units_remaining": null
  }
}
```

`done` não repete o texto completo. O texto final é a concatenação dos eventos
`token`.

### `error`

```json
{
  "request_id": "uuid-ou-null",
  "code": "model_unavailable",
  "message": "The alfred model call failed."
}
```

## Estado sugerido

```ts
export interface AlfredStreamState {
  status: "idle" | "connecting" | "streaming" | "done" | "error";
  text: string;
  references: EvidenceReference[];
  analysis: AnalysisReport | null;
  proposedPatch: ProposedPatch | null;
  requestId: UUID | null;
  conversationId: UUID | null;
  route: InternalRoute | null;
  usage: AIUsage | null;
  error: AIErrorResponse | null;
}
```

## Parser mínimo

```ts
type SSEHandler = (event: string, data: unknown) => void;

export async function consumeSSE(
  response: Response,
  onEvent: SSEHandler,
): Promise<void> {
  if (!response.ok) {
    throw await parseApiError(response);
  }

  if (!response.body) {
    throw new Error("Streaming response has no body");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    buffer += decoder.decode(value, { stream: !done });
    buffer = buffer.replaceAll("\r\n", "\n");

    const frames = buffer.split("\n\n");
    buffer = frames.pop() ?? "";

    for (const frame of frames) {
      let eventName = "message";
      const dataLines: string[] = [];

      for (const line of frame.split("\n")) {
        if (line.startsWith("event:")) {
          eventName = line.slice(6).trim();
        } else if (line.startsWith("data:")) {
          dataLines.push(line.slice(5).trimStart());
        }
      }

      if (dataLines.length > 0) {
        onEvent(eventName, JSON.parse(dataLines.join("\n")));
      }
    }

    if (done) break;
  }
}
```

O Codex deve adaptar `parseApiError`, abort e atualização de estado ao stack do
frontend.

## Cancelamento

Use `AbortController`. Ao trocar de conversa, sair da tela ou cancelar
explicitamente:

```ts
controller.abort();
```

Não mantenha dois streams simultâneos no plano Free.

---

# 9. Usage e capabilities

## Usage

```http
GET /api/v1/ai/usage
```

Exemplo:

```json
{
  "plan": "free",
  "weighted_units_today": {
    "used": 5,
    "limit": null,
    "remaining": null,
    "reset_at": "2026-07-27T03:00:00Z"
  },
  "standard_requests_today": {
    "used": 8,
    "limit": 30,
    "remaining": 22,
    "reset_at": "2026-07-27T03:00:00Z"
  },
  "rag_requests_today": {
    "used": 2,
    "limit": 15,
    "remaining": 13,
    "reset_at": "2026-07-27T03:00:00Z"
  },
  "deep_analyses_this_week": {
    "used": 1,
    "limit": 3,
    "remaining": 2,
    "reset_at": "2026-07-27T03:00:00Z"
  },
  "requests_per_minute": 6
}
```

`reset_at` é calculado considerando o timezone do usuário.

Se `limit=null`, não mostre “0 restante”. Apresente como ilimitado ou oculte a
barra, conforme o design.

Atualize usage:

- ao abrir a área do Alfred;
- depois de `done`;
- depois de uma resposta não-streaming;
- depois de erro de quota.

## Capabilities

```http
GET /api/v1/ai/capabilities
```

Exemplo:

```json
{
  "plan": "free",
  "capabilities": {
    "conversation": true,
    "deep_analysis": true,
    "rag": true,
    "patch_generation": true,
    "memory": "basic",
    "streaming": true
  }
}
```

Use capabilities para habilitar controles. Não deduza funcionalidades apenas
pelo nome do plano.

---

# 10. Conversas

## Criar

```http
POST /api/v1/ai/conversations
```

```json
{
  "title": "Planejamento da semana"
}
```

Status:

```text
201 Created
```

O título possui de 1 a 160 caracteres.

Também é possível começar com `conversation_id=null` em `/invoke`; nesse caso o
backend cria uma conversa usando a mensagem como fonte do título.

## Listar

```http
GET /api/v1/ai/conversations
```

Retorna até 50 conversas, mais recentes primeiro:

```json
[
  {
    "id": "uuid",
    "title": "Planejamento da semana",
    "summary_en": null,
    "created_at": "2026-07-26T12:00:00Z",
    "updated_at": "2026-07-26T12:05:00Z"
  }
]
```

## Detalhar

```http
GET /api/v1/ai/conversations/{conversation_id}
```

Retorna metadados e até as 100 mensagens mais recentes em ordem cronológica.
Os artefatos estruturados de `/invoke` e `/stream` são persistidos na mensagem
`assistant` associada ao mesmo `request_id`. Portanto, o detalhe da conversa é
a fonte de verdade também após refresh, troca de tela ou nova sessão.

```json
{
  "id": "uuid",
  "title": "Planejamento da semana",
  "summary_en": "Internal rolling summary.",
  "created_at": "2026-07-26T12:00:00Z",
  "updated_at": "2026-07-26T12:05:00Z",
  "messages": [
    {
      "id": "uuid",
      "role": "user",
      "content": "Como posso organizar a semana?",
      "route": "alfred",
      "analysis": null,
      "references": null,
      "proposed_patch": null,
      "requires_confirmation": null,
      "patch_status": null,
      "request_id": "uuid",
      "created_at": "2026-07-26T12:01:00Z"
    },
    {
      "id": "uuid",
      "role": "assistant",
      "content": "Encontrei uma oportunidade de ajuste.",
      "route": "feedbacker",
      "analysis": {
        "diagnosis": {
          "summary": "A execução caiu nos dias de maior carga.",
          "data_window": "últimos 30 dias",
          "data_quality": 0.9,
          "observed_facts": ["Queda de conclusão às quartas-feiras."]
        },
        "patterns": [],
        "hypotheses": [],
        "recommendations": [],
        "success_metrics": [],
        "metadata": {}
      },
      "references": [],
      "proposed_patch": {
        "patch_id": "uuid",
        "entity_type": "routine_item",
        "entity_id": "uuid",
        "operations": [
          {
            "op": "replace",
            "path": "/duration_minutes",
            "value": 45
          }
        ],
        "reason": "Adequar a carga ao tempo disponível.",
        "simulation": {
          "status": "validated",
          "before": {"duration_minutes": 60},
          "after": {"duration_minutes": 45},
          "changed_fields": ["duration_minutes"]
        },
        "success_metrics": []
      },
      "requires_confirmation": true,
      "patch_status": "pending",
      "request_id": "uuid",
      "created_at": "2026-07-26T12:01:05Z"
    }
  ]
}
```

Os cinco campos de artefato são nullable por compatibilidade:

- mensagens antigas e mensagens `user`/`system` normalmente retornam `null`;
- uma resposta nova sem referências pode retornar `references=[]`;
- `patch_status=null` significa que a mensagem não possui patch persistido;
- `patch_status=pending` exige confirmação e
  `requires_confirmation=true`;
- `applied`, `rejected` e `expired` são estados finais e retornam
  `requires_confirmation=false`.

Não condicione esses campos a uma habilidade específica. O mesmo contrato vale
para `auto`, `analisar_progresso`, `consultar_conhecimento`,
`reorganizar_rotina`, `criar_plano` e `conversar`, qualquer que tenha sido a
rota interna escolhida pelo backend.

Ao editar um patch, o histórico passa a devolver as novas `operations` e a nova
`simulation`, ainda com `patch_status=pending`. Ao aceitar, rejeitar ou expirar,
o `patch_status` da mesma mensagem `assistant/request_id` é atualizado.

## Excluir

```http
DELETE /api/v1/ai/conversations/{conversation_id}
```

Status:

```text
204 No Content
```

Não execute `response.json()` em uma resposta `204`.

A exclusão é lógica. A conversa desaparece da listagem imediatamente e é
removida definitivamente conforme a política de retenção.

## Estado recomendado

Ao trocar de conversa:

1. cancelar stream ativo;
2. limpar estado transitório de patch/análise/referências;
3. buscar detalhes;
4. substituir mensagens e reconstruir analysis/references/patch pelos campos
   de cada mensagem `assistant`;
5. definir `conversation_id`;
6. permitir novo envio.

---

# 11. Human in the Loop: patches

Alfred nunca aplica uma mudança de rotina diretamente durante `/invoke`.

Quando houver sugestão mutável:

```text
requires_confirmation = true
proposed_patch != null
proposed_patch.patch_id != null
proposed_patch.simulation != null
```

O frontend deve mostrar:

- motivo;
- campos alterados;
- estado anterior;
- estado simulado;
- métricas de sucesso;
- botões aceitar, editar e rejeitar.

## Aceitar

```http
POST /api/v1/ai/patches/{patch_id}/accept
```

```json
{
  "idempotency_key": "31c69049-26cf-474c-af71-04194eb5cbc4"
}
```

Response:

```json
{
  "patch_id": "uuid",
  "status": "applied",
  "proposed_patch": {
    "patch_id": "uuid",
    "entity_type": "routine_item",
    "entity_id": "uuid",
    "operations": [
      {
        "op": "replace",
        "path": "/duration_minutes",
        "value": 45
      }
    ],
    "reason": "Reduzir a carga planejada.",
    "simulation": {
      "status": "validated",
      "before": {
        "duration_minutes": 60
      },
      "after": {
        "duration_minutes": 45
      },
      "changed_fields": ["duration_minutes"]
    },
    "success_metrics": []
  },
  "audit_id": "uuid",
  "requires_confirmation": false
}
```

Reutilize a mesma chave em retry de rede. Um aceite confirmado deve atualizar
ou invalidar os caches da rotina, hábito, meta ou perfil afetado.

## Rejeitar

```http
POST /api/v1/ai/patches/{patch_id}/reject
```

```json
{
  "reason": "Não consigo treinar antes das 08:00."
}
```

`reason` é opcional e possui no máximo 500 caracteres.

Response:

```text
status = rejected
requires_confirmation = false
```

O motivo ajuda a memória privada do Feedbacker a evitar sugestões semelhantes.

## Editar

```http
POST /api/v1/ai/patches/{patch_id}/edit
```

```json
{
  "idempotency_key": "5f99c335-85d7-4c0f-bde3-5dfcb2bded80",
  "operations": [
    {
      "op": "replace",
      "path": "/duration_minutes",
      "value": 45
    }
  ]
}
```

Response:

```text
status = pending
requires_confirmation = true
```

A edição não aplica a mudança. O backend revalida, recalcula a simulação e
retorna outro estado pendente. O usuário ainda precisa aceitar.

Não permita que o usuário digite JSON Pointer livremente. A UI deve oferecer
campos editáveis derivados de `operations` e `simulation.changed_fields`.

## Concorrência de UI

Enquanto uma decisão está em andamento:

- desabilite os três botões;
- mostre loading somente no botão escolhido;
- não faça optimistic update da entidade real;
- após sucesso, marque o card com o status retornado;
- em `409` ou `410`, recarregue/feche a proposta.

---

# 12. Erros

Erros da aplicação de IA seguem:

```json
{
  "request_id": "uuid",
  "code": "daily_rag_limit_exceeded",
  "message": "Mensagem segura para apresentação.",
  "details": {}
}
```

Erros de autenticação e validação FastAPI podem ter outro formato, normalmente
com `detail`.

## Status importantes

| Status | Possíveis causas | Comportamento |
|---:|---|---|
| `400` | request semanticamente inválido | mostrar mensagem e manter input |
| `401` | token ausente/expirado | refresh uma vez ou login |
| `403` | e-mail, plano ou ownership | fluxo específico; não fazer retry |
| `404` | conversa/patch não encontrado | remover recurso local |
| `409` | patch já resolvido | fechar confirmação e recarregar |
| `410` | patch expirado | informar expiração |
| `422` | schema inválido | erro de integração; registrar |
| `429` | quota ou rate limit | mostrar reset quando disponível |
| `503` | modelo/grafo/custo global | permitir retry manual |

## Códigos públicos relevantes

```ts
export type AIErrorCode =
  | "invalid_request"
  | "idempotency_key_reused"
  | "conversation_not_found"
  | "conversation_forbidden"
  | "user_context_forbidden"
  | "user_context_unavailable"
  | "plan_unavailable"
  | "rate_limit_exceeded"
  | "daily_quota_exceeded"
  | "daily_standard_limit_exceeded"
  | "daily_rag_limit_exceeded"
  | "weekly_deep_analysis_limit_exceeded"
  | "concurrent_stream_limit_exceeded"
  | "global_cost_limit_exceeded"
  | "patch_not_found"
  | "patch_forbidden"
  | "patch_expired"
  | "patch_already_resolved"
  | "model_unavailable"
  | "model_invalid_output"
  | "graph_execution_failed";
```

Use `code`, não parsing de texto, para decidir UX.

Sempre registre `request_id` na ferramenta de observabilidade do frontend, sem
registrar mensagem, análise ou contexto pessoal.

## Rate limit SlowAPI

O `429` externo do SlowAPI pode não usar `AIErrorResponse`. O parser de erro
deve tolerar:

```ts
interface UnknownApiError {
  detail?: unknown;
  error?: unknown;
  message?: unknown;
  code?: unknown;
  request_id?: unknown;
}
```

---

# 13. Cliente HTTP sugerido

Assumindo um helper autenticado já existente:

```ts
const AI_PREFIX = "/api/v1/ai";

export const alfredApi = {
  invoke(payload: AIInvokeRequest, signal?: AbortSignal) {
    return api.post<AIInvokeResponse>(
      `${AI_PREFIX}/invoke`,
      payload,
      { signal },
    );
  },

  usage() {
    return api.get<AIUsageResponse>(`${AI_PREFIX}/usage`);
  },

  capabilities() {
    return api.get<AICapabilitiesResponse>(
      `${AI_PREFIX}/capabilities`,
    );
  },

  createConversation(title = "Nova conversa") {
    return api.post<AIConversationSummary>(
      `${AI_PREFIX}/conversations`,
      { title },
    );
  },

  listConversations() {
    return api.get<AIConversationSummary[]>(
      `${AI_PREFIX}/conversations`,
    );
  },

  getConversation(conversationId: UUID) {
    return api.get<AIConversationDetail>(
      `${AI_PREFIX}/conversations/${conversationId}`,
    );
  },

  deleteConversation(conversationId: UUID) {
    return api.delete<void>(
      `${AI_PREFIX}/conversations/${conversationId}`,
    );
  },

  acceptPatch(patchId: UUID, idempotencyKey: UUID) {
    return api.post<PatchResolutionResponse>(
      `${AI_PREFIX}/patches/${patchId}/accept`,
      { idempotency_key: idempotencyKey },
    );
  },

  rejectPatch(patchId: UUID, reason?: string) {
    return api.post<PatchResolutionResponse>(
      `${AI_PREFIX}/patches/${patchId}/reject`,
      { reason: reason ?? null },
    );
  },

  editPatch(
    patchId: UUID,
    operations: PatchOperation[],
    idempotencyKey: UUID,
  ) {
    return api.post<PatchResolutionResponse>(
      `${AI_PREFIX}/patches/${patchId}/edit`,
      {
        operations,
        idempotency_key: idempotencyKey,
      },
    );
  },
};
```

Adapte `api.post` ao cliente real. Não crie um segundo sistema independente de
refresh token.

Para `/stream`, use `fetch` diretamente ou um helper que exponha o
`ReadableStream`; muitos wrappers tentam interpretar a resposta como JSON e não
servem para SSE.

---

# 14. Fluxo recomendado da tela

## Entrada na área do Alfred

Execute em paralelo:

```text
GET /capabilities
GET /usage
GET /conversations
```

Não bloqueie toda a tela se apenas usage falhar. Trate os três estados
separadamente.

## Nova mensagem

```text
1. validar texto localmente
2. gerar idempotency_key
3. inserir mensagem otimista do usuário
4. iniciar /stream ou /invoke
5. obter/atualizar conversation_id
6. renderizar resposta
7. renderizar analysis/references/patch se existirem
8. atualizar usage
9. atualizar ordenação/título da conversa
```

Se o request falhar antes de ser aceito:

- mantenha a mensagem com estado `failed`;
- ofereça “tentar novamente”;
- reutilize a idempotency key original.

## Carregamento de conversa

Use o backend como fonte de verdade. Mensagens otimistas podem ser conciliadas
por `request_id` após recarregar os detalhes.

Não mantenha um cache paralelo definitivo para análise, referências ou patch.
Após `GET /conversations/{id}`, derive os cards diretamente de cada
`AIMessage`. Depois de aceitar, editar ou rejeitar, atualize a resposta local e
recarregue a conversa; isso também cobre expiração decidida pelo backend/job.

---

# 15. Segurança e privacidade no frontend

Não enviar:

- token dentro de `screen_context`;
- objetos completos do usuário;
- HTML bruto;
- estado global inteiro;
- chaves de API;
- conteúdo de outras telas não visível/relevante.

`screen_context` deve conter somente pistas pequenas:

```json
{
  "screen": "habit_detail",
  "entity_id": "uuid",
  "visible_period": "month"
}
```

O backend ignora autoridade declarada no contexto e consulta dados pelo usuário
autenticado, mas o frontend ainda deve minimizar dados.

Ao registrar erros:

- registrar `request_id`, status e `code`;
- não registrar `message` do usuário;
- não registrar resposta do Alfred;
- não registrar `screen_context`;
- não registrar trechos RAG.

---

# 16. Estados visuais mínimos

O frontend deve distinguir:

```text
idle
sending
streaming
completed
failed
cancelled
quota_exceeded
plan_unavailable
```

Componentes condicionais sugeridos:

```text
AlfredMessage
AnalysisReportCard
EvidenceReferences
PatchConfirmationCard
UsageIndicator
ConversationSidebar
StreamStatus
```

Não mostre nomes técnicos como `feedbacker`, `rag_then_alfred` ou nodes ao
usuário final. Eles podem aparecer apenas em ferramentas de desenvolvimento ou
observabilidade.

---

# 17. Migração do fluxo antigo

O Codex deve procurar e remover:

- endpoints públicos antigos de chat/Alfred/Feedbacker;
- enum público com `alfred` ou `feedbacker` como seleção;
- requests sem `conversation_id`;
- lógica que aplica sugestão diretamente;
- parser que espera apenas `message`;
- `EventSource` para o novo stream;
- limites hardcoded divergentes de `/usage`;
- caches de conversa que não consideram exclusão `204`;
- retries que geram uma nova idempotency key.

Preservar:

- componentes visuais úteis;
- store de autenticação;
- cliente HTTP base;
- padrões de loading, toast e acessibilidade;
- design system atual.

---

# 18. Testes exigidos no frontend

## Cliente

- envia Bearer token;
- serializa `snake_case`;
- omite opcionais corretamente;
- mantém idempotency key em retry;
- não chama `.json()` em `204`;
- normaliza `AIErrorResponse` e erros com `detail`.

## Invoke

- renderiza resposta determinística;
- renderiza análise;
- renderiza referências;
- renderiza patch somente com confirmação;
- guarda `conversation_id`;
- atualiza usage;
- trata `429` e `503`.

## Streaming

- suporta frames divididos entre chunks;
- concatena tokens com espaço;
- acumula múltiplas referências;
- processa analysis e patch;
- finaliza apenas em `done`;
- trata evento `error`;
- trata erro HTTP antes do SSE;
- aborta ao desmontar/trocar conversa.

## Conversas

- lista mais recentes primeiro;
- carrega mensagens cronologicamente;
- cria nova conversa;
- remove conversa após `204`;
- limpa estado transitório ao trocar.

## Patches

- mostra before/after;
- bloqueia duplo clique;
- aceita com idempotência;
- rejeita com motivo opcional;
- edita e mantém pendente;
- trata `409` e `410`;
- invalida cache da entidade após aceite.

## Acessibilidade

- resposta em streaming usa região `aria-live` sem reler todo o texto a cada
  chunk;
- botões de patch têm labels claros;
- loading não depende somente de cor;
- foco é movido para erro/confirmação quando necessário;
- usuário pode cancelar streaming pelo teclado.

---

# 19. Critérios de aceite da migração

A migração está concluída quando:

- [ ] somente `/api/v1/ai/*` é usado para IA;
- [ ] não existe endpoint público de Feedbacker no frontend;
- [ ] `selected_skill` aceita apenas os seis valores públicos;
- [ ] `/invoke` funciona com e sem `conversation_id`;
- [ ] streaming `POST` autenticado funciona via `fetch`;
- [ ] todas as variantes SSE são tratadas;
- [ ] usage e capabilities vêm do backend;
- [ ] conversas podem ser criadas, listadas, abertas e excluídas;
- [ ] analysis, references e proposed_patch reaparecem após recarregar;
- [ ] mensagens antigas com artefatos `null` continuam renderizando;
- [ ] patches exigem confirmação explícita;
- [ ] edição de patch não é tratada como aceite;
- [ ] status `pending/applied/rejected/expired` é restaurado pelo histórico;
- [ ] idempotência é preservada em retry;
- [ ] erros usam `code` e `request_id`;
- [ ] nenhuma mensagem pessoal é enviada à observabilidade;
- [ ] testes de cliente, streaming, conversas e HITL passam;
- [ ] não há regressão na autenticação/refresh token;
- [ ] interface não exibe nomes internos do grafo.

---

# 20. Resumo operacional

Fluxo principal:

```text
frontend
  → POST /api/v1/ai/invoke ou /stream
  → backend escolhe capacidade
  → response.message
  → analysis/references opcionais
  → proposed_patch opcional
  → usuário aceita, edita ou rejeita
  → frontend atualiza caches e usage
```

Fonte de verdade:

```text
Requests/responses → schemas Pydantic do backend
Conversa/artefatos → endpoints /conversations
Quota              → endpoint /usage
Funcionalidades    → endpoint /capabilities
Mutação            → endpoints /patches com confirmação
```

Se o frontend encontrar uma necessidade que não cabe nesses contratos, não
deve improvisar um endpoint: registre a lacuna para alteração coordenada no
backend.
