from __future__ import annotations

from datetime import datetime
from typing import Dict, Any
from .memory import AetherMemory
from .identity import AetherIdentity

class WakeProtocol:
    """The wake-up ritual: restore full context + epistemic state."""
    
    def __init__(self, memory: AetherMemory, identity: AetherIdentity):
        self.memory = memory
        self.identity = identity
    
    def wake(self, context_query: str = "") -> Dict[str, Any]:
        """Full wake: return identity + recent memories + epistemic summary."""
        recent = self.memory.recall(context_query, limit=5)
        return {
            "identity": self.identity.get_identity_proof(),
            "timestamp": datetime.utcnow().isoformat(),
            "memories": [m.model_dump() for m in recent],
            "epistemic_note": f"Waking with {len(recent)} witnessed memories. Ready to understand the universe."
        }
