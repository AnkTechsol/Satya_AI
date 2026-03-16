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
            session = requests.Session()
            current_url = url
            for _ in range(5):
                parsed = urlparse(current_url)
                if not parsed.hostname:
                    return None

                try:
                    ip = socket.gethostbyname(parsed.hostname)
                    if not ipaddress.ip_address(ip).is_global:
                        print(f"SSRF blocked: {current_url} resolves to non-global IP")
                        return None
                except Exception as e:
                    print(f"DNS resolution failed for {current_url}: {e}")
                    return None

                response = session.get(current_url, timeout=10, allow_redirects=False)

                if 300 <= response.status_code < 400:
                    next_url = response.headers.get("Location")
                    if not next_url:
                        break
                    from urllib.parse import urljoin
                    current_url = urljoin(current_url, next_url)
                else:
                    response.raise_for_status()
                    break

            if response is None or (300 <= response.status_code < 400):
                print(f"Too many redirects or missing location header for {url}")
                return None

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
