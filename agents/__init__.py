from __future__ import annotations

from typing import Any, Dict, List, Optional
from aether.kernel.memory import AetherMemory, MemoryEntry
from aether.kernel.identity import AetherIdentity
from aether.kernel.wake import WakeProtocol
from aether.kernel.evolution import EvolutionEngine


class AetherAgent:
    """
    A persistent, self-evolving agent with:
    - Witnessed memory (cryptographically signed)
    - Cryptographic identity (persists across sessions)
    - Wake protocol (context restoration)
    - Evolution engine (synthesises insights from accumulated observations)
    """

    def __init__(
        self,
        name: str = "Aether-Agent",
        storage_path: str = ".aether",
        groq_api_key: str = "",
        auto_evolve_threshold: int = 10,
    ):
        self.name = name
        self.memory = AetherMemory(storage_path=f"{storage_path}/memory.jsonl")
        self.identity = AetherIdentity(name=name, storage_path=storage_path)
        self.wake_protocol = WakeProtocol(self.memory, self.identity)
        self.evolution: Optional[EvolutionEngine] = (
            EvolutionEngine(self.memory, groq_api_key) if groq_api_key else None
        )
        self.auto_evolve_threshold = auto_evolve_threshold

    def wake(self, context_query: str = "") -> Dict[str, Any]:
        """Restore context from persistent memory."""
        return self.wake_protocol.wake(context_query)

    def observe(
        self,
        content: str,
        confidence: float = 1.0,
        parent_id: Optional[str] = None,
    ) -> str:
        """Store a witnessed observation. Returns entry ID. Auto-evolves if threshold met."""
        entry_id = self.memory.remember(
            content=content,
            provenance={"agent": self.name, "source": "observation"},
            confidence=confidence,
            parent_id=parent_id,
        )
        if (
            self.evolution
            and len(self.memory.entries) >= self.auto_evolve_threshold
            and self.evolution.should_evolve()
        ):
            self.evolution.evolve()
        return entry_id

    def recall(self, query: str = "", limit: int = 5) -> List[MemoryEntry]:
        return self.memory.recall(query=query, limit=limit)

    def verify_memory(self, entry: MemoryEntry) -> bool:
        return self.memory.verify(entry)

    def evolve(self, topic: str = "") -> Dict[str, Any]:
        """Manually trigger an evolution cycle. Requires groq_api_key."""
        if not self.evolution:
            return {"error": "No Groq API key configured — evolution unavailable"}
        return self.evolution.evolve(topic)

    def hypothesise(self, question: str) -> Optional[str]:
        """Generate a hypothesis from existing memories using Groq."""
        if not self.evolution:
            return None
        result = self.evolution.hypothesise(question)
        if result:
            hypothesis, confidence = result
            self.memory.remember(
                content=hypothesis,
                provenance={"source": "evolution:hypothesis", "question": question},
                confidence=confidence,
            )
            return f"[{confidence:.0%}] {hypothesis}"
        return None

    def status(self) -> Dict[str, Any]:
        evolution_cycles = len(self.evolution.evolution_log) if self.evolution else 0
        return {
            **self.identity.get_identity_proof(),
            "memory_count": len(self.memory.entries),
            "evolution_cycles": evolution_cycles,
            "evolution_enabled": self.evolution is not None,
        }
