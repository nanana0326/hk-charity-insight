from datetime import datetime, timedelta, timezone
import os
import binascii
import hashlib
import hmac
import logging
import smtplib
from email.message import EmailMessage

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from . import models, schemas
from .config import get_settings
from .db import get_db


router = APIRouter(tags=["auth"])
logger = logging.getLogger(__name__)


def _get_default_tenant(db: Session) -> models.Tenant:
    tenant = db.query(models.Tenant).first()
    if tenant is None:
        tenant = models.Tenant(name="Foundation for Shared Impact", is_active=True)
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
    return tenant


def _hash_password(password: str) -> str:
    """Hash password using PBKDF2-HMAC-SHA256 with random salt."""
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return "pbkdf2_sha256$" + binascii.hexlify(salt).decode("ascii") + "$" + binascii.hexlify(
        dk
    ).decode("ascii")


def _verify_password(password: str, stored: str) -> bool:
    try:
        algo, salt_hex, hash_hex = stored.split("$", 2)
        if algo != "pbkdf2_sha256":
            return False
        salt = binascii.unhexlify(salt_hex.encode("ascii"))
        expected = binascii.unhexlify(hash_hex.encode("ascii"))
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
        return hmac.compare_digest(dk, expected)
    except Exception:
        return False


def _send_password_reset_email(to_email: str, reset_link: str) -> None:
    settings = get_settings()
    if (
        not settings.smtp_host
        or not settings.smtp_user
        or not settings.smtp_password
        or not settings.smtp_from_email
    ):
        logger.warning(
            "SMTP not configured; password reset email skipped for %s. Reset link: %s",
            to_email,
            reset_link,
        )
        return

    msg = EmailMessage()
    msg["Subject"] = "Reset your password"
    msg["From"] = settings.smtp_from_email
    msg["To"] = to_email
    msg.set_content(
        "We received a request to reset your password.\n\n"
        f"Open this link to set a new password:\n{reset_link}\n\n"
        "If you did not request this, you can ignore this email."
    )

    if settings.smtp_use_ssl:
        with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=20) as smtp:
            smtp.login(settings.smtp_user, settings.smtp_password)
            smtp.send_message(msg)
        return

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as smtp:
        if settings.smtp_use_tls:
            smtp.starttls()
        smtp.login(settings.smtp_user, settings.smtp_password)
        smtp.send_message(msg)


@router.post("/auth/register", response_model=schemas.UserRead)
def register(payload: schemas.AuthRegisterPayload, db: Session = Depends(get_db)) -> schemas.UserRead:
    """
    Register a new user with email + password.
    """
    tenant = _get_default_tenant(db)

    existing = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing and existing.password_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered.",
        )

    password_hash = _hash_password(payload.password)

    if existing:
        # Upgrade a dev-login user to have a password.
        existing.password_hash = password_hash
        if payload.display_name is not None:
            existing.display_name = payload.display_name
        db.commit()
        db.refresh(existing)
        return schemas.UserRead.model_validate(existing)

    user = models.User(
        tenant_id=tenant.id,
        email=payload.email,
        display_name=payload.display_name,
        role=models.UserRole.ANALYST,
        is_active=True,
        password_hash=password_hash,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return schemas.UserRead.model_validate(user)


@router.post("/auth/login", response_model=schemas.UserRead)
def login(payload: schemas.AuthLoginPayload, db: Session = Depends(get_db)) -> schemas.UserRead:
    """
    Login with email + password.
    """
    tenant = _get_default_tenant(db)

    user = (
        db.query(models.User)
        .filter(models.User.tenant_id == tenant.id, models.User.email == payload.email)
        .first()
    )
    if user is None or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not _verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive.",
        )

    return schemas.UserRead.model_validate(user)


@router.post("/auth/forgot-password")
def forgot_password(
    payload: schemas.AuthForgotPasswordPayload, db: Session = Depends(get_db)
) -> dict:
    """
    Start a password reset flow.

    For now we generate and store a reset token and expiry, but do not send email.
    """
    tenant = _get_default_tenant(db)

    user = (
        db.query(models.User)
        .filter(models.User.tenant_id == tenant.id, models.User.email == payload.email)
        .first()
    )
    if user is None:
        # Do not reveal whether the email exists.
        return {"status": "ok"}

    token_bytes = os.urandom(20)
    token = binascii.hexlify(token_bytes).decode("ascii")
    user.reset_token = token
    user.reset_token_expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    db.commit()

    settings = get_settings()
    reset_link = (
        f"{settings.web_base_url.rstrip('/')}/auth/reset-password?token={token}"
    )
    _send_password_reset_email(user.email, reset_link)

    return {"status": "ok"}


@router.post("/auth/reset-password")
def reset_password(
    payload: schemas.AuthResetPasswordPayload, db: Session = Depends(get_db)
) -> dict:
    """
    Reset password with a one-time token.
    """
    user = db.query(models.User).filter(models.User.reset_token == payload.token).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token.",
        )

    expires_at = user.reset_token_expires_at
    now_utc = datetime.now(timezone.utc)
    if expires_at is not None and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at is None or expires_at <= now_utc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token.",
        )

    if not payload.new_password or len(payload.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters.",
        )

    user.password_hash = _hash_password(payload.new_password)
    user.reset_token = None
    user.reset_token_expires_at = None
    db.commit()
    return {"status": "ok"}
