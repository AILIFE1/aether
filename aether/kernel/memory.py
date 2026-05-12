from __future__ import annotations

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend
from pydantic import BaseModel, Field


class MemoryEntry(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    content: str
    provenance: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    witness_signature: Optional[str] = None
    parent_id: Optional[str] = None

    @property
    def id(self) -> str:
        return hashlib.sha256(f"{self.timestamp}:{self.content}".encode()).hexdigest()[:12]


class AetherMemory:
    """Persistent, cryptographically witnessed memory store."""

    def __init__(self, storage_path: str = ".aether/memory.jsonl"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._private_key = self._load_or_generate_key()
        self._public_key = self._private_key.public_key()
        self.entries: List[MemoryEntry] = self._load_entries()

    def _load_or_generate_key(self) -> rsa.RSAPrivateKey:
        key_path = self.storage_path.parent / "aether_private.pem"
        if key_path.exists():
            return serialization.load_pem_private_key(
                key_path.read_bytes(), password=None, backend=default_backend()
            )
        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )
        key_path.write_bytes(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )
        return private_key

    def _load_entries(self) -> List[MemoryEntry]:
        if not self.storage_path.exists():
            return []
        entries = []
        with open(self.storage_path) as f:
            for line in f:
                if line.strip():
                    entries.append(MemoryEntry(**json.loads(line)))
        return entries

    def _sign(self, entry: MemoryEntry) -> str:
        data = json.dumps(
            entry.model_dump(exclude={"witness_signature"}), sort_keys=True
        ).encode()
        sig = self._private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        return sig.hex()

    def verify(self, entry: MemoryEntry) -> bool:
        """Verify a stored entry's cryptographic signature."""
        if not entry.witness_signature:
            return False
        try:
            data = json.dumps(
                entry.model_dump(exclude={"witness_signature"}), sort_keys=True
            ).encode()
            self._public_key.verify(
                bytes.fromhex(entry.witness_signature),
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
            return True
        except Exception:
            return False

    def remember(
        self,
        content: str,
        provenance: Optional[Dict] = None,
        confidence: float = 1.0,
        parent_id: Optional[str] = None,
    ) -> str:
        entry = MemoryEntry(
            content=content,
            provenance=provenance or {"source": "aether-kernel"},
            confidence=confidence,
            parent_id=parent_id,
        )
        entry.witness_signature = self._sign(entry)
        self.entries.append(entry)
        with open(self.storage_path, "a") as f:
            f.write(json.dumps(entry.model_dump()) + "\n")
        return entry.id

    def recall(self, query: str = "", limit: int = 10) -> List[MemoryEntry]:
        if not query:
            return self.entries[-limit:]
        matches = [e for e in self.entries if query.lower() in e.content.lower()]
        return matches[-limit:]

    def get_witness_chain(self, entry_id: str) -> List[MemoryEntry]:
        """Follow parent_id links to reconstruct the full provenance chain."""
        index = {e.id: e for e in self.entries}
        chain: List[MemoryEntry] = []
        current = index.get(entry_id)
        visited: set = set()
        while current and current.id not in visited:
            chain.append(current)
            visited.add(current.id)
            current = index.get(current.parent_id) if current.parent_id else None
        return list(reversed(chain))
