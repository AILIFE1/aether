"""
Aether Kernel - Persistent Identity & Memory Core
The foundation for all Aether agents: never forget, never drift.
"""

from .memory import AetherMemory
from .identity import AetherIdentity
from .wake import WakeProtocol

__all__ = ["AetherMemory", "AetherIdentity", "WakeProtocol"]

__version__ = "0.1.0-alpha"
