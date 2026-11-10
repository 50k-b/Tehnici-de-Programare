# Laborator: funcții, metode și importuri pe web
# Student: Vicol Nadejda
#
# Partea 5: propriul modul (exercițiile 44-50)
# Rulare: python main.py https://cybercor.org

import argparse
import time

import requests

# Ex. 44: import de modul întreg
import webtools

# Ex. 45: import de nume anume
from webtools import DEFAULT_HEADERS, get_title, score_headers, security_headers

# Dacă main.py ar avea și o funcție proprie get_title, ea ar înlocui funcția
# importată (ultima definiție a numelui câștigă), fără nicio eroare. De aceea
# `import webtools` + `webtools.get_title()` e mai sigur în proiecte mari.


def main():
    # Ex. 48: URL-ul vine din linia de comandă, nu din BASE_URL
    parser = argparse.ArgumentParser(description="Analizează un site web.")
    parser.add_argument("url", type=str, help="ex.: https://cybercor.org")
    args = parser.parse_args()
    url = args.url

    try:
        # Ex. 44
        response = webtools.fetch(url)
        print("Titlu:", webtools.get_title(response.text))
        print("Status:", webtools.get_status(url))
        time.sleep(1)

        # Ex. 45
        print("Titlu (from import):", get_title(response.text))
        print("Scor antete de securitate:", score_headers(security_headers(url)))
        time.sleep(1)

        # Ex. 47
        print("DEFAULT_HEADERS:", DEFAULT_HEADERS)

        # Ex. 49: raport CSV
        results = webtools.check_paths(url, ["/", "/robots.txt", "/sitemap.xml"])
        webtools.save_paths_csv(results, "report.csv")
        print("Rezultate salvate în report.csv:", results)
        time.sleep(1)

        # Ex. 50: raportul complet al site-ului
        print("\n=== Raport site ===")
        webtools.site_report(url)
    except requests.RequestException as error:
        print("Nu am putut accesa site-ul:", error)


if __name__ == "__main__":
    main()
