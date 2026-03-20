import requests
from bs4 import BeautifulSoup
import markdownify
import socket
import ipaddress
from urllib.parse import urlparse, urljoin
from . import storage
from .git_handler import GitHandler

def _is_safe_url(url: str) -> bool:
    """Validates if a URL is safe to fetch, preventing SSRF."""
    parsed = urlparse(url)
    if parsed.scheme not in ('http', 'https'):
        return False
    try:
        # Resolve hostname to IP
        ip_str = socket.gethostbyname(parsed.hostname)
        ip_obj = ipaddress.ip_address(ip_str)
        # Check if the IP is globally routable
        # This prevents accessing loopback, private networks, and link-local (e.g., AWS metadata)
        return ip_obj.is_global
    except Exception:
        return False

class Scraper:
    def __init__(self, repo_path="."):
        self.repo_path = repo_path
        self.git_handler = GitHandler(repo_path)
        storage.ensure_satya_dirs()

    def fetch_and_save(self, url, title=None):
        try:
            current_url = url
            redirect_limit = 5
            response = None

            for _ in range(redirect_limit):
                if not _is_safe_url(current_url):
                    print(f"Error scraping {current_url}: URL resolved to unsafe IP or invalid scheme.")
                    return None

                response = requests.get(current_url, timeout=10, allow_redirects=False)

                if 300 <= response.status_code < 400 and 'location' in response.headers:
                    next_url = response.headers['location']
                    # Resolve relative redirects using urljoin
                    current_url = urljoin(current_url, next_url)
                else:
                    break

            if response is None or (300 <= response.status_code < 400):
                print(f"Error scraping {url}: Too many redirects.")
                return None

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
