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
            if ip_obj.is_link_local or ip_obj.is_loopback:
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

import queue
import atexit

_webhook_queue = queue.Queue(maxsize=1000)

def _webhook_worker():
    while True:
        item = _webhook_queue.get()
        if item is None:
            _webhook_queue.task_done()
            break
        url, data, event_type = item
        try:
            if not is_safe_url(url):
                logger.warning(f"Skipping dispatch to unsafe webhook URL: {url}")
            else:
                requests.post(url, json=data, timeout=5, allow_redirects=False)
                logger.info(f"Webhook dispatched to {url} for event {event_type}")
        except Exception as e:
            logger.error(f"Failed to dispatch webhook to {url}: {e}")
        finally:
            _webhook_queue.task_done()

_worker_thread = threading.Thread(target=_webhook_worker, daemon=True)
_worker_thread.start()

def shutdown_webhooks():
    if not _worker_thread.is_alive(): return
    while True:
        try:
            _webhook_queue.get_nowait()
            _webhook_queue.task_done()
        except queue.Empty:
            break
    try:
        _webhook_queue.put_nowait(None)
    except queue.Full:
        pass
    _webhook_queue.join()
    _worker_thread.join()

atexit.register(shutdown_webhooks)

def dispatch(event_type, payload):
    webhooks = load_webhooks()
    urls_to_notify = [wh["url"] for wh in webhooks if event_type in wh.get("events", [])]

    if not urls_to_notify:
        return

    data = {
        "event": event_type,
        "payload": payload
    }

    for url in urls_to_notify:
        try:
            _webhook_queue.put_nowait((url, data, event_type))
        except queue.Full:
            pass
