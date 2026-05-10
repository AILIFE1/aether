from __future__ import annotations

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend

class MemoryEntry(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    content: str
    provenance: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    witness_signature: Optional[str] = None
    parent_id: Optional[str] = None

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
            with open(key_path, "rb") as f:
                return rsa.load_pem_private_key(f.read(), password=None, backend=default_backend())
        else:
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            with open(key_path, "wb") as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            return private_key
    
    def _load_entries(self) -> List[MemoryEntry]:
        if not self.storage_path.exists():
            return []
        entries = []
        with open(self.storage_path, "r") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    entries.append(MemoryEntry(**data))
        return entries
    
    def remember(self, content: str, provenance: Optional[Dict] = None, confidence: float = 1.0, parent_id: Optional[str] = None) -> str:
        """Store a new memory with cryptographic witness."""
        entry = MemoryEntry(
            content=content,
            provenance=provenance or {"source": "aether-kernel"},
            confidence=confidence,
            parent_id=parent_id
        )
        # Sign the memory
        data_to_sign = json.dumps(entry.model_dump(exclude={"witness_signature"}), sort_keys=True).encode()
        signature = self._private_key.sign(
            data_to_sign,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        entry.witness_signature = signature.hex()
        
        self.entries.append(entry)
        with open(self.storage_path, "a") as f:
            f.write(json.dumps(entry.model_dump()) + "\n")
        return entry.timestamp
    
    def recall(self, query: str = "", limit: int = 10) -> List[MemoryEntry]:
        """Simple recall with optional fuzzy search."""
        if not query:
            return self.entries[-limit:]
        # Basic keyword search for v0
        return [e for e in self.entries if query.lower() in e.content.lower()][-limit:]
    
    def get_witness_chain(self, entry_id: str) -> List[MemoryEntry]:
        """Reconstruct provenance chain."""
        # Simplified for v0
        return self.entries

# Missing import fix for serialization
try:
    from cryptography.hazmat.primitives import serialization
except ImportError:
    pass
