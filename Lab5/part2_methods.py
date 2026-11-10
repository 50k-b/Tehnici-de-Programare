# Laborator: funcții, metode și importuri pe web
# Student: Vicol Nadejda
#
# Partea 2: Metode și atribute ale obiectelor web (exercițiile 9-20)

import time

import requests

BASE_URL = "https://cybercor.org"
ECHO_URL = "https://httpbin.org"
TIMEOUT = 10  # secunde


def pause():
    """Pauză de 1 secundă între cereri (regula laboratorului)."""
    time.sleep(1)


def ex09(response):
    """Ex. 9: elementele de bază ale răspunsului."""
    print(response.status_code)  # atribut
    print(response.ok)  # atribut
    print(response.url)  # atribut
    print(response.encoding)  # atribut
    # Toate patru sunt ATRIBUTE (nu au paranteze). O metodă ar avea paranteze,
    # de ex. response.json() sau response.raise_for_status().


def ex10():
    """Ex. 10: tratarea erorilor cu o metodă."""
    home = requests.get(BASE_URL, timeout=TIMEOUT)
    home.raise_for_status()  # pe pagina principală nu face nimic (cod 2xx)
    print("Pagina principală: OK")

    pause()

    try:
        response = requests.get(BASE_URL + "/this-page-does-not-exist", timeout=TIMEOUT)
        response.raise_for_status()  # aruncă HTTPError pentru 4xx/5xx
    except requests.HTTPError as error:
        print("Pagina nu a fost găsită sau serverul a dat o eroare:", error)


def ex11(response):
    """Ex. 11: toate antetele."""
    for name, value in response.headers.items():
        print(f"{name}: {value}")


def ex12(response):
    """Ex. 12: metode de dicționar."""
    print("Server:", response.headers.get("Server", "lipsește"))
    print("Content-Type:", response.headers.get("Content-Type", "lipsește"))
    print("content-type (litere mici):", response.headers.get("content-type", "lipsește"))
    # Observație: rezultatul este același. response.headers este un
    # CaseInsensitiveDict, iar numele antetelor HTTP nu țin cont de majuscule.


def ex13(response):
    """Ex. 13: înlănțuirea metodelor de șir."""
    count = response.text.lower().count("cyber")
    print('Cuvântul "cyber" apare de', count, "ori")
    # .lower() returnează un nou șir (str), deci pe rezultat putem apela direct
    # alte metode de șir, cum este .count().


def ex14(response):
    """Ex. 14: găsirea titlului cu find() și slicing."""
    html = response.text
    start = html.find("<title>") + len("<title>")
    end = html.find("</title>")
    title = html[start:end].strip()
    print("Titlu:", title)


def ex15(response):
    """Ex. 15: numărarea liniilor."""
    lines = response.text.splitlines()
    longest = max(lines, key=len)
    print("Număr de linii:", len(lines))
    print("Lungimea celei mai lungi linii:", len(longest))


def ex16(response):
    """Ex. 16: verificarea HTTPS."""
    if response.url.startswith("https://"):
        print("Conexiune securizată")
    else:
        print("Conexiune nesecurizată")


def ex17():
    """Ex. 17: urmărirea redirecționărilor."""
    response = requests.get("http://cybercor.org", timeout=TIMEOUT)
    for step in response.history:
        print(step.status_code, step.url)
    print("URL final:", response.url)


def ex18():
    """Ex. 18: HEAD versus GET."""
    head = requests.head(BASE_URL, timeout=TIMEOUT)
    pause()
    get = requests.get(BASE_URL, timeout=TIMEOUT)
    print("HEAD len(content):", len(head.content))
    print("GET  len(content):", len(get.content))
    # HEAD cere doar antetele, fără corp, deci len(content) este 0.
    # GET cere și corpul paginii, deci len(content) este mare.
    # HEAD e util ca să verifici rapid dacă o pagină există, fără să o descarci.


def ex19(response):
    """Ex. 19: cookie-uri."""
    if response.cookies:
        for cookie in response.cookies:
            print(cookie.name, cookie.secure)
    else:
        print("Niciun cookie setat")


def ex20():
    """Ex. 20: sesiuni (cererea merge către httpbin.org, nu către cybercor.org)."""
    session = requests.Session()
    session.headers.update({"User-Agent": "WebLab-Vicol-Nadejda"})

    response = session.get(ECHO_URL + "/headers", timeout=TIMEOUT)
    print(response.text)
    sent = response.json()["headers"]["User-Agent"]
    print("User-Agent primit de server:", sent)

    # Verificați-vă: response.text nu are paranteze pentru că este un ATRIBUT
    # (o valoare deja stocată, un șir). response.json() este o METODĂ: execută
    # o acțiune (parsează textul JSON într-un dicționar), deci se apelează cu ().


if __name__ == "__main__":
    # O singură descărcare a paginii principale, refolosită pentru exercițiile de citire.
    home = requests.get(BASE_URL, timeout=TIMEOUT)

    for exercise in (ex09, ex11, ex12, ex13, ex14, ex15, ex16, ex19):
        print(f"\n=== {exercise.__name__} ===")
        exercise(home)

    for exercise in (ex10, ex17, ex18, ex20):
        pause()
        print(f"\n=== {exercise.__name__} ===")
        exercise()
