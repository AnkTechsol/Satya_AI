import pytest
import socket
from src.satya.core.scraper import _get_safe_ip

def test_safe_url_global_ip(monkeypatch):
    # Mock socket.getaddrinfo to return a globally routable IP structure
    # Based on memory: "mock socket.getaddrinfo in unit tests to return a known globally routable IP structure (e.g., [(2, 1, 6, '', ('93.184.216.34', 0))])"
    def mock_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        return [(2, 1, 6, '', ('93.184.216.34', 0))]
    monkeypatch.setattr(socket, "getaddrinfo", mock_getaddrinfo)

    assert _get_safe_ip("https://example.com") == '93.184.216.34'

def test_unsafe_url_local_ip(monkeypatch):
    # Mock to return a private IP
    def mock_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        return [(2, 1, 6, '', ('127.0.0.1', 0))]
    monkeypatch.setattr(socket, "getaddrinfo", mock_getaddrinfo)

    assert _get_safe_ip("https://localhost") is None

def test_unsafe_url_mixed_ips(monkeypatch):
    # Mock to return one global IP and one private IP
    def mock_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        return [
            (2, 1, 6, '', ('93.184.216.34', 0)),
            (2, 1, 6, '', ('192.168.1.1', 0))
        ]
    monkeypatch.setattr(socket, "getaddrinfo", mock_getaddrinfo)

    assert _get_safe_ip("https://malicious-domain.com") is None

def test_invalid_scheme():
    assert _get_safe_ip("ftp://example.com") is None

def test_empty_hostname():
    assert _get_safe_ip("https://") is None
