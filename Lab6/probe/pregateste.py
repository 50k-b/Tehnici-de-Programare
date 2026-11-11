"""probe/pregateste.py

Generează fișierele pe care le analizați în Laboratorul 6:
  - probe/mesaj.txt     un șir codat (base64) peste text citibil
  - probe/xor.bin       un mesaj criptat XOR cu o cheie de un octet
  - probe/wordlist.txt  o listă mică de cuvinte (codare latin1)
  - probe/hashuri.txt   hash-urile (md5/sha1/sha256) ale unei parole din listă
  - probe/foto.jpg      o poză cu EXIF și coordonate GPS
  - probe/ascuns.png    o poză cu o arhivă ZIP lipită la coadă
  - probe/challenge.bin bonus: encoding + XOR, pentru "pentru vârful sălii"

Rulare: python probe/pregateste.py
Se rulează o singură dată, din rădăcina proiectului (vede folderul probe/).
"""

import base64
import hashlib
import io
import os
import zipfile

from PIL import Image
from PIL.TiffImagePlugin import IFDRational

PROBE_DIR = os.path.join(os.path.dirname(__file__))


def scrie(nume, continut, mod="w", **kwargs):
    cale = os.path.join(PROBE_DIR, nume)
    with open(cale, mod, **kwargs) as f:
        f.write(continut)
    return cale


# --------------------------------------------------------------------------
# mesaj.txt: un singur strat (base64) peste text cu spatii
# --------------------------------------------------------------------------
def genereaza_mesaj():
    # Un singur strat (base64) peste text cu spatii: suficient ca sa se vada
    # ca decodeaza_complet() se opreste corect cand textul devine citibil.
    # (Inlantuirea a doua codari text-spre-text, de ex. hex apoi base64, nu
    # functioneaza cu verificarea simpla citibil(): rezultatul intermediar -
    # chiar fiind tot o codare - e deja compus din caractere printabile, deci
    # bucla s-ar opri prea devreme, inainte de ultimul strat.)
    secret = "parola e sub covorul din hol, nu o spune nimanui"
    scrie("mesaj.txt", base64.b64encode(secret.encode()).decode())


# --------------------------------------------------------------------------
# xor.bin: text criptat cu XOR pe un octet
# --------------------------------------------------------------------------
XOR_KEY = 0x5A
XOR_MESAJ = b"Felicitari, ati spart XOR-ul cu un octet!"


def genereaza_xor():
    date = bytes(b ^ XOR_KEY for b in XOR_MESAJ)
    scrie("xor.bin", date, mod="wb")


# --------------------------------------------------------------------------
# wordlist.txt + hashuri.txt
# --------------------------------------------------------------------------
WORDLIST = [
    "parola123",
    "admin",
    "iloveyou",
    "cybercor",
    "qwerty",
    "student2026",
    "laborator6",
    "soare123",
]
PAROLA_SECRETA = "cybercor"


def genereaza_hashuri():
    with open(os.path.join(PROBE_DIR, "wordlist.txt"), "w", encoding="latin1") as f:
        f.write("\n".join(WORDLIST) + "\n")

    parola = PAROLA_SECRETA.encode()
    linii = [
        hashlib.md5(parola).hexdigest(),
        hashlib.sha1(parola).hexdigest(),
        hashlib.sha256(parola).hexdigest(),
    ]
    scrie("hashuri.txt", "\n".join(linii) + "\n")


# --------------------------------------------------------------------------
# foto.jpg: imagine cu EXIF și GPS (Chișinău, aproximativ)
# --------------------------------------------------------------------------
def grade_in_dms(valoare):
    """Transformă grade zecimale în tuplul (grade, minute, secunde),
    în formatul așteptat de tag-ul GPS EXIF (fracții IFDRational)."""
    grade = int(valoare)
    minute_float = (valoare - grade) * 60
    minute = int(minute_float)
    secunde = (minute_float - minute) * 60
    return (
        IFDRational(grade, 1),
        IFDRational(minute, 1),
        IFDRational(int(round(secunde * 100)), 100),
    )


def genereaza_foto():
    img = Image.new("RGB", (640, 480), color=(90, 130, 170))

    exif = img.getexif()
    exif[0x010F] = "WebLab"              # Make
    exif[0x0110] = "Camera Laborator"    # Model
    exif[0x0132] = "2026:11:10 12:00:00"  # DateTime

    gps_ifd = exif.get_ifd(0x8825)  # 0x8825 = GPSInfo IFD
    gps_ifd[1] = "N"                       # emisfera latitudine
    gps_ifd[2] = grade_in_dms(47.0245)     # latitudine (Chisinau)
    gps_ifd[3] = "E"                       # emisfera longitudine
    gps_ifd[4] = grade_in_dms(28.8322)     # longitudine

    img.save(os.path.join(PROBE_DIR, "foto.jpg"), exif=exif)


# --------------------------------------------------------------------------
# ascuns.png: o poză normală + o arhivă ZIP lipită la coadă
# --------------------------------------------------------------------------
def genereaza_ascuns():
    imagine = Image.new("RGB", (200, 150), color=(200, 200, 200))
    buf = io.BytesIO()
    imagine.save(buf, format="PNG")
    png_bytes = buf.getvalue()

    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w") as zf:
        zf.writestr(
            "secret.txt",
            "Ati gasit arhiva ascunsa cu file carving! Felicitari.\n",
        )
    zip_bytes = zip_buf.getvalue()

    with open(os.path.join(PROBE_DIR, "ascuns.png"), "wb") as f:
        f.write(png_bytes + zip_bytes)


# --------------------------------------------------------------------------
# challenge.bin (bonus, "pentru vârful sălii"): encoding peste XOR
# --------------------------------------------------------------------------
CHALLENGE_KEY = 0x2A
CHALLENGE_FLAG = b"FLAG{forensics_e_usor_cand_stii_pasii}"


def genereaza_challenge():
    xorat = bytes(b ^ CHALLENGE_KEY for b in CHALLENGE_FLAG)
    strat_final = base64.b64encode(xorat)
    scrie("challenge.bin", strat_final, mod="wb")
    # Hash-ul flagului, ca sa poata fi verificata solutia gasita.
    scrie(
        "challenge_hash.txt",
        hashlib.sha256(CHALLENGE_FLAG).hexdigest() + "\n",
    )


def main():
    os.makedirs(PROBE_DIR, exist_ok=True)
    genereaza_mesaj()
    genereaza_xor()
    genereaza_hashuri()
    genereaza_foto()
    genereaza_ascuns()
    genereaza_challenge()
    print("Fisiere probe generate in", PROBE_DIR)
    for nume in sorted(os.listdir(PROBE_DIR)):
        if nume != os.path.basename(__file__):
            print(" -", nume)


if __name__ == "__main__":
    main()
