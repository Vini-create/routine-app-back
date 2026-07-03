import logging

import httpx

from app.core.config import settings


logger = logging.getLogger(__name__)


class EmailDeliveryError(RuntimeError):
    """Raised when the transactional email provider cannot accept a message."""


async def _send_transactional_email(payload: dict) -> None:
    headers = {
        "api-key": settings.brevo_api_key,
        "content-type": "application/json",
        "accept": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                "https://api.brevo.com/v3/smtp/email",
                json=payload,
                headers=headers,
            )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        status_code = (
            exc.response.status_code if isinstance(exc, httpx.HTTPStatusError) else None
        )
        logger.exception("Transactional email delivery failed (status=%s)", status_code)
        raise EmailDeliveryError("Transactional email delivery failed") from exc


def _language_copy(
    language: str | None, copies: dict[str, dict[str, str]]
) -> dict[str, str]:
    return copies.get(language or "", copies["english_us"])


async def send_verification_email(
    to_email: str, token: str, language: str | None = None
) -> None:
    verification_url = f"{settings.frontend_url}/verify-email?token={token}"
    copy = _language_copy(
        language,
        {
            "portuguese_br": {
                "subject": "Confirme seu e-mail no Winperium",
                "welcome": "Boas-vindas ao Winperium.",
                "instruction": "Confirme seu e-mail para ativar sua conta:",
                "action": "Verificar e-mail",
                "expiry": "Este link é válido por 24 horas. Se você não criou esta conta, ignore esta mensagem.",
            },
            "spanish": {
                "subject": "Confirma tu correo en Winperium",
                "welcome": "Te damos la bienvenida a Winperium.",
                "instruction": "Confirma tu correo para activar tu cuenta:",
                "action": "Verificar correo",
                "expiry": "Este enlace es válido durante 24 horas. Si no creaste esta cuenta, ignora este mensaje.",
            },
            "french": {
                "subject": "Confirmez votre e-mail Winperium",
                "welcome": "Bienvenue sur Winperium.",
                "instruction": "Confirmez votre e-mail pour activer votre compte :",
                "action": "Vérifier l’e-mail",
                "expiry": "Ce lien est valable 24 heures. Si vous n’avez pas créé ce compte, ignorez ce message.",
            },
            "english_us": {
                "subject": "Verify your Winperium email",
                "welcome": "Welcome to Winperium.",
                "instruction": "Verify your email to activate your account:",
                "action": "Verify email",
                "expiry": "This link is valid for 24 hours. If you did not create this account, ignore this message.",
            },
        },
    )

    payload = {
        "sender": {
            "name": settings.email_from_name,
            "email": settings.email_from_address,
        },
        "to": [{"email": to_email}],
        "subject": copy["subject"],
        "htmlContent": f"""
            <div style="font-family:Arial,sans-serif;line-height:1.6;color:#171717">
              <h1 style="font-size:24px">Winperium</h1>
              <p>{copy["welcome"]}</p>
              <p>{copy["instruction"]}</p>
              <p><a href="{verification_url}" style="display:inline-block;padding:12px 20px;border-radius:12px;background:#171717;color:#fff;text-decoration:none;font-weight:700">{copy["action"]}</a></p>
              <p style="color:#666;font-size:13px">{copy["expiry"]}</p>
            </div>
        """,
    }

    await _send_transactional_email(payload)


