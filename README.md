# Winperium backend

## Autenticação Google

Configure no Railway:

```text
GOOGLE_CLIENT_ID=seu-client-id-web.apps.googleusercontent.com
LOGIN_CODE_EXPIRE_MINUTES=10
LOGIN_CODE_MAX_ATTEMPTS=5
```

`GOOGLE_CLIENT_ID` é o mesmo Client ID público usado pelo frontend. Não adicione client secret ao frontend. O deploy executa `alembic upgrade head` pelo `preDeployCommand` do `railway.toml`, criando as tabelas `external_identities` e `login_challenges` antes de iniciar a aplicação.

O login com senha envia um código de uso único por e-mail e só entrega os tokens após `POST /auth/login/verify`. O login Google valida o ID token com a biblioteca oficial, exige `email_verified` e confere um nonce descartável gerado pelo backend.
