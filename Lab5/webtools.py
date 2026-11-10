"""webtools -  modul pentru analiza unui site web.

Laborator: funcții, metode și importuri pe web (Partea 5, ex. 44-50).

Utilizare:
    import webtools
    webtools.get_title(webtools.fetch("https://cybercor.org").text)
"""

# Student: Vicol Nadejda

import csv
import json
import re
import socket
import ssl
import time
from datetime import datetime
from urllib.parse import urljoin, urlparse

import requests

# Bonus (ex. 50): beautifulsoup4 este opțional. Fără el, funcțiile *_bs4 nu merg.
try:
    from bs4 import BeautifulSoup
except ImportError:  # pragma: no cover
    BeautifulSoup = None

TIMEOUT = 10  # secunde

# Ex. 47: constantă de modul, folosită în fetch()
DEFAULT_HEADERS = {"User-Agent": "WebLab-Vicol-Nadejda"}

SECURITY_HEADERS = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Referrer-Policy",
]

# Rețea: cereri HTTP

def fetch(url: str, timeout: int = TIMEOUT) -> requests.Response:
    """Descarcă `url` cu GET și returnează obiectul Response.

    Folosește mereu un timeout și antetele implicite DEFAULT_HEADERS.
    """
    return requests.get(url, timeout=timeout, headers=DEFAULT_HEADERS)


def get_status(url: str) -> int:
    """Returnează codul de stare HTTP pentru `url`."""
    return fetch(url).status_code


def page_exists(url: str) -> bool:
    """Returnează True dacă pagina răspunde cu un cod < 400, altfel False.

    Nu aruncă erori de rețea (domeniu inexistent, timeout etc.).
    """
    try:
        return fetch(url).status_code < 400
    except requests.RequestException:
        return False

# Analiza HTML (fără rețea)
def get_title(html: str) -> str:
    """Returnează textul dintre <title> și </title> (curățat cu strip()).

    Dacă pagina nu are titlu, returnează un șir gol. Nu face nicio cerere
    de rețea: primește doar HTML-ul.
    """
    open_tag, close_tag = "<title>", "</title>"
    start = html.find(open_tag)
    if start == -1:
        return ""
    start += len(open_tag)
    end = html.find(close_tag, start)
    if end == -1:
        return ""
    return html[start:end].strip()


def extract_links(html: str) -> list:
    """Returnează toate valorile href din `html`, fără duplicate (ordinea se păstrează)."""
    links = re.findall(r'href="([^"]+)"', html)
    return list(dict.fromkeys(links))


def split_links(links: list, domain: str) -> tuple:
    """Împarte legăturile în (interne, externe) în funcție de `domain`.

    `domain` poate fi "cybercor.org" sau "https://cybercor.org".
    """
    if "://" in domain:
        base_netloc = urlparse(domain).netloc
    else:
        base_netloc = domain

    internal, external = [], []
    for link in links:
        absolute = urljoin(f"https://{base_netloc}", link)
        if urlparse(absolute).netloc == base_netloc:
            internal.append(absolute)
        else:
            external.append(absolute)
    return internal, external


# Bonus (ex. 50): aceleași două funcții, cu BeautifulSoup
def get_title_bs4(html: str) -> str:
    """Varianta BeautifulSoup a lui get_title(): mai scurtă și tolerantă la atribute/majuscule."""
    soup = BeautifulSoup(html, "html.parser")
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    return ""


def extract_links_bs4(html: str) -> list:
    """Varianta BeautifulSoup a lui extract_links(): găsește și href='...' cu apostrof."""
    soup = BeautifulSoup(html, "html.parser")
    return list(dict.fromkeys(a["href"] for a in soup.find_all("a", href=True)))



# Antete de securitate

def security_headers(url: str) -> dict:
    """Verifică prezența a 5 antete de securitate și returnează {antet: True/False}.

    Dacă cererea eșuează, toate antetele sunt considerate lipsă (False).
    """
    try:
        response = fetch(url)
    except requests.RequestException:
        return {name: False for name in SECURITY_HEADERS}
    return {name: name in response.headers for name in SECURITY_HEADERS}


def score_headers(results: dict) -> str:
    """Primește dicționarul din security_headers() și returnează un scor, ex. "3/5"."""
    present = sum(1 for ok in results.values() if ok)
    return f"{present}/{len(results)}"



# robots.txt

def fetch_robots(base: str):
    """Returnează textul din /robots.txt sau None dacă fișierul lipsește."""
    try:
        response = fetch(urljoin(base, "/robots.txt"))
    except requests.RequestException:
        return None
    if response.status_code == 200:
        return response.text
    return None


