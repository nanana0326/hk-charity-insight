from datetime import datetime, timedelta, timezone
from typing import Iterable
from urllib.parse import urlencode

import httpx
from sqlalchemy.orm import Session

from .config import get_settings
from . import models


GOOGLE_AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"


def build_authorization_url(
    *,
    provider: models.GoogleProvider,
    state: str,
) -> str:
    settings = get_settings()
    if not (settings.google_client_id and settings.google_redirect_uri):
        raise RuntimeError("Google OAuth is not configured")

    scopes: Iterable[str]
    if provider is models.GoogleProvider.ANALYTICS:
        scopes = settings.google_analytics_scopes
    else:
        scopes = settings.google_search_console_scopes

    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": " ".join(scopes),
        "access_type": "offline",
        "include_granted_scopes": "true",
        "state": state,
        "prompt": "consent",
    }
    return f"{GOOGLE_AUTH_ENDPOINT}?{urlencode(params)}"


async def exchange_code_for_tokens(
    *,
    code: str,
    provider: models.GoogleProvider,
    tenant_id: int,
    db: Session,
) -> models.GoogleCredential:
    settings = get_settings()
    if not (
        settings.google_client_id
        and settings.google_client_secret
        and settings.google_redirect_uri
    ):
        raise RuntimeError("Google OAuth is not configured")

    data = {
        "code": code,
        "client_id": settings.google_client_id,
        "client_secret": settings.google_client_secret,
        "redirect_uri": settings.google_redirect_uri,
        "grant_type": "authorization_code",
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(GOOGLE_TOKEN_ENDPOINT, data=data, timeout=20)
        resp.raise_for_status()
        payload = resp.json()

    expires_at = None
    if "expires_in" in payload:
        expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=int(payload["expires_in"])
        )

    cred = models.GoogleCredential(
        tenant_id=tenant_id,
        provider=provider,
        access_token=payload["access_token"],
        refresh_token=payload.get("refresh_token"),
        token_type=payload.get("token_type"),
        expires_at=expires_at,
        scope=payload.get("scope"),
    )

    db.add(cred)
    db.commit()
    db.refresh(cred)
    return cred

