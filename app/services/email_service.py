import httpx

from app.core.config import settings


async def send_verification_email(to_email: str, token: str) -> None:
    verification_url = f"{settings.frontend_url}/verify-email?token={token}"

    payload = {
        "sender": {
            "name": settings.email_from_name,
            "email": settings.email_from_address,
        },
        "to": [
            {"email": to_email}
        ],
        "subject": "Verify your email",
        "htmlContent": f"""
            <p>Welcome to AlfredAI.</p>
            <p>Click the link below to verify your email:</p>
            <p><a href="{verification_url}">Verify email</a></p>
        """,
    }

    headers = {
        "api-key": settings.brevo_api_key,
        "content-type": "application/json",
        "accept": "application/json",
    }

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(
            "https://api.brevo.com/v3/smtp/email",
            json=payload,
            headers=headers,
        )

    response.raise_for_status()


async def send_password_reset_email(to_email: str, token: str) -> None:
    reset_url = f"{settings.frontend_url}/reset-password?token={token}"

    payload = {
        "sender": {
            "name": settings.email_from_name,
            "email": settings.email_from_address,
        },
        "to": [
            {"email": to_email}
        ],
        "subject": "Reset your password",
        "htmlContent": f"""
            <p>You requested a password reset.</p>
            <p>Click the link below to create a new password:</p>
            <p><a href="{reset_url}">Reset password</a></p>
            <p>If you did not request this, ignore this email.</p>
        """,
    }

    headers = {
        "api-key": settings.brevo_api_key,
        "content-type": "application/json",
        "accept": "application/json",
    }

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(
            "https://api.brevo.com/v3/smtp/email",
            json=payload,
            headers=headers,
        )

    response.raise_for_status()