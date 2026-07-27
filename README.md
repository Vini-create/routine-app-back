# Winperium backend

## Integração do frontend com Alfred

O contrato completo das 11 rotas públicas de IA, tipos TypeScript, streaming
SSE, conversas, quotas, erros e confirmação de patches está em
[`FRONTEND_AI_INTEGRATION_GUIDE.md`](FRONTEND_AI_INTEGRATION_GUIDE.md).

## Autenticação Google

Configure no Railway:

```text
GOOGLE_CLIENT_ID=seu-client-id-web.apps.googleusercontent.com
LOGIN_CODE_EXPIRE_MINUTES=10
LOGIN_CODE_MAX_ATTEMPTS=5
```

`GOOGLE_CLIENT_ID` é o mesmo Client ID público usado pelo frontend. Não adicione client secret ao frontend. O deploy executa `alembic upgrade head` pelo `preDeployCommand` do `railway.toml`, criando as tabelas `external_identities` e `login_challenges` antes de iniciar a aplicação.

O login com senha envia um código de uso único por e-mail e só entrega os tokens após `POST /auth/login/verify`. O login Google valida o ID token com a biblioteca oficial, exige `email_verified` e confere um nonce descartável gerado pelo backend.

## Rate limit compartilhado

Em produção, conecte um serviço Redis do Railway e configure no backend:

```text
APP_ENV=production
RATE_LIMIT_STORAGE_URI=${{Redis.REDIS_URL}}
```

Com `APP_ENV=production`, a aplicação não inicia sem Redis. Em
`APP_ENV=development` ou `test`, a ausência da variável ativa o armazenamento
local, adequado somente para desenvolvimento e testes.

## Configuração segura

O startup valida:

- `SECRET_KEY` com no mínimo 64 caracteres;
- JWT limitado a `ALGORITHM=HS256`;
- `CORS_ORIGINS` sem wildcard, paths, queries ou fragments;
- URLs HTTP(S) absolutas;
- expiração de access token entre 5 minutos e 24 horas;
- refresh token entre 1 e 90 dias;
- código de login entre 5 e 30 minutos;
- tentativas do código de login entre 3 e 10.

Banco, Redis, `SECRET_KEY`, Brevo e OpenAI são tratados como `SecretStr` e
aparecem mascarados em representações e logs de configuração.

## Retenção dos dados de IA

Configure um Cron Job diário separado no Railway com:

```bash
python -m app.ai.maintenance.retention
```

O job remove conteúdo temporário expirado e mantém eventos de observabilidade
por 400 dias. Ele imprime somente as contagens excluídas.
