import pytest
import socket
from src.satya.core.scraper import _get_safe_session

def test_safe_url_global_ip(monkeypatch):
    # Mock socket.getaddrinfo to return a globally routable IP structure
    # Based on memory: "mock socket.getaddrinfo in unit tests to return a known globally routable IP structure (e.g., [(2, 1, 6, '', ('93.184.216.34', 0))])"
    def mock_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        return [(2, 1, 6, '', ('93.184.216.34', 0))]
    monkeypatch.setattr(socket, "getaddrinfo", mock_getaddrinfo)

    session, error = _get_safe_session("https://example.com")
    assert session is not None
    assert error is None

def test_unsafe_url_local_ip(monkeypatch):
    # Mock to return a private IP
    def mock_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        return [(2, 1, 6, '', ('127.0.0.1', 0))]
    monkeypatch.setattr(socket, "getaddrinfo", mock_getaddrinfo)

    session, error = _get_safe_session("https://localhost")
    assert session is None

def test_unsafe_url_mixed_ips(monkeypatch):
    # Mock to return one global IP and one private IP
    def mock_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        return [
            (2, 1, 6, '', ('93.184.216.34', 0)),
            (2, 1, 6, '', ('192.168.1.1', 0))
        ]
    monkeypatch.setattr(socket, "getaddrinfo", mock_getaddrinfo)

    session, error = _get_safe_session("https://malicious-domain.com")
    assert session is None

def test_invalid_scheme():
    session, error = _get_safe_session("ftp://example.com")
    assert session is None

def test_empty_hostname():
    session, error = _get_safe_session("https://")
    assert session is None
