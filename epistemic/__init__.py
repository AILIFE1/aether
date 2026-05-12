from __future__ import annotations

from typing import List
from aether.kernel.memory import MemoryEntry


def confidence_summary(entries: List[MemoryEntry]) -> dict:
    """Summarise the epistemic state of a set of memory entries."""
    if not entries:
        return {"count": 0, "avg_confidence": 0.0, "verified": 0}
    avg = sum(e.confidence for e in entries) / len(entries)
    return {
        "count": len(entries),
        "avg_confidence": round(avg, 3),
        "high_confidence": sum(1 for e in entries if e.confidence >= 0.8),
        "low_confidence": sum(1 for e in entries if e.confidence < 0.5),
    }


def filter_by_confidence(entries: List[MemoryEntry], min_confidence: float = 0.7) -> List[MemoryEntry]:
    """Return only entries meeting a confidence threshold."""
    return [e for e in entries if e.confidence >= min_confidence]


def provenance_sources(entries: List[MemoryEntry]) -> List[str]:
    """List unique provenance sources across entries."""
    sources = set()
    for e in entries:
        sources.update(str(v) for v in e.provenance.values())
    return sorted(sources)
