"""forensics.py

Lucrarea B (B1-B4): citești ce spun fișierele despre ele, dincolo de
extensie - semnătura reală (magic bytes), textul ascuns în binar (strings),
metadatele EXIF/GPS dintr-o poză, și un fișier lipit la coadă (file carving).

Rulare: python forensics.py
(implicit analizează fișierele din probe/; rulați mai întâi
python probe/pregateste.py dacă acel folder e gol)
"""

import os
import re

from PIL import Image
from PIL.ExifTags import GPSTAGS, TAGS

PROBE_DIR = "probe"

# --------------------------------------------------------------------------
# B1. Magic bytes: tipul real, nu extensia
# --------------------------------------------------------------------------
SEMNATURI = {
    b"%PDF": "pdf",
    b"\x89PNG": "png",
    b"\xff\xd8": "jpeg",
    b"PK\x03\x04": "zip/docx",
}


def tip_real(cale: str) -> str:
    """Citește primii octeți din `cale` și-i compară cu semnături cunoscute.

    Returnează numele tipului găsit, sau hexul primilor octeți dacă nu
    recunoaște semnătura (ca să poți căuta manual ce e).
    """
    cap = open(cale, "rb").read(8)
    for semnatura, nume in SEMNATURI.items():
        if cap.startswith(semnatura):
            return nume
    return cap.hex()


# --------------------------------------------------------------------------
# B2. strings: textul citibil dintr-un binar
# --------------------------------------------------------------------------
def strings_din_fisier(cale: str, lungime_minima: int = 4) -> list:
    """Returnează toate secvențele de caractere printabile (lungime >= `lungime_minima`)
    găsite în fișierul binar `cale`, ca listă de șiruri."""
    date = open(cale, "rb").read()
    tipar = re.compile(rb"[ -~]{%d,}" % lungime_minima)
    return [m.decode() for m in tipar.findall(date)]


# --------------------------------------------------------------------------
# B3. Metadate EXIF și GPS din poză
# --------------------------------------------------------------------------
def citeste_exif(cale: str) -> dict:
    """Returnează un dicționar {nume_tag: valoare} din EXIF-ul pozei `cale`."""
    exif = Image.open(cale).getexif()
    return {TAGS.get(tag_id, tag_id): valoare for tag_id, valoare in exif.items()}


def _dms_in_zecimal(dms, emisfera: str) -> float:
    """Transformă (grade, minute, secunde) + emisferă în grade zecimale."""
    grade, minute, secunde = dms
    valoare = float(grade) + float(minute) / 60 + float(secunde) / 3600
    if emisfera in ("S", "W"):
        valoare = -valoare
    return valoare


def citeste_gps(cale: str):
    """Extrage latitudinea și longitudinea (grade zecimale) din EXIF-ul `cale`.

    Returnează (lat, lon), sau None dacă poza nu are bloc GPS (tag 34853).
    """
    exif = Image.open(cale).getexif()
    gps_ifd = exif.get_ifd(0x8825)  # 34853 = GPSInfo
    if not gps_ifd:
        return None

    gps = {GPSTAGS.get(tag_id, tag_id): valoare for tag_id, valoare in gps_ifd.items()}
    lat = _dms_in_zecimal(gps["GPSLatitude"], gps["GPSLatitudeRef"])
    lon = _dms_in_zecimal(gps["GPSLongitude"], gps["GPSLongitudeRef"])
    return lat, lon


# --------------------------------------------------------------------------
# B4. File carving: scoți fișierul ascuns
# --------------------------------------------------------------------------
def extrage_fisier_ascuns(cale: str, semnatura: bytes = b"PK\x03\x04", iesire: str = "gasit.zip"):
    """Caută `semnatura` în fișierul `cale` și salvează tot ce urmează, în `iesire`.

    Returnează octetul la care a fost găsită semnătura, sau None dacă lipsește.
    """
    date = open(cale, "rb").read()
    i = date.find(semnatura)
    if i == -1:
        return None
    with open(iesire, "wb") as f:
        f.write(date[i:])
    return i


def demo():
    foto = os.path.join(PROBE_DIR, "foto.jpg")
    ascuns = os.path.join(PROBE_DIR, "ascuns.png")

    print("=== B1. Magic bytes ===")
    print("foto.jpg  ->", tip_real(foto))
    print("ascuns.png ->", tip_real(ascuns))

    print("\n=== B2. strings ===")
    for s in strings_din_fisier(ascuns):
        print(" ", s)

    print("\n=== B3. EXIF si GPS ===")
    for nume, valoare in citeste_exif(foto).items():
        print(f"  {nume} = {valoare}")
    gps = citeste_gps(foto)
    if gps:
        print(f"  Coordonate: {gps[0]:.6f}, {gps[1]:.6f}")
    else:
        print("  Fara date GPS in aceasta poza.")

    print("\n=== B4. File carving ===")
    cale_iesire = "gasit.zip"
    offset = extrage_fisier_ascuns(ascuns, iesire=cale_iesire)
    if offset is not None:
        print(f"  Arhiva gasita la octetul {offset}, salvata in {cale_iesire}")
        import zipfile

        with zipfile.ZipFile(cale_iesire) as zf:
            print("  Continut arhiva:", zf.namelist())
            for nume in zf.namelist():
                print(f"  --- {nume} ---")
                print(" ", zf.read(nume).decode().strip())
    else:
        print("  Nicio arhiva ascunsa gasita.")


if __name__ == "__main__":
    demo()
