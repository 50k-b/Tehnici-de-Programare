# Raport - Laboratorul 6: Informații invizibile, forensics și steganografie

## Lucrarea A: Decoderul Universal (`arsenal/forensics/decode.py`)
- **Recunoașterea straturilor (`ghici_strat`):** Scriptul identifică automat tipul de codare analizând formatul șirului (URL encoding cu `%xx`, Hexazecimal cu lungime pară, sau Base64 pe baza alfabetului specific).
- **Decodarea recursivă (`desfa` și bucla de straturi):** Programul decodifică șirurile strat cu strat până la obținerea unui text ASCII citibil (`citibil()`), salvând rezultatul final în `arsenal/forensics/fisa.json`.
- **Testarea automată:** Funcționalitatea de decodare Base64 este validată complet prin testul automat din `teste/test_decode.py`.

## Lucrarea B: Forensics pe fișiere și steganografie (`forensics.py`)
- **Magic bytes (`tip_real`):** S-a verificat semnătura binară a fișierelor analizate pentru a le determina tipul real dincolo de extensie (ex: recunoașterea antetelor pentru PNG, JPEG sau PDF).
- **Strings:** S-au extras secvențele de caractere imprimabile din fișierele binare pentru a descoperi indicii, căi sau mesaje ascunse.
- **Metadate EXIF și GPS:** S-a analizat structura EXIF a imaginii `foto.jpg` pentru a extrage informații tehnice și coordonatele GPS de geolocație.
- **File Carving:** S-a căutat semnătura fișierului ZIP (`PK\x03\x04`) la coada fișierului `ascuns.png`, reușindu-se extragerea cu succes a arhivei ascunse (`gasit.zip`).
- **Steganografie LSB (Least Significant Bit):**
  - **Ascundere:** S-a modificat cel mai puțin semnificativ bit al canalelor de culoare RGB din `foto.jpg` pentru a încorpora mesajul secret, generând imaginea identică vizual `stego.png`.
  - **Dezvăluire:** S-au extras biții LSB din `stego.png`, s-au regrupat în octeți și s-a reconstituit cu succes mesajul ascuns.

