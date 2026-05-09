import hashlib
import hmac

def hash_payload(payload_str: str) -> str:
    """Creates a SHA-256 hash of a stringified payload."""
    return hashlib.sha256(payload_str.encode("utf-8")).hexdigest()

def verify_api_key(provided_key: str, allowed_keys: list[str]) -> bool:
    """Verifies if the provided key is in the allowed list."""
    return any(hmac.compare_digest(str(provided_key or ""), str(allowed_key or "")) for allowed_key in allowed_keys)
