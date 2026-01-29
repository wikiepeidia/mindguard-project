"""Encryption utilities for protecting user data."""
import hashlib
import json
from typing import List


def hash_reporter_id(identifier: str, salt: str = "mindguard2025") -> str:
    """Hash reporter identifier for anonymity."""
    data = f"{identifier}{salt}".encode('utf-8')
    return hashlib.sha256(data).hexdigest()


def encrypt_scammer_info(info: str, key: str) -> str:
    """Simple encryption for scammer identifier."""
    # In production, use proper encryption like Fernet
    return hashlib.sha256(f"{info}{key}".encode()).hexdigest()


def validate_evidence(evidence_list: List[str]) -> bool:
    """Validate evidence URLs."""
    if not evidence_list or len(evidence_list) == 0:
        return False
    
    valid_count = 0
    for evidence in evidence_list:
        if evidence and len(evidence.strip()) > 0:
            valid_count += 1
    
    return valid_count >= 1  # At least 1 valid evidence


def serialize_evidence(evidence_list: List[str]) -> str:
    """Convert evidence list to JSON string."""
    return json.dumps(evidence_list)


def deserialize_evidence(evidence_str: str) -> List[str]:
    """Convert JSON string back to evidence list."""
    try:
        return json.loads(evidence_str) if evidence_str else []
    except:
        return []