def disallowed_paths(robots_text) -> list:
    """Returnează lista valorilor `Disallow:` din robots.txt. Acceptă și None."""
    if not robots_text:
        return []
    paths = []
    for line in robots_text.splitlines():
        line = line.strip()
        if line.lower().startswith("disallow:"):
            value = line.split(":", 1)[1].strip()
            if value:  # "Disallow:" gol înseamnă "nimic interzis"
                paths.append(value)
    return paths



# DNS, certificat, redirecționări

def resolve(hostname: str) -> str:
    """Returnează adresa IP a lui `hostname`."""
    return socket.gethostbyname(hostname)


def cert_days_left(hostname: str, port: int = 443) -> int:
    """Returnează câte zile mai sunt până la expirarea certificatului TLS."""
    context = ssl.create_default_context()
    with socket.create_connection((hostname, port), timeout=TIMEOUT) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as tls:
            cert = tls.getpeercert()
    expires_at = ssl.cert_time_to_seconds(cert["notAfter"])
    return int((expires_at - time.time()) // 86400)


def redirect_chain(url: str) -> list:
    """Returnează lanțul de redirecționări ca listă de {"status": ..., "url": ...}.

    Ultimul element este destinația finală.
    """
    response = fetch(url)
    chain = [{"status": r.status_code, "url": r.url} for r in response.history]
    chain.append({"status": response.status_code, "url": response.url})
    return chain



# Verificarea mai multor căi + raport CSV (ex. 28 și 49)

def check_paths(base: str, paths: list, delay: float = 1) -> dict:
    """Returnează {cale: cod_de_stare} pentru fiecare cale din `paths`.

    Face pauză de `delay` secunde între cereri. Dacă o cerere eșuează,
    valoarea este None.
    """
    results = {}
    for i, path in enumerate(paths):
        if i > 0:
            time.sleep(delay)
        try:
            results[path] = get_status(urljoin(base, path))
        except requests.RequestException:
            results[path] = None
    return results


def save_paths_csv(results: dict, filename: str = "report.csv") -> None:
    """Salvează rezultatul lui check_paths() în CSV (coloane: path, status, checked_at)."""
    checked_at = datetime.now().isoformat()
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["path", "status", "checked_at"])
        writer.writeheader()
        for path, status in results.items():
            writer.writerow({"path": path, "status": status, "checked_at": checked_at})



# Ex. 50: proiectul final

def site_report(url: str, save_to: str = "report.json") -> dict:
    """Colectează informații despre un site, le afișează și le salvează în JSON.

    Include: status și URL final, titlu, IP, lanț de redirecționări (pornind de
    la http://), scor antete de securitate, zile până la expirarea certificatului,
    număr de legături interne/externe și căile interzise din robots.txt.

    Între cereri se face pauză de 1 secundă (regula laboratorului).
    """
    host = urlparse(url).hostname

    response = fetch(url)
    time.sleep(1)

    chain = redirect_chain("http://" + host)
    time.sleep(1)

    headers = security_headers(url)
    time.sleep(1)

    robots = fetch_robots(url)

    internal, external = split_links(extract_links(response.text), url)

    try:
        days_left = cert_days_left(host)
    except (OSError, ssl.SSLError):
        days_left = None

    try:
        ip = resolve(host)
    except OSError:
        ip = None

    report = {
        "url": url,
        "checked_at": datetime.now().isoformat(),
        "status_code": response.status_code,
        "final_url": response.url,
        "title": get_title(response.text),
        "ip": ip,
        "redirect_chain": chain,
        "security_score": score_headers(headers),
        "security_headers": headers,
        "cert_days_left": days_left,
        "internal_links": len(internal),
        "external_links": len(external),
        "disallowed_paths": disallowed_paths(robots),
    }

    for key, value in report.items():
        print(f"{key}: {value}")

    with open(save_to, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)
    print(f"\nRaport salvat în {save_to}")
    return report


# Ex. 46: autotestul rulează doar la `python webtools.py`, nu la `import webtools`.
# Rămâne offline (nu trimite nicio cerere).
if __name__ == "__main__":
    print("Autotest webtools")
    assert get_title("<html><title> Test </title></html>") == "Test"
    assert get_title("<html></html>") == ""
    assert score_headers({"a": True, "b": False, "c": True}) == "2/3"
    assert disallowed_paths(None) == []
    assert disallowed_paths("User-agent: *\nDisallow: /admin\nDisallow:\n") == ["/admin"]
    assert extract_links('<a href="/a"></a><a href="/a"></a><a href="/b"></a>') == ["/a", "/b"]
    internal, external = split_links(["/x", "https://example.com/y"], "cybercor.org")
    assert internal == ["https://cybercor.org/x"]
    assert external == ["https://example.com/y"]
    print("OK: toate testele au trecut")
