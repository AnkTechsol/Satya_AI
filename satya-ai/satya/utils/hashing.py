import hashlib

def hash_payload(payload_str: str) -> str:
    """Creates a SHA-256 hash of a stringified payload."""
    return hashlib.sha256(payload_str.encode("utf-8")).hexdigest()

def verify_api_key(provided_key: str, allowed_keys: list[str]) -> bool:
    """Verifies if the provided key is in the allowed list."""
    # In a real system, you might use constant-time comparison or check against hashed keys
    # For v0.1, simple exact match against the env var list
    return provided_key in allowed_keys
