import pytest
from unittest.mock import patch
from src.satya.core.scraper import Scraper

@patch("src.satya.core.scraper.socket.gethostbyname")
@patch("src.satya.core.scraper.requests.get")
def test_scraper_ssrf_protection_private_ip(mock_get, mock_gethostbyname):
    scraper = Scraper()
    # Mock socket resolution to return localhost
    mock_gethostbyname.return_value = "127.0.0.1"

    # Try to scrape local URL
    result = scraper.fetch_and_save("http://localhost:8080/admin")

    assert result is None
    # Verify that requests.get was NEVER called because SSRF protection blocked it
    mock_get.assert_not_called()

@patch("src.satya.core.scraper.socket.gethostbyname")
@patch("src.satya.core.scraper.requests.get")
def test_scraper_ssrf_protection_aws_metadata(mock_get, mock_gethostbyname):
    scraper = Scraper()
    # Mock socket resolution to return AWS metadata link-local address
    mock_gethostbyname.return_value = "169.254.169.254"

    # Try to scrape the AWS metadata endpoint
    result = scraper.fetch_and_save("http://169.254.169.254/latest/meta-data")

    assert result is None
    # Verify that requests.get was NEVER called because SSRF protection blocked it
    mock_get.assert_not_called()

def test_scraper_ssrf_protection_invalid_scheme():
    scraper = Scraper()
    # Try to scrape using a non-http(s) scheme (e.g., file://)
    result = scraper.fetch_and_save("file:///etc/passwd")

    assert result is None