async def send_password_reset_email(
    to_email: str, token: str, language: str | None = None
) -> None:
    reset_url = f"{settings.frontend_url}/reset-password?token={token}"
    copy = _language_copy(
        language,
        {
            "portuguese_br": {
                "subject": "Redefina sua senha do Winperium",
                "instruction": "Recebemos uma solicitação para redefinir sua senha.",
                "action": "Criar nova senha",
                "expiry": "Este link é válido por 30 minutos. Se você não fez esta solicitação, ignore esta mensagem.",
            },
            "spanish": {
                "subject": "Restablece tu contraseña de Winperium",
                "instruction": "Recibimos una solicitud para restablecer tu contraseña.",
                "action": "Crear nueva contraseña",
                "expiry": "Este enlace es válido durante 30 minutos. Si no hiciste esta solicitud, ignora este mensaje.",
            },
            "french": {
                "subject": "Réinitialisez votre mot de passe Winperium",
                "instruction": "Nous avons reçu une demande de réinitialisation de votre mot de passe.",
                "action": "Créer un nouveau mot de passe",
                "expiry": "Ce lien est valable 30 minutes. Si vous n’êtes pas à l’origine de cette demande, ignorez ce message.",
            },
            "english_us": {
                "subject": "Reset your Winperium password",
                "instruction": "We received a request to reset your password.",
                "action": "Create a new password",
                "expiry": "This link is valid for 30 minutes. If you did not make this request, ignore this message.",
            },
        },
    )

    payload = {
        "sender": {
            "name": settings.email_from_name,
            "email": settings.email_from_address,
        },
        "to": [{"email": to_email}],
        "subject": copy["subject"],
        "htmlContent": f"""
            <div style="font-family:Arial,sans-serif;line-height:1.6;color:#171717">
              <h1 style="font-size:24px">Winperium</h1>
              <p>{copy["instruction"]}</p>
              <p><a href="{reset_url}" style="display:inline-block;padding:12px 20px;border-radius:12px;background:#171717;color:#fff;text-decoration:none;font-weight:700">{copy["action"]}</a></p>
              <p style="color:#666;font-size:13px">{copy["expiry"]}</p>
            </div>
        """,
    }

    await _send_transactional_email(payload)


async def send_login_code_email(
    to_email: str, code: str, language: str | None = None
) -> None:
    copy = _language_copy(
        language,
        {
            "portuguese_br": {
                "subject": "Seu código de acesso ao Winperium",
                "instruction": "Recebemos uma tentativa de login na sua conta. Use este código para confirmar que é você:",
                "expiry": f"O código expira em {settings.login_code_expire_minutes} minutos e só pode ser usado uma vez. Se não foi você, não compartilhe o código e altere sua senha.",
            },
            "spanish": {
                "subject": "Tu código de acceso a Winperium",
                "instruction": "Recibimos un intento de inicio de sesión. Usa este código para confirmar que eres tú:",
                "expiry": f"El código caduca en {settings.login_code_expire_minutes} minutos y solo puede usarse una vez. Si no fuiste tú, no lo compartas y cambia tu contraseña.",
            },
            "french": {
                "subject": "Votre code de connexion Winperium",
                "instruction": "Nous avons reçu une tentative de connexion. Utilisez ce code pour confirmer qu'il s'agit bien de vous :",
                "expiry": f"Le code expire dans {settings.login_code_expire_minutes} minutes et ne peut être utilisé qu'une fois. Si ce n'était pas vous, ne le partagez pas et changez votre mot de passe.",
            },
            "english_us": {
                "subject": "Your Winperium sign-in code",
                "instruction": "We received a sign-in attempt. Use this code to confirm it is you:",
                "expiry": f"The code expires in {settings.login_code_expire_minutes} minutes and can only be used once. If this was not you, do not share it and change your password.",
            },
        },
    )
    payload = {
        "sender": {
            "name": settings.email_from_name,
            "email": settings.email_from_address,
        },
        "to": [{"email": to_email}],
        "subject": copy["subject"],
        "htmlContent": f"""
            <div style="font-family:Arial,sans-serif;line-height:1.6;color:#171717">
              <h1 style="font-size:24px">Winperium</h1>
              <p>{copy["instruction"]}</p>
              <p style="font-size:32px;font-weight:800;letter-spacing:8px;margin:24px 0">{code}</p>
              <p style="color:#666;font-size:13px">{copy["expiry"]}</p>
            </div>
        """,
    }
    await _send_transactional_email(payload)
