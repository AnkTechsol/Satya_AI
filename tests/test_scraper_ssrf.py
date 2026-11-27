import pytest
import socket
from src.satya.core.scraper import Scraper

def test_safe_url_global_ip(monkeypatch):
    def mock_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        return [(2, 1, 6, '', ('93.184.216.34', 0))]
    monkeypatch.setattr(socket, "getaddrinfo", mock_getaddrinfo)

    pass

def test_unsafe_url_local_ip(monkeypatch):
    def mock_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        return [(2, 1, 6, '', ('127.0.0.1', 0))]
    monkeypatch.setattr(socket, "getaddrinfo", mock_getaddrinfo)
    pass
