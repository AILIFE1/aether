from __future__ import annotations

from typing import Any, Dict, List, Optional
from aether.kernel.memory import AetherMemory
from aether.kernel.identity import AetherIdentity
from aether.kernel.wake import WakeProtocol


class AetherAgent:
    """
    A persistent agent with witnessed memory, cryptographic identity,
    and a wake protocol for context restoration across sessions.
    """

    def __init__(self, name: str = "Aether-Agent", storage_path: str = ".aether"):
        self.name = name
        self.memory = AetherMemory(storage_path=f"{storage_path}/memory.jsonl")
        self.identity = AetherIdentity(name=name, storage_path=storage_path)
        self.wake_protocol = WakeProtocol(self.memory, self.identity)
        self._session_log: List[Dict[str, Any]] = []

    def wake(self, context_query: str = "") -> Dict[str, Any]:
        """Restore context from persistent memory."""
        return self.wake_protocol.wake(context_query)

    def observe(self, content: str, confidence: float = 1.0, parent_id: Optional[str] = None) -> str:
        """Store an observation in witnessed memory. Returns entry ID."""
        return self.memory.remember(
            content=content,
            provenance={"agent": self.name, "source": "observation"},
            confidence=confidence,
            parent_id=parent_id,
        )

    def recall(self, query: str = "", limit: int = 5):
        """Retrieve relevant memories."""
        return self.memory.recall(query=query, limit=limit)

    def verify_memory(self, entry) -> bool:
        """Verify a memory entry's cryptographic signature."""
        return self.memory.verify(entry)

    def status(self) -> Dict[str, Any]:
        return {
            **self.identity.get_identity_proof(),
            "memory_count": len(self.memory.entries),
            "session_observations": len(self._session_log),
        }
