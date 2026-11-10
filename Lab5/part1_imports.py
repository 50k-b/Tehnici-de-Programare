# Laborator: funcții, metode și importuri pe web
# Student: Vicol Nadejda
#
# Partea 1: Importuri (exercițiile 1-8)

import time
import urllib.request

import requests

BASE_URL = "https://cybercor.org"
ECHO_URL = "https://httpbin.org"
TIMEOUT = 10  # secunde


def pause():
    """Pauză de 1 secundă între cereri (regula laboratorului)."""
    time.sleep(1)


def ex01():
    """Ex. 1: primul import."""
    print("requests versiunea:", requests.__version__)
    print("urllib.request se află în:", urllib.request.__name__)
    # 'urllib' face parte din biblioteca standard (vine cu Python, nu se instalează).
    # 'requests' este o bibliotecă externă (third-party): se instalează din PyPI cu pip.


def ex02():
    """Ex. 2: două stiluri de import."""
    # Stilul 1: import requests
    response = requests.get(BASE_URL, timeout=TIMEOUT)
    print("Stilul 1 ->", response.status_code)
    # Avantaj: clar de unde vine funcția (requests.get) și fără conflicte de nume.

    pause()

    # Stilul 2: from requests import get
    from requests import get

    response = get(BASE_URL, timeout=TIMEOUT)
    print("Stilul 2 ->", response.status_code)
    # Avantaj: cod mai scurt, apelezi direct get(...).


def ex03():
    """Ex. 3: alias-uri."""
    import requests as rq

    response = rq.get(BASE_URL, timeout=TIMEOUT)
    print("Cu alias rq ->", response.status_code)
    # Alias-ul ajută la nume lungi sau la convenții cunoscute de toți
    # (import pandas as pd, import numpy as np).
    # Alias-ul încurcă dacă e obscur sau ambiguu (de ex. "r" sau "rq")
    # și cititorii nu îl recunosc.


def ex04():
    """Ex. 4: doar biblioteca standard (urllib.request)."""
    with urllib.request.urlopen(BASE_URL, timeout=TIMEOUT) as response:
        print("Status:", response.status)
        body = response.read().decode("utf-8")  # .read() dă bytes -> decodăm în str
    print(body[:200])


def ex05():
    """Ex. 5: privim în interiorul unui modul."""
    print(dir(requests))
    # Trei nume din rezultat:
    # - get        -> FUNCȚIE (requests.get trimite o cerere GET)
    # - Response   -> CLASĂ (obiectul returnat de o cerere)
    # - exceptions -> MODUL (conține ConnectionError, Timeout, HTTPError etc.)
    for name in ("get", "Response", "exceptions"):
        print(name, "->", type(getattr(requests, name)).__name__)


def ex06():
    """Ex. 6: citim documentația."""
    help(requests.get)
    # Parametrul care setează timpul maxim de așteptare este `timeout`.
    response = requests.get(BASE_URL, timeout=TIMEOUT)
    print("Cerere cu timeout ->", response.status_code)


def ex07():
    """Ex. 7: cronometrarea unei cereri."""
    start = time.perf_counter()
    response = requests.get(BASE_URL, timeout=TIMEOUT)
    total = time.perf_counter() - start

    print(f"perf_counter: {total:.3f} s")
    print(f"response.elapsed: {response.elapsed.total_seconds():.3f} s")
    # perf_counter() măsoară tot ce face apelul (conectare, TLS, cerere, răspuns,
    # descărcarea corpului). response.elapsed măsoară doar de la trimiterea cererii
    # până la primirea antetelor, de aceea e de obicei mai mic.


def ex08():
    """Ex. 8: când un import eșuează."""
    try:
        import bs4  # noqa: F401

        print("bs4 este instalat, versiunea", bs4.__version__)
    except ImportError:
        print("Instalați modulul cu: pip install beautifulsoup4")

    # Verificați-vă: modul vs. pachet vs. bibliotecă
    # - modul:     un singur fișier .py (ex. helper.py)
    # - pachet:    director cu mai multe module (de obicei cu __init__.py)
    # - bibliotecă: termen general, colecție de pachete/module (requests, pandas)


if __name__ == "__main__":
    # Exercițiile cu rețea sunt separate prin pauze de 1 secundă.
    for exercise in (ex01, ex02, ex03, ex04, ex05, ex06, ex07, ex08):
        print(f"\n=== {exercise.__name__} ===")
        exercise()
        pause()
