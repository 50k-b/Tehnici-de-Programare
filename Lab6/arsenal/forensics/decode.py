"""arsenal/forensics/decode.py

Lucrarea A: decoderul universal.

Recunoaște stratul unui șir (base64, hex, URL), îl desface, decodează în
buclă straturile succesive, și sparge prin forță brută un XOR cu cheie de un
octet sau un hash de parolă (prin dicționar).

Rulare:
    python arsenal/forensics/decode.py "U2FsdXQ="
    python arsenal/forensics/decode.py probe/mesaj.txt --fisier
"""

import argparse
import base64
import hashlib
import json
import os
import re
from urllib.parse import unquote

# --------------------------------------------------------------------------
# A1. Text și octeți: încălzirea
# --------------------------------------------------------------------------
# s = "Salut"
# b = s.encode()              # bytes
# print(b, b[0])               # b"Salut" 83
# print(b.hex())                # "53616c7574"
# print(bytes.fromhex(b.hex())) # b"Salut" - am refacut bytes din hex


# --------------------------------------------------------------------------
# A2. Recunoști stratul după formă
# --------------------------------------------------------------------------
_URL_RE = re.compile(r"%[0-9A-Fa-f]{2}")
_HEX_RE = re.compile(r"^[0-9A-Fa-f]+$")
_BASE64_RE = re.compile(r"^[A-Za-z0-9+/]+=*$")


def ghici_strat(s: str) -> str:
    """Ghicește ce codare are șirul `s`, doar uitându-se la forma lui.

    Ordinea verificărilor contează: URL (are "%xx") e cel mai specific,
    apoi hex (doar 0-9a-f, lungime pară), apoi base64 (alfabet mai larg,
    deci verificat ultimul ca să nu fure șirurile hex).
    """
    if _URL_RE.search(s):
        return "url"
    if _HEX_RE.fullmatch(s) and len(s) % 2 == 0:
        return "hex"
    if _BASE64_RE.fullmatch(s) and len(s) % 4 == 0:
        return "base64"
    return "necunoscut"


# --------------------------------------------------------------------------
# A3. Desfaci stratul recunoscut
# --------------------------------------------------------------------------
def desfa(s: str):
    """Decodează `s` după stratul recunoscut de ghici_strat().

    Returnează tuplul (strat, rezultat_bytes). Pentru "necunoscut", întoarce
    șirul original, transformat direct în bytes.
    """
    strat = ghici_strat(s)
    if strat == "base64":
        return strat, base64.b64decode(s)
    if strat == "hex":
        return strat, bytes.fromhex(s)
    if strat == "url":
        return strat, unquote(s).encode()
    return "necunoscut", s.encode()


# --------------------------------------------------------------------------
# A4. Straturi multiple, într-o buclă
# --------------------------------------------------------------------------
def citibil(b: bytes) -> bool:
    """True dacă toți octeții din `b` sunt caractere ASCII imprimabile."""
    return len(b) > 0 and all(32 <= c < 127 for c in b)


def decodeaza_complet(val: str, incercari_maxime: int = 8):
    """Desface `val` strat după strat, până iese text citibil.

    Returnează (lista_straturilor_desfacute, text_final). Dacă după
    `incercari_maxime` pași tot nu e citibil, se oprește oricum (ca să nu
    intre într-o buclă infinită pe un șir care nu e deloc codat).
    """
    straturi = []
    for _ in range(incercari_maxime):
        strat, b = desfa(val)
        straturi.append(strat)
        if citibil(b) or strat == "necunoscut":
            return straturi, b.decode("utf-8", errors="replace")
        val = b.decode("utf-8", errors="replace")
    return straturi, val


# --------------------------------------------------------------------------
# A5. Spargi un XOR cu cheie de un octet
# --------------------------------------------------------------------------
def _scor_text(text: str) -> float:
    """Cât de mult seamănă `text` cu text normal (litere și spații, mai ales
    spații, care apar des în propoziții dar rar într-un XOR greșit)."""
    if not text:
        return -1.0
    litere_sau_spatiu = sum(c.isalpha() or c == " " for c in text)
    spatii = text.count(" ")
    return litere_sau_spatiu / len(text) + spatii / len(text)


