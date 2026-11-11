# Laborator 6 — Informații invizibile: forensics și steganografie

## Lucrarea A — decoderul universal (`arsenal/forensics/decode.py`)

- **Mesajul din `probe/mesaj.txt`** era codat pe un singur strat, base64.
  Decodat, textul era: `parola e sub covorul din hol, nu o spune nimanui`.
- **XOR-ul din `probe/xor.bin`**: cheia găsită prin forță brută (cele 256
  valori posibile) a fost **90 (0x5A)**, iar textul clar a fost:
  `Felicitari, ati spart XOR-ul cu un octet!`.
- **Hash-ul din `probe/hashuri.txt`**: primul hash (MD5, 32 caractere) a
  fost spart prin dicționar (`probe/wordlist.txt`, citit cu `latin1`);
  parola găsită a fost **`cybercor`**. Aceeași parolă a fost verificată și
  pentru hash-urile SHA-1 și SHA-256 din fișier.
- Rulare: `python arsenal/forensics/decode.py "<sir>"` sau cu `--fisier`
  pentru o cale. Rezultatul se salvează automat în `arsenal/forensics/fisa.json`.
- Testul din `teste/test_decode.py` trece (`pytest -q`).

### Bonus — `probe/challenge.bin`

Combina un strat base64 peste un XOR cu cheie de un octet. Pentru că
forța brută pe XOR poate da mai multe rezultate "citibile" fals-pozitive,
am verificat fiecare candidat cu hash-ul din `probe/challenge_hash.txt`
(SHA-256). Cheia corectă a fost **42**, iar flagul găsit:
`FLAG{forensics_e_usor_cand_stii_pasii}` (`arsenal/forensics/challenge_bonus.py`).

## Lucrarea B — forensics pe fișiere și mesaj ascuns

- **Tipul real al fișierelor** (`forensics.py`, B1): `probe/foto.jpg` are
  semnătura JPEG (`\xff\xd8`), iar `probe/ascuns.png` are semnătura PNG
  (`\x89PNG`) — ambele corespund extensiei, dar verificarea s-a făcut pe
  conținut, nu pe nume.
- **`strings` pe `probe/ascuns.png`** (B2) a scos la iveală, printre
  blocurile PNG normale (`IHDR`, `IDATx`, `IEND`), și numele fișierului
  `secret.txt` și mesajul din arhiva lipită la coadă — un indiciu clar că
  mai e ceva după datele PNG.
- **Metadatele EXIF/GPS din `probe/foto.jpg`** (B3): `Make`, `Model` și
  `DateTime` arată ca niște date de cameră obișnuite; blocul GPS (tag
  `34853`) a dat coordonatele **47.024500, 28.832200** — zona Chișinău.
  De aici se vede clar de ce merită să ștergi EXIF-ul înainte să publici o
  poză: coordonatele exacte unde a fost făcută sunt expuse oricui se uită.
- **Arhiva ascunsă din `probe/ascuns.png`** (B4, file carving): semnătura
  ZIP (`PK\x03\x04`) a fost găsită la octetul **465**. Extrasă în
  `gasit.zip`, arhiva conținea `secret.txt`, cu textul:
  „Ati gasit arhiva ascunsa cu file carving! Felicitari.”
- **Mesajul ascuns prin LSB** (B5-B6, `stego.py`): am ascuns textul
  `FLAG{ascuns_in_pixeli}` în ultimul bit al fiecărui canal de culoare din
  `probe/foto.jpg`, salvat ca `stego.png` (fără pierdere — un `.jpg` ar fi
  distrus biții ascunși la recompresie). Dezvăluirea (citirea acelorași
  biți, regrupați câte 8) a reconstituit exact același mesaj.

## Concluzii

Am exersat diferența text/octeți, recunoașterea și desfacerea codărilor
textuale (base64/hex/URL), spargerea prin forță brută (XOR pe un octet) și
prin dicționar (hash de parolă), construirea unei interfețe `argparse` cu
opțiuni poziționale și `--fisier`, și salvarea rezultatelor ca JSON. În
Lucrarea B am aplicat aceleași principii pe fișiere binare reale: citirea
semnăturii (magic bytes) în loc de a avea încredere în extensie, extragerea
textului ascuns cu `strings`, metadatele EXIF/GPS (și riscul lor pentru
confidențialitate), file carving pentru un fișier lipit la coadă, și
steganografia LSB, în ambele sensuri (ascundere și dezvăluire).

Am lucrat exclusiv pe fișierele generate de `probe/pregateste.py`, conform
cadrului legal al laboratorului.
