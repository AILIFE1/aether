from __future__ import annotations

from typing import Any, Callable, List, Optional, Tuple


class GuardianViolation(Exception):
    pass


class Rule:
    def __init__(self, name: str, check: Callable[[str, float], bool], description: str = ""):
        self.name = name
        self.check = check   # (content, confidence) -> is_allowed
        self.description = description


class AetherGuardian:
    """
    Deterministic validation layer. Gates what an agent is allowed to store or act on.
    Rules are evaluated in order; the first hard violation blocks the action.
    """

    BUILTIN = {
        "min_confidence": lambda threshold: Rule(
            name=f"min_confidence_{threshold}",
            check=lambda content, conf: conf >= threshold,
            description=f"Blocks entries with confidence < {threshold}",
        ),
        "no_empty": Rule(
            name="no_empty",
            check=lambda content, conf: bool(content.strip()),
            description="Blocks empty content",
        ),
        "max_length": lambda n: Rule(
            name=f"max_length_{n}",
            check=lambda content, conf: len(content) <= n,
            description=f"Blocks content longer than {n} chars",
        ),
    }

    def __init__(self, rules: Optional[List[Rule]] = None):
        self.rules = list(rules or [])
        self._audit: List[dict] = []

    def add(self, rule: Rule):
        self.rules.append(rule)

    def validate(self, content: str, confidence: float = 1.0) -> Tuple[bool, List[str]]:
        """Returns (is_allowed, list_of_violations)."""
        violations = []
        for rule in self.rules:
            if not rule.check(content, confidence):
                violations.append(rule.name)
        allowed = len(violations) == 0
        self._audit.append({"content_preview": content[:40], "confidence": confidence, "allowed": allowed, "violations": violations})
        return allowed, violations

    def guard(self, content: str, confidence: float = 1.0) -> str:
        """Validate and raise GuardianViolation if blocked."""
        allowed, violations = self.validate(content, confidence)
        if not allowed:
            raise GuardianViolation(f"Blocked by rules: {violations}")
        return content

    @property
    def audit_trail(self) -> List[dict]:
        return list(self._audit)
