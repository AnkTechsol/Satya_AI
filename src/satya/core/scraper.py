import socket
import ipaddress
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup
import markdownify
from . import storage
from .git_handler import GitHandler

def _is_safe_url(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https'):
            return False
        hostname = parsed.hostname
        if not hostname:
            return False
        ip = socket.gethostbyname(hostname)
        ip_obj = ipaddress.ip_address(ip)
        return ip_obj.is_global
    except Exception as e:
        print(f"Error resolving or validating URL {url}: {e}")
        return False

class Scraper:
    def __init__(self, repo_path="."):
        self.repo_path = repo_path
        self.git_handler = GitHandler(repo_path)
        storage.ensure_satya_dirs()

    def fetch_and_save(self, url, title=None):
        try:
            current_url = url
            session = requests.Session()
            response = None

            for _ in range(5):
                if not _is_safe_url(current_url):
                    print(f"Error scraping {url}: SSRF block - Unsafe or non-global IP resolved for {current_url}")
                    return None

                response = session.get(current_url, timeout=10, allow_redirects=False)
                if response.is_redirect:
                    next_url = response.headers.get('Location')
                    if not next_url:
                        break
                    current_url = urljoin(current_url, next_url)
                else:
                    break
            else:
                print(f"Error scraping {url}: Too many redirects")
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
