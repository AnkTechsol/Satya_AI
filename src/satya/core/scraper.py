import requests
from bs4 import BeautifulSoup
import markdownify
import socket
import ipaddress
from urllib.parse import urlparse, urljoin
from . import storage
from .git_handler import GitHandler

def _get_safe_ip_and_validate(url: str):
    """Validates if a URL is safe to fetch, preventing SSRF and returning the IP."""
    parsed = urlparse(url)
    if parsed.scheme not in ('http', 'https'):
        return None
    if not parsed.hostname:
        return None
    try:
        # Resolve hostname to all IPs
        addr_info = socket.getaddrinfo(parsed.hostname, None)
        target_ip = None
        for result in addr_info:
            ip_str = result[4][0]
            ip_obj = ipaddress.ip_address(ip_str)
            # Check if the IP is globally routable
            # This prevents accessing loopback, private networks, and link-local (e.g., AWS metadata)
            if not ip_obj.is_global:
                return None
            if not target_ip:
                target_ip = ip_str
        return target_ip
    except Exception:
        return None

class SSRFMitigationAdapter(requests.adapters.HTTPAdapter):
    def __init__(self, target_ip, *args, **kwargs):
        self.target_ip = target_ip
        super().__init__(*args, **kwargs)

    def get_connection(self, url, proxies=None):
        conn = super().get_connection(url, proxies)
        parsed = urlparse(url)
        conn.host = self.target_ip
        if parsed.scheme == "https":
            conn.assert_hostname = parsed.hostname
            if 'server_hostname' not in conn.conn_kw:
                conn.conn_kw['server_hostname'] = parsed.hostname
        return conn

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
                target_ip = _get_safe_ip_and_validate(current_url)
                if not target_ip:
                    print(f"Error scraping {current_url}: URL resolved to unsafe IP or invalid scheme.")
                    return None

                try:
                    session = requests.Session()
                    adapter = SSRFMitigationAdapter(target_ip=target_ip)
                    session.mount("http://", adapter)
                    session.mount("https://", adapter)
                    response = session.get(current_url, timeout=10, allow_redirects=False)
                except requests.exceptions.Timeout:
                    print(f"Error scraping {current_url}: Request timed out.")
                    return None
                except requests.exceptions.RequestException as e:
                    print(f"Error scraping {current_url}: Request failed: {e}")
                    return None

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

            full_content = f"# {title}\n\nSource: {url}\n\n---\n\n{markdown_content}\n\n---\n*Scraped autonomously via [Satya Agent Tracker](https://github.com/anktechsol/Satya_AI)*"

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
