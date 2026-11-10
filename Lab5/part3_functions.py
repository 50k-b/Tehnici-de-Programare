# Laborator: funcții, metode și importuri pe web
# Student: Vicol Nadejda
#
# Partea 3: Scrierea propriilor funcții (exercițiile 21-34)

import time
from urllib.parse import urljoin

import requests

BASE_URL = "https://cybercor.org"
ECHO_URL = "https://httpbin.org"
TIMEOUT = 10  # secunde


# Ex. 21 + 23: fetch(url) cu parametru implicit timeout=10
def fetch(url, timeout=10):
    """Descarcă `url` cu GET și returnează obiectul Response."""
    return requests.get(url, timeout=timeout)


# Ex. 22 + 26: get_status cu adnotări de tip
def get_status(url: str) -> int:
    """Returnează codul de stare HTTP pentru adresa `url`."""
    return fetch(url).status_code


# Ex. 24 + 25: o singură sarcină pe funcție + docstring
def get_title(html: str) -> str:
    """Returnează titlul paginii (textul dintre <title> și </title>).

    Primește un șir HTML și nu face nicio operație de rețea.
    """
    start = html.find("<title>") + len("<title>")
    end = html.find("</title>")
    return html[start:end].strip()


# Ex. 27
def page_exists(url: str) -> bool:
    """Returnează True dacă pagina există (cod < 400), altfel False, fără să arunce erori."""
    try:
        return requests.get(url, timeout=TIMEOUT).status_code < 400
    except requests.RequestException:
        return False


# Ex. 28
def check_paths(base: str, paths: list) -> dict:
    """Returnează {cale: cod_de_stare} pentru fiecare cale din listă."""
    results = {}
    for i, path in enumerate(paths):
        if i > 0:
            time.sleep(1)  # pauză între cereri
        results[path] = get_status(urljoin(base, path))
    return results


# Ex. 29
def get_header(url: str, name: str, default: str = "lipsește") -> str:
    """Returnează valoarea unui singur antet, sau `default` dacă lipsește."""
    return fetch(url).headers.get(name, default)


# Ex. 30
SECURITY_HEADERS = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Referrer-Policy",
]


def security_headers(url: str) -> dict:
    """Returnează {antet: True/False} pentru cele 5 antete de securitate."""
    try:
        response = fetch(url)
    except requests.RequestException:
        return {name: False for name in SECURITY_HEADERS}
    return {name: name in response.headers for name in SECURITY_HEADERS}


# Ex. 31
def score_headers(results: dict) -> str:
    """Primește dicționarul din security_headers() și returnează un scor, ex. "3/5"."""
    present = sum(1 for ok in results.values() if ok)
    return f"{present}/{len(results)}"


# Ex. 32
def fetch_robots(base: str):
    """Returnează textul din /robots.txt sau None dacă fișierul lipsește."""
    try:
        response = fetch(urljoin(base, "/robots.txt"))
    except requests.RequestException:
        return None
    return response.text if response.status_code == 200 else None


def disallowed_paths(robots_text) -> list:
    """Returnează lista valorilor `Disallow:`. Funcționează și cu None."""
    if not robots_text:
        return []
    paths = []
    for line in robots_text.splitlines():
        line = line.strip()
        if line.lower().startswith("disallow:"):
            value = line.split(":", 1)[1].strip()
            if value:
                paths.append(value)
    return paths


# Ex. 33
def response_times(*urls) -> dict:
    """Returnează {url: secunde} pentru oricâte URL-uri (None dacă cererea eșuează)."""
    times = {}
    for i, url in enumerate(urls):
        if i > 0:
            time.sleep(1)
        start = time.perf_counter()
        try:
            fetch(url)
            times[url] = round(time.perf_counter() - start, 3)
        except requests.RequestException:
            times[url] = None
    return times


# Ex. 34
def log(message, **details):
    """Afișează mesajul urmat de fiecare detaliu, ex.: verificat | url=... | status=200."""
    parts = [message]
    for key, value in details.items():
        parts.append(f"{key}={value}")
    print(" | ".join(parts))


# Verificați-vă: print() vs return
# - print() doar afișează o valoare pe ecran; valoarea se pierde, iar funcția
#   returnează None.
# - return trimite valoarea înapoi apelantului, care o poate salva, transmite altei
#   funcții sau folosi în calcule. return oprește și execuția funcției.


def demo():
    print("--- Ex. 21 ---")
    print(fetch(BASE_URL).status_code)

    print("--- Ex. 22 ---")
    for path in ("/", "/robots.txt", "/sitemap.xml"):
        print(path, get_status(BASE_URL + path))
        time.sleep(1)

    print("--- Ex. 23 ---")
    print(fetch(BASE_URL).status_code)  # timeout implicit (10)
    time.sleep(1)
    print(fetch(BASE_URL, timeout=3).status_code)
    time.sleep(1)

    print("--- Ex. 24 ---")
    print(get_title(fetch(BASE_URL).text))
    time.sleep(1)

    print("--- Ex. 25 ---")
    help(get_title)

    print("--- Ex. 26 ---")
    print(get_status(BASE_URL))
    try:
        get_status(123)
    except requests.RequestException as error:
        # Adnotările de tip nu opresc apelul: sunt doar indicii pentru programatori
        # și unelte (mypy, IDE). Eroarea vine din requests (URL fără schemă).
        print(f"Eroare ({type(error).__name__}): {error}")
    time.sleep(1)

    print("--- Ex. 27 ---")
    print(page_exists(BASE_URL))
    print(page_exists("https://this-domain-does-not-exist.invalid"))
    time.sleep(1)

    print("--- Ex. 28 ---")
    print(check_paths(BASE_URL, ["/", "/robots.txt", "/sitemap.xml"]))
    time.sleep(1)

    print("--- Ex. 29 ---")
    print(get_header(BASE_URL, name="Server"))
    time.sleep(1)

    print("--- Ex. 30 + 31 ---")
    results = security_headers(BASE_URL)
    print(results)
    print(score_headers(results))
    time.sleep(1)

    print("--- Ex. 32 ---")
    robots = fetch_robots(BASE_URL)
    print(disallowed_paths(robots))
    print(disallowed_paths(None))
    time.sleep(1)

    print("--- Ex. 33 ---")
    print(response_times(BASE_URL, ECHO_URL))

    print("--- Ex. 34 ---")
    log("verificat", url=BASE_URL, status=200)


if __name__ == "__main__":
    demo()
