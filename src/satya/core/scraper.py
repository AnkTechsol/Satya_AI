import socket
import ipaddress
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import markdownify
from . import storage
from .git_handler import GitHandler

class Scraper:
    def __init__(self, repo_path="."):
        self.repo_path = repo_path
        self.git_handler = GitHandler(repo_path)
        storage.ensure_satya_dirs()

    def _is_safe_url(self, url):
        """Validates that a URL does not point to internal or link-local resources (SSRF prevention)."""
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https"):
                return False

            hostname = parsed.hostname
            if not hostname:
                return False

            ip_addr = socket.gethostbyname(hostname)
            ip_obj = ipaddress.ip_address(ip_addr)

            # Using is_global ensures we block private networks AND link-local (like AWS metadata 169.254.169.254)
            # Note: This is vulnerable to DNS rebinding (TOCTOU) because requests.get() will resolve the hostname again.
            # A full mitigation would require forcing requests to connect to the pre-validated IP address directly.
            return ip_obj.is_global
        except Exception:
            return False

    def fetch_and_save(self, url, title=None):
        try:
            if not self._is_safe_url(url):
                print(f"Error scraping {url}: URL is not a safe, global address (SSRF prevention).")
                return None

            response = requests.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            if not title:
                if soup.title:
                    title = soup.title.string.strip()
                else:
                    title = "untitled_page"

            safe_title = "".join([c for c in title if c.isalnum() or c in (' ', '-', '_')]).strip().replace(' ', '_')
            filename = f"{safe_title}.md"

            markdown_content = markdownify.markdownify(response.text, heading_style="ATX")

            full_content = f"# {title}\n\nSource: {url}\n\n---\n\n{markdown_content}"

            saved_path = storage.save_markdown(filename, full_content)

            if saved_path:
                self.git_handler.commit_and_push([saved_path], f"Added Truth Source: {title}")
                return filename
            return None

        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None

    def list_sources(self):
        return storage.list_truth_files()
