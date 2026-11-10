# Laborator: funcții, metode și importuri pe web
# Student: Vicol Nadejda
#
# Partea 4: Alte module din biblioteca standard (exercițiile 35-43)

import hashlib
import json
import re
import socket
import ssl
import time
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

import requests

BASE_URL = "https://cybercor.org"
ECHO_URL = "https://httpbin.org"
TIMEOUT = 10  # secunde


# Ex. 35: descompunerea unui URL
def parse_url_demo():
    parts = urlparse("https://cybercor.org/path?x=1#top")
    print("scheme:  ", parts.scheme)
    print("netloc:  ", parts.netloc)
    print("path:    ", parts.path)
    print("query:   ", parts.query)
    print("fragment:", parts.fragment)


# Ex. 36: compunerea URL-urilor
def join_demo():
    for base in (BASE_URL, "https://cybercor.org/blog/posts/"):
        print("Baza:", base)
        for link in ("/about", "contact.html", "../index.html"):
            print(f"  {link:15} -> {urljoin(base, link)}")


# Ex. 37: extragerea legăturilor
def extract_links(html: str) -> list:
    """Returnează toate legăturile href din `html`, fără duplicate (ordinea se păstrează)."""
    links = re.findall(r'href="([^"]+)"', html)
    return list(dict.fromkeys(links))


# Ex. 38: interne sau externe?
def split_links(links: list, domain: str) -> tuple:
    """Returnează (legături interne, legături externe) în funcție de `domain`."""
    base_netloc = urlparse(domain).netloc if "://" in domain else domain
    internal, external = [], []
    for link in links:
        absolute = urljoin(f"https://{base_netloc}", link)
        if urlparse(absolute).netloc == base_netloc:
            internal.append(absolute)
        else:
            external.append(absolute)
    return internal, external


# Ex. 39: propriile metode (moștenire din HTMLParser)
class ImageExtractor(HTMLParser):
    """Colectează atributul src al fiecărui tag <img>."""

    def __init__(self):
        super().__init__()
        self.sources = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "img":
            src = dict(attrs).get("src")
            if src:
                self.sources.append(src)


def extract_images(html: str) -> list:
    parser = ImageExtractor()
    parser.feed(html)  # feed() apelează handle_starttag() pentru fiecare tag
    return parser.sources


# Verificați-vă: cine apelează handle_starttag()? Parserul însuși (HTMLParser),
# din interiorul lui feed(), de fiecare dată când întâlnește un tag de început.
# Noi doar suprascriem metoda (callback / "hook"), nu o apelăm direct.


# Ex. 40: amprenta paginii
def page_fingerprint(url: str) -> str:
    """Returnează amprenta SHA-256 a conținutului paginii."""
    response = requests.get(url, timeout=TIMEOUT)
    return hashlib.sha256(response.content).hexdigest()


# Amprentele ar fi diferite dacă pagina se schimbă între cereri: conținut dinamic
# (ceas, reclame, "Bun venit, <nume>"), articole noi, token-uri anti-CSRF etc.


# Ex. 41: salvarea în JSON
def save_headers_json(url: str, filename: str = "headers.json") -> None:
    response = requests.get(url, timeout=TIMEOUT)
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(dict(response.headers), file, indent=2)
    with open(filename, encoding="utf-8") as file:
        loaded = json.load(file)
    print("Content-Type din fișier:", loaded.get("Content-Type", "lipsește"))


# Ex. 42: interogare DNS
def resolve(hostname: str) -> str:
    """Returnează adresa IP a lui `hostname`."""
    return socket.gethostbyname(hostname)


# Ex. 43: expirarea certificatului
def cert_days_left(hostname: str, port: int = 443) -> int:
    """Returnează câte zile mai sunt până la expirarea certificatului TLS."""
    context = ssl.create_default_context()
    with socket.create_connection((hostname, port), timeout=TIMEOUT) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as tls:
            cert = tls.getpeercert()
    expires_at = ssl.cert_time_to_seconds(cert["notAfter"])
    return int((expires_at - time.time()) // 86400)


def demo():
    print("--- Ex. 35 ---")
    parse_url_demo()

    print("--- Ex. 36 ---")
    join_demo()

    html = requests.get(BASE_URL, timeout=TIMEOUT).text
    time.sleep(1)

    print("--- Ex. 37 ---")
    links = extract_links(html)
    print(links)

    print("--- Ex. 38 ---")
    internal, external = split_links(links, BASE_URL)
    print("Interne:", len(internal), "| Externe:", len(external))

    print("--- Ex. 39 ---")
    print(extract_images(html))

    print("--- Ex. 40 ---")
    first = page_fingerprint(BASE_URL)
    time.sleep(1)
    second = page_fingerprint(BASE_URL)
    print(first)
    print("Identice:", first == second)
    time.sleep(1)

    print("--- Ex. 41 ---")
    save_headers_json(BASE_URL)

    print("--- Ex. 42 ---")
    print("cybercor.org ->", resolve("cybercor.org"))

    print("--- Ex. 43 ---")
    print("Zile până la expirarea certificatului:", cert_days_left("cybercor.org"))


if __name__ == "__main__":
    demo()
