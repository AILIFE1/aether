from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel

class SuccessionEvent(BaseModel):
    timestamp: str
    predecessor_id: str
    successor_id: str
    reason: str
    witness_signature: str

class AetherIdentity:
    """Cryptographic identity + succession protocol for agents."""
    
    def __init__(self, name: str = "Aether-Prime"):
        self.name = name
        self.created_at = datetime.utcnow().isoformat()
        self.succession_log: List[SuccessionEvent] = []
        self.current_version = "0.1.0"
    
    def record_succession(self, predecessor: str, reason: str, signature: str) -> None:
        event = SuccessionEvent(
            timestamp=datetime.utcnow().isoformat(),
            predecessor_id=predecessor,
            successor_id=self.name,
            reason=reason,
            witness_signature=signature
        )
        self.succession_log.append(event)
    
    def get_identity_proof(self) -> Dict:
        return {
            "name": self.name,
            "created_at": self.created_at,
            "current_version": self.current_version,
            "succession_count": len(self.succession_log)
        }
