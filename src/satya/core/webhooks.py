import json
import os
import requests
import threading
import logging
from . import storage

logger = logging.getLogger(__name__)

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
            try:
                requests.post(url, json=data, timeout=5)
                logger.info(f"Webhook dispatched to {url} for event {event_type}")
            except Exception as e:
                logger.error(f"Failed to dispatch webhook to {url}: {e}")

    # Run in background to avoid blocking
    threading.Thread(target=_send, daemon=True).start()