def sparge_xor(date: bytes):
    """Încearcă toate cele 256 de chei XOR de un octet pe `date`.

    Mai multe chei pot da, din întâmplare, text "citibil" (octeți 32-126),
    de aceea nu ne oprim la prima potrivire: le colectăm pe toate și alegem
    candidatul care seamănă cel mai mult cu text normal (cu _scor_text).
    Returnează (cheie, text_clar), sau None dacă nicio cheie nu dă text citibil.
    """
    candidati = []
    for cheie in range(256):
        clar = bytes(b ^ cheie for b in date)
        if citibil(clar):
            candidati.append((cheie, clar.decode()))
    if not candidati:
        return None
    return max(candidati, key=lambda perechi: _scor_text(perechi[1]))


# --------------------------------------------------------------------------
# A6. Spargi un hash prin dicționar
# --------------------------------------------------------------------------
_ALGORITM_DUPA_LUNGIME = {32: "md5", 40: "sha1", 64: "sha256"}


def sparge_hash(hash_tinta: str, cale_wordlist: str):
    """Caută în `cale_wordlist` un cuvânt al cărui hash e egal cu `hash_tinta`.

    Algoritmul (md5/sha1/sha256) e ales după lungimea hash-ului țintă.
    Returnează cuvântul găsit, sau None dacă nu e în listă.
    """
    hash_tinta = hash_tinta.strip().lower()
    algoritm = _ALGORITM_DUPA_LUNGIME.get(len(hash_tinta))
    if algoritm is None:
        return None

    with open(cale_wordlist, encoding="latin1") as f:
        for linie in f:
            cuvant = linie.strip()
            if not cuvant:
                continue
            calculat = hashlib.new(algoritm, cuvant.encode()).hexdigest()
            if calculat == hash_tinta:
                return cuvant
    return None


# --------------------------------------------------------------------------
# A7. argparse, fișa JSON și un test
# --------------------------------------------------------------------------
def construieste_fisa(intrare: str, din_fisier: bool) -> dict:
    """Construiește dicționarul care se salvează în fisa.json."""
    if din_fisier:
        date = open(intrare, "rb").read()
        if citibil(date):
            val = date.decode()
            straturi, text = decodeaza_complet(val)
            return {
                "intrare": intrare,
                "tip": "fisier-text",
                "straturi": straturi,
                "rezultat": text,
            }
        xor = sparge_xor(date)
        if xor:
            cheie, text = xor
            return {
                "intrare": intrare,
                "tip": "xor-un-octet",
                "cheie": cheie,
                "rezultat": text,
            }
        return {
            "intrare": intrare,
            "tip": "fisier-binar",
            "lungime": len(date),
            "rezultat": date.hex(),
        }

    # intrarea e un sir: fie e direct un hash de spart, fie e codat in straturi
    if re.fullmatch(r"[0-9A-Fa-f]{32}|[0-9A-Fa-f]{40}|[0-9A-Fa-f]{64}", intrare):
        wordlist = os.path.join(os.path.dirname(__file__), "..", "..", "probe", "wordlist.txt")
        gasit = sparge_hash(intrare, wordlist)
        return {"intrare": intrare, "tip": "hash", "parola": gasit}

    straturi, text = decodeaza_complet(intrare)
    return {"intrare": intrare, "straturi": straturi, "rezultat": text}


def main():
    parser = argparse.ArgumentParser(
        description="Decoder universal: recunoaste si desface straturi, sparge XOR si hash-uri."
    )
    parser.add_argument("intrare", help="un sir codat, sau o cale catre un fisier")
    parser.add_argument("--fisier", action="store_true", help="trateaza 'intrare' ca o cale de fisier")
    args = parser.parse_args()

    fisa = construieste_fisa(args.intrare, args.fisier)
    print(json.dumps(fisa, indent=2, ensure_ascii=False))

    cale_fisa = os.path.join(os.path.dirname(__file__), "fisa.json")
    with open(cale_fisa, "w", encoding="utf-8") as f:
        json.dump(fisa, f, indent=2, ensure_ascii=False)
    print(f"\nFisa salvata in {cale_fisa}")


if __name__ == "__main__":
    main()
