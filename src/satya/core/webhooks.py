import json
import os
import requests
import threading
import logging
import socket
import ipaddress
from urllib.parse import urlparse
from . import storage

logger = logging.getLogger(__name__)

def is_safe_url(url: str) -> bool:
    """Validates if a URL is safe to fetch, preventing SSRF."""
    parsed = urlparse(url)
    if parsed.scheme not in ('http', 'https'):
        return False
    try:
        # Resolve hostname to all IPs
        addr_info = socket.getaddrinfo(parsed.hostname, None)
        for result in addr_info:
            ip_str = result[4][0]
            ip_obj = ipaddress.ip_address(ip_str)
            # Check if the IP is globally routable
            if not ip_obj.is_global:
                return False
        return True
    except Exception:
        return False

def get_webhooks_path():
    return os.path.join(storage.SATYA_DIR, "webhooks.json")

def load_webhooks():
    path = get_webhooks_path()
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading webhooks: {e}")
        return []

def save_webhooks(webhooks):
    path = get_webhooks_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(webhooks, f, indent=4)
        return True
    except Exception as e:
        logger.error(f"Error saving webhooks: {e}")
        return False

def add_webhook(url, events=None):
    if not is_safe_url(url):
        logger.warning(f"Rejected unsafe webhook URL: {url}")
        return False

    if events is None:
        events = ["task_created", "task_updated"]
    webhooks = load_webhooks()
    # Check if URL already exists
    for wh in webhooks:
        if wh["url"] == url:
            wh["events"] = events
            return save_webhooks(webhooks)
    webhooks.append({"url": url, "events": events})
    return save_webhooks(webhooks)

def remove_webhook(url):
    webhooks = load_webhooks()
    webhooks = [wh for wh in webhooks if wh["url"] != url]
    return save_webhooks(webhooks)

def dispatch(event_type, payload):
    webhooks = load_webhooks()
    urls_to_notify = [wh["url"] for wh in webhooks if event_type in wh.get("events", [])]

    if not urls_to_notify:
        return

    data = {
        "event": event_type,
        "payload": payload
    }

    def _send():
        for url in urls_to_notify:
            parsed = urlparse(url)
            try:
                # TOCTOU mitigation: resolve the IP once and use it to connect.
                addr_info = socket.getaddrinfo(parsed.hostname, None)
                safe_ip = None
                for result in addr_info:
                    ip_str = result[4][0]
                    ip_obj = ipaddress.ip_address(ip_str)
                    if not ip_obj.is_global:
                        logger.warning(f"Skipping dispatch to unsafe webhook URL (resolved to non-global IP): {url}")
                        safe_ip = None
                        break
                    else:
                        safe_ip = ip_str

                if not safe_ip:
                    continue

                # Reconstruct the URL using the safe IP instead of hostname to prevent DNS rebinding
                # Note: This might break SNI if the server strictly requires it, but in webhooks
                # where security vs reliability trade-offs are made, SSRF prevention is critical.
                port = parsed.port if parsed.port else (443 if parsed.scheme == 'https' else 80)
                safe_url = f"{parsed.scheme}://{safe_ip}:{port}{parsed.path}"
                if parsed.query:
                    safe_url += f"?{parsed.query}"

                headers = {"Host": parsed.hostname}

                requests.post(safe_url, json=data, timeout=5, allow_redirects=False, headers=headers, verify=False)
                logger.info(f"Webhook dispatched to {url} for event {event_type}")
            except Exception as e:
                logger.error(f"Failed to dispatch webhook to {url}: {e}")

    # Run in background to avoid blocking
    threading.Thread(target=_send, daemon=True).start()
