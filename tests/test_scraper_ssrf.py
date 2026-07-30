import pytest
import socket
from src.satya.core.scraper import _is_safe_url

def test_safe_url_global_ip(monkeypatch):
    # Mock socket.getaddrinfo to return a globally routable IP structure
    # Based on memory: "mock socket.getaddrinfo in unit tests to return a known globally routable IP structure (e.g., [(2, 1, 6, '', ('93.184.216.34', 0))])"
    def mock_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        return [(2, 1, 6, '', ('93.184.216.34', 0))]
    monkeypatch.setattr(socket, "getaddrinfo", mock_getaddrinfo)

    assert _is_safe_url("https://example.com") is True

def test_unsafe_url_local_ip(monkeypatch):
    # Mock to return a private IP
    def mock_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        return [(2, 1, 6, '', ('127.0.0.1', 0))]
    monkeypatch.setattr(socket, "getaddrinfo", mock_getaddrinfo)

    assert _is_safe_url("https://localhost") is False

def test_unsafe_url_mixed_ips(monkeypatch):
    # Mock to return one global IP and one private IP
    def mock_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        return [
            (2, 1, 6, '', ('93.184.216.34', 0)),
            (2, 1, 6, '', ('192.168.1.1', 0))
        ]
    monkeypatch.setattr(socket, "getaddrinfo", mock_getaddrinfo)

    assert _is_safe_url("https://malicious-domain.com") is False

def test_invalid_scheme():
    assert _is_safe_url("ftp://example.com") is False

def test_empty_hostname():
    assert _is_safe_url("https://") is False
