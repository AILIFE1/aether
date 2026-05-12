from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend
from pydantic import BaseModel


class SuccessionEvent(BaseModel):
    timestamp: str
    predecessor_id: str
    successor_id: str
    reason: str
    witness_signature: str


class AetherIdentity:
    """Cryptographic identity + succession protocol. Persists to disk."""

    def __init__(self, name: str = "Aether-Prime", storage_path: str = ".aether"):
        self.name = name
        self.storage_dir = Path(storage_path)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.created_at = self._load_or_set_created()
        self._private_key = self._load_or_generate_key()
        self.succession_log: List[SuccessionEvent] = []
        self.current_version = "0.1.0"

    def _load_or_set_created(self) -> str:
        meta_path = self.storage_dir / "identity.json"
        if meta_path.exists():
            return json.loads(meta_path.read_text()).get("created_at", datetime.utcnow().isoformat())
        ts = datetime.utcnow().isoformat()
        meta_path.write_text(json.dumps({"name": self.name, "created_at": ts}))
        return ts

    def _load_or_generate_key(self) -> rsa.RSAPrivateKey:
        key_path = self.storage_dir / "identity.pem"
        if key_path.exists():
            return serialization.load_pem_private_key(
                key_path.read_bytes(), password=None, backend=default_backend()
            )
        key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )
        key_path.write_bytes(
            key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )
        return key

    @property
    def public_key_fingerprint(self) -> str:
        pub = self._private_key.public_key()
        der = pub.public_bytes(
            serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return hashlib.sha256(der).hexdigest()[:16]

    def sign(self, data: str) -> str:
        sig = self._private_key.sign(
            data.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        return sig.hex()

    def record_succession(self, predecessor: str, reason: str) -> SuccessionEvent:
        witness_sig = self.sign(f"{predecessor}:{self.name}:{reason}")
        event = SuccessionEvent(
            timestamp=datetime.utcnow().isoformat(),
            predecessor_id=predecessor,
            successor_id=self.name,
            reason=reason,
            witness_signature=witness_sig,
        )
        self.succession_log.append(event)
        return event

    def get_identity_proof(self) -> Dict:
        return {
            "name": self.name,
            "created_at": self.created_at,
            "current_version": self.current_version,
            "public_key": self.public_key_fingerprint,
            "succession_count": len(self.succession_log),
        }
