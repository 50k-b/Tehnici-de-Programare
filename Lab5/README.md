# Laborator Python: funcții, metode și importuri pe web

Lucrarea de laborator nr. 5, disciplina **Tehnici de programare**
(Universitatea Tehnică a Moldovei, FCIM, gr. SI-262).

Programe Python care comunică cu un site web real și exersează trei concepte:
**importuri**, **metode** și **funcții**. La final există un modul propriu,
`webtools.py`, care generează un raport despre un site.

## Structură

| Fișier | Conținut |
| --- | --- |
| `part1_imports.py` | Ex. 1-8: importuri (`import`, `from`, alias, `urllib`, `try/except ImportError`) |
| `part2_methods.py` | Ex. 9-20: metode și atribute (`response`, headere, cookie-uri, `Session`) |
| `part3_functions.py` | Ex. 21-34: funcții proprii (parametri impliciți, `*args`, `**kwargs`, type hints) |
| `part4_modules.py` | Ex. 35-43: `urllib.parse`, `re`, `html.parser`, `hashlib`, `json`, `socket`, `ssl` |
| `webtools.py` | Ex. 44-50: modulul propriu (`site_report`, raport CSV/JSON, bonus BeautifulSoup) |
| `main.py` | Ex. 44-50: linia de comandă cu `argparse` |

## Instalare

```bash
python --version          # 3.9 sau mai nou
pip install -r requirements.txt
```

## Rulare

```bash
python part1_imports.py
python part2_methods.py
python part3_functions.py
python part4_modules.py
python webtools.py                      # autotest (fără rețea)
python main.py https://cybercor.org     # raport complet, scrie report.csv și report.json
```

## Reguli de lucru respectate

- fiecare cerere are `timeout`;
- pauză de 1 secundă (`time.sleep(1)`) între cereri;
- către `cybercor.org` se trimit doar cereri `GET` și `HEAD`; cererea cu antet personalizat merge către `httpbin.org`;
- nu există bucle infinite care trimit cereri;
- se accesează doar URL-urile din exerciții.
