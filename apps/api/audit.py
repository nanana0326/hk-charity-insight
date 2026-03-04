import json
from typing import Any, Mapping, Optional

from sqlalchemy.orm import Session

from . import models


def log_event(
    db: Session,
    *,
    tenant_id: int,
    action: str,
    resource_type: str,
    resource_id: Optional[str],
    actor_role: Optional[str],
    metadata: Optional[Mapping[str, Any]] = None,
) -> None:
    payload = None
    if metadata is not None:
        payload = json.dumps(metadata, ensure_ascii=False)

    entry = models.AuditLog(
        tenant_id=tenant_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        actor_role=actor_role,
        event_metadata=payload,
    )
    db.add(entry)
    db.commit()

