from datetime import datetime
from typing import Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def audit_log(
    admin_id: int,
    action: str,
    details: Optional[Dict[str, Any]] = None
) -> None:
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "admin_id": admin_id,
        "action": action,
        "details": details or {}
    }
    
    logger.info(f"AUDIT: {log_entry}")
