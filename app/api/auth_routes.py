#rotas de autenticação

from fastapi import APIRouter, Depends, HTTPException, status
from app.db.db import get_session
from app.api.dependencies import get_current_user
from app.schemas.auth_schemas import AccessToken, AuthActionTokenType, ChangePasswordRequest, DeleteAccountRequest, UserCreate, UserLogin, RefreshTokenSchema, Token, UserRegisterResponse, UserMeResponse, UserSimpleUpdate, ForgotPasswordRequest, ResendVerificationRequest, ResetPasswordRequest, VerifyEmailRequest, MessageResponse
from app.services.auth_service import register_user, authenticate_user, change_current_user_password, confirm_password, create_tokens_for_user, refresh_access_token, create_auth_action_token, deactivate_current_user, logout_session, request_email_verification, request_password_reset, reset_password, update_current_user, verify_user
from app.services.email_service import EmailDeliveryError, send_verification_email
from fastapi import Request
from app.api.rate_limit import limiter

auth_router = APIRouter(prefix="/auth", tags=["auth"])
users_router = APIRouter(prefix="/users", tags=["users"])

@auth_router.post("/register", response_model=UserRegisterResponse)
@limiter.limit("5/hour")
async def register(request: Request, user_create: UserCreate, session=Depends(get_session)):
    try:
        user, credentials = await register_user(session, user_create.email.lower().strip(), user_create.display_name, user_create.language.value, user_create.password)
        token = await create_auth_action_token(session, user_id=str(user.id), token_type=AuthActionTokenType.EMAIL_VERIFICATION, expires_in_minutes=1440)
        await send_verification_email(to_email=user.email, token=token, language=user.language)
        return {"message": "User registered successfully", "user_id": str(user.id)}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except EmailDeliveryError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Account created, but the verification email could not be sent. Please try resending it.",
        )


@auth_router.post("/resend-verification", response_model=MessageResponse)
@limiter.limit("3/hour")
async def resend_verification_email(
    request: Request,
    payload: ResendVerificationRequest,
    session=Depends(get_session),
):
    try:
        await request_email_verification(session, payload.email.lower().strip())
    except EmailDeliveryError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The verification email could not be sent. Please try again shortly.",
        )

    return {
        "message": "If the account exists and still needs verification, a new email was sent"
    }
    
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
    try:
        await request_password_reset(session, payload.email.lower().strip())
    except EmailDeliveryError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The password reset email could not be sent. Please try again shortly.",
        )

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


@auth_router.patch("/me", response_model=UserMeResponse)
@limiter.limit("30/minute")
async def patch_current_user(
    request: Request,
    payload: UserSimpleUpdate,
    session=Depends(get_session),
    current_user=Depends(get_current_user),
):
    return await update_current_user(session, current_user, payload)


@auth_router.post("/change-password", response_model=MessageResponse)
@limiter.limit("5/hour")
async def change_password(
    request: Request,
    payload: ChangePasswordRequest,
    session=Depends(get_session),
    current_user=Depends(get_current_user),
):
    try:
        await change_current_user_password(
            session,
            current_user,
            payload.current_password,
            payload.new_password,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return {"message": "Password updated successfully. Sign in again on your devices."}


@auth_router.post("/logout", response_model=MessageResponse)
@limiter.limit("30/minute")
async def logout(
    request: Request,
    payload: RefreshTokenSchema,
    session=Depends(get_session),
    current_user=Depends(get_current_user),
):
    await logout_session(session, current_user.id, payload.refresh_token)
    return {"message": "Logout successful"}


@users_router.delete("/me", response_model=MessageResponse)
@limiter.limit("5/hour")
async def delete_current_user(
    request: Request,
    payload: DeleteAccountRequest,
    session=Depends(get_session),
    current_user=Depends(get_current_user),
):
    try:
        await confirm_password(session, current_user, payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    await deactivate_current_user(session, current_user)
    return {"message": "Account deleted successfully"}
