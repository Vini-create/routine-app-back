#rotas de autenticação

from fastapi import APIRouter, Depends, HTTPException, status
from app.db.db import get_session
from app.api.dependencies import get_current_user
from app.schemas.auth_schemas import AccessToken, AuthActionTokenType, UserCreate, UserLogin, RefreshTokenSchema, Token, UserRegisterResponse, UserMeResponse, ForgotPasswordRequest, ResetPasswordRequest, VerifyEmailRequest, MessageResponse
from app.services.auth_service import register_user, authenticate_user, create_tokens_for_user, refresh_access_token, create_auth_action_token, request_password_reset, reset_password, verify_user
from app.services.email_service import send_verification_email
from fastapi import Request
from app.api.rate_limit import limiter

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/register", response_model=UserRegisterResponse)
@limiter.limit("5/hour")
async def register(request: Request, user_create: UserCreate, session=Depends(get_session)):
    try:
        user, credentials = await register_user(session, user_create.email.lower().strip(), user_create.display_name, user_create.language.value, user_create.password)
        token = await create_auth_action_token(session, user_id=str(user.id), token_type=AuthActionTokenType.EMAIL_VERIFICATION, expires_in_minutes=1440)
        await send_verification_email(to_email=user.email, token=token)
        return {"message": "User registered successfully", "user_id": str(user.id)}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
@auth_router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login(request: Request, user_login: UserLogin, session=Depends(get_session)):
    try:
        user = await authenticate_user(session, user_login.email.lower().strip(), user_login.password)
        access_token, refresh_token = await create_tokens_for_user(session, user)
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@auth_router.post("/refresh", response_model=AccessToken)
@limiter.limit("10/minute")
async def refresh_token(request: Request, refresh_token: RefreshTokenSchema, session=Depends(get_session)):
    try:
        new_access_token = await refresh_access_token(session, refresh_token.refresh_token)
        return {"access_token": new_access_token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    
@auth_router.post("/verify-email", response_model=MessageResponse)
@limiter.limit("10/minute")
async def verify_email_route(request: Request,
    payload: VerifyEmailRequest,
    session=Depends(get_session),
):
    verified = await verify_user(session, payload.token)

    if not verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token",
        )

    return {"message": "Email verified successfully"}

@auth_router.post("/forgot-password", response_model=MessageResponse)
@limiter.limit("3/hour")
async def forgot_password(request: Request,
    payload: ForgotPasswordRequest,
    session=Depends(get_session),
):
    await request_password_reset(session, payload.email.lower().strip())

    return {
        "message": "If the email exists, a password reset link was sent"
    }

@auth_router.post("/reset-password", response_model=MessageResponse)
@limiter.limit("3/minute")
async def reset_password_route(
    request: Request,
    payload: ResetPasswordRequest,
    session=Depends(get_session),
):
    updated = await reset_password(session, payload.token, payload.new_password)

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token",
        )

    return {"message": "Password updated successfully"}

    ### ------------- ROTAS PROTEGIDAS: ------------- ###

@auth_router.get("/me", response_model=UserMeResponse)
@limiter.limit("60/minute")
async def read_current_user(request: Request, current_user=Depends(get_current_user)) -> UserMeResponse:
    return current_user

