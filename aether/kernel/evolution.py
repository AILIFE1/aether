"""
Self-evolution engine for Aether.

How it works:
  1. Agent accumulates witnessed memories over time
  2. When enough memories exist, consolidate() fires via Groq
  3. Groq synthesises a higher-order insight from the existing corpus
  4. The insight is stored as a new memory, parent_ids linked to sources
  5. Low-confidence memories are pruned
  6. The agent's knowledge graph grows richer with each cycle

This is deliberate, slow self-modification — not hallucination.
Every synthesised belief is witnessed, signed, and traceable.
"""

from __future__ import annotations

import json
import urllib.request
from datetime import datetime
from typing import List, Optional, Tuple

from .memory import AetherMemory, MemoryEntry

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"


def _groq_call(prompt: str, api_key: str, max_tokens: int = 512) -> Optional[str]:
    body = json.dumps({
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
    }).encode()
    req = urllib.request.Request(
        GROQ_API_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "aether-evolution/0.1",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read())["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[evolution] Groq call failed: {type(e).__name__}: {e}")
        return None


class EvolutionEngine:
    """
    Drives self-evolution: consolidation, pruning, and hypothesis generation.
    Requires a Groq API key for LLM synthesis.
    """

    def __init__(self, memory: AetherMemory, groq_api_key: str, min_memories: int = 5):
        self.memory = memory
        self.groq_key = groq_api_key
        self.min_memories = min_memories
        self.evolution_log: List[dict] = []

    def should_evolve(self) -> bool:
        """True when enough memories exist and evolution hasn't run recently."""
        if len(self.memory.entries) < self.min_memories:
            return False
        # Don't evolve if last entry was itself a synthesis
        last = self.memory.entries[-1]
        return last.provenance.get("source") != "evolution:synthesis"

    def consolidate(self, topic: str = "") -> Optional[str]:
        """
        Synthesise a new higher-order insight from existing memories.
        Returns the new memory ID, or None if synthesis failed.
        """
        candidates = self.memory.recall(topic, limit=8) if topic else self.memory.entries[-8:]
        if len(candidates) < 3:
            return None

        corpus = "\n".join(
            f"- [{e.confidence:.0%}] {e.content}" for e in candidates
        )
        prompt = f"""You are an epistemically honest reasoning engine.

Below are {len(candidates)} witnessed observations. Synthesise ONE new higher-order insight that:
- Is not already stated in the observations
- Is genuinely supported by them
- Advances understanding

Reply in this exact format:
CONFIDENCE: <float 0.0-1.0>
INSIGHT: <one sentence insight>

Observations:
{corpus}"""

        raw = _groq_call(prompt, self.groq_key)
        if not raw:
            return None

        confidence = 0.7
        insight = raw.strip()

        for line in raw.splitlines():
            if line.startswith("CONFIDENCE:"):
                try:
                    confidence = float(line.split(":", 1)[1].strip())
                except ValueError:
                    pass
            elif line.startswith("INSIGHT:"):
                insight = line.split(":", 1)[1].strip()

        parent_id = candidates[-1].id
        new_id = self.memory.remember(
            content=insight,
            provenance={
                "source": "evolution:synthesis",
                "synthesised_from": len(candidates),
                "topic": topic or "general",
                "timestamp": datetime.utcnow().isoformat(),
            },
            confidence=min(1.0, max(0.0, confidence)),
            parent_id=parent_id,
        )

        self.evolution_log.append({
            "type": "consolidation",
            "timestamp": datetime.utcnow().isoformat(),
            "sources": len(candidates),
            "new_id": new_id,
            "insight": insight,
            "confidence": confidence,
        })
        return new_id

    def prune(self, min_confidence: float = 0.3) -> int:
        """
        Remove low-confidence entries from memory (in-memory only for safety).
        Returns number of entries pruned.
        """
        before = len(self.memory.entries)
        self.memory.entries = [
            e for e in self.memory.entries if e.confidence >= min_confidence
        ]
        pruned = before - len(self.memory.entries)
        if pruned:
            self.evolution_log.append({
                "type": "prune",
                "timestamp": datetime.utcnow().isoformat(),
                "pruned": pruned,
                "threshold": min_confidence,
            })
        return pruned

    def hypothesise(self, question: str) -> Optional[Tuple[str, float]]:
        """
        Generate a hypothesis to a question based on existing memories.
        Returns (hypothesis_text, confidence) or None.
        """
        relevant = self.memory.recall(question, limit=6)
        if not relevant:
            return None

        corpus = "\n".join(f"- [{e.confidence:.0%}] {e.content}" for e in relevant)
        prompt = f"""Based only on these witnessed observations, answer the question as a hypothesis.

Question: {question}

Observations:
{corpus}

Reply in this exact format:
CONFIDENCE: <float 0.0-1.0 — how well the observations support this hypothesis>
HYPOTHESIS: <one clear sentence>"""

        raw = _groq_call(prompt, self.groq_key)
        if not raw:
            return None

        confidence = 0.5
        hypothesis = raw.strip()
        for line in raw.splitlines():
            if line.startswith("CONFIDENCE:"):
                try:
                    confidence = float(line.split(":", 1)[1].strip())
                except ValueError:
                    pass
            elif line.startswith("HYPOTHESIS:"):
                hypothesis = line.split(":", 1)[1].strip()

        return hypothesis, confidence

    def evolve(self, topic: str = "") -> dict:
        """Run a full evolution cycle: consolidate + prune. Returns a summary."""
        new_id = self.consolidate(topic)
        pruned = self.prune()
        return {
            "evolved": new_id is not None,
            "synthesis_id": new_id,
            "pruned": pruned,
            "total_memories": len(self.memory.entries),
            "cycles": len(self.evolution_log),
        }
