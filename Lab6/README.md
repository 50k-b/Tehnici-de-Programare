# Laborator 6: forensics și steganografie

Lucrarea de laborator nr. 6, disciplina **Tehnici de programare**
(Universitatea Tehnică a Moldovei, FCIM, gr. SI-262).

Două unelte de forensics scrise în Python:
- **Lucrarea A** — un decoder universal: recunoaște stratul unui șir
  (base64/hex/URL), îl desface, și sparge un XOR pe un octet sau un hash de
  parolă (prin dicționar).
- **Lucrarea B** — forensics pe fișiere: tipul real (magic bytes), text
  ascuns (`strings`), metadate EXIF/GPS, un fișier lipit la coadă (file
  carving) și steganografie LSB (ascundere + dezvăluire).

## Structură

| Fișier | Conținut |
| --- | --- |
| `probe/pregateste.py` | Generează toate fișierele de test în `probe/` |
| `arsenal/forensics/decode.py` | Lucrarea A (A1-A7) |
| `arsenal/forensics/challenge_bonus.py` | Bonus: `probe/challenge.bin` |
| `teste/test_decode.py` | Testul din A7 + verificări suplimentare |
| `forensics.py` | Lucrarea B, partea 1 (B1-B4) |
| `stego.py` | Lucrarea B, partea 2 (B5-B6) |
| `raport.md` | Rezultatele obținute (chei, parole, coordonate GPS, mesaj) |

## Instalare

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Rulare

```bash
# 1. genereaza fisierele de test (o singura data)
python probe/pregateste.py

# Lucrarea A
python arsenal/forensics/decode.py "$(cat probe/mesaj.txt)"
python arsenal/forensics/decode.py probe/xor.bin --fisier
python arsenal/forensics/decode.py "$(head -1 probe/hashuri.txt)"
python -m arsenal.forensics.challenge_bonus   # bonus
pytest -q

# Lucrarea B
python forensics.py
python stego.py ascunde probe/foto.jpg stego.png "mesajul meu"
python stego.py dezvaluie stego.png
```

## Cadrul legal

Toate uneltele lucrează doar pe fișierele generate de `probe/pregateste.py`
sau pe fișiere proprii. Forensics pe fișierele sau contul altcuiva, fără
acordul lui, este acces neautorizat la date (Cod penal RM, cap. XI).
