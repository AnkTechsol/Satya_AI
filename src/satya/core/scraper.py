import requests
import socket
import ipaddress
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import markdownify
from . import storage
from .git_handler import GitHandler

class Scraper:
    def __init__(self, repo_path="."):
        self.repo_path = repo_path
        self.git_handler = GitHandler(repo_path)
        storage.ensure_satya_dirs()

    def fetch_and_save(self, url, title=None):
        try:
            parsed_url = urlparse(url)
            hostname = parsed_url.hostname

            if not hostname:
                print(f"Invalid URL: {url}")
                return None

            try:
                ip = socket.gethostbyname(hostname)
            except socket.gaierror:
                print(f"Could not resolve hostname: {hostname}")
                return None

            ip_obj = ipaddress.ip_address(ip)
            if not ip_obj.is_global:
                print(f"Security Error: SSRF blocked. IP {ip} is not globally routable.")
                return None

            # A true mitigation for TOCTOU DNS Rebinding with HTTPS SNI is complex.
            # We will use the original URL to preserve SNI and SSL validation,
            # but this leaves a small TOCTOU window. Given the constraints,
            # validating the IP first is a significant security improvement over no validation.
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
