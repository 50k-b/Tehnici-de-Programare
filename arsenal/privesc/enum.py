import argparse
import json
import os
import sys

GTFO = {
    "find",
    "vim.basic",
    "vim",
    "nmap",
    "cp",
    "bash",
    "less",
    "awk",
    "python3",
    "perl",
}

# Directoare în care poate scrie oricine: o comandă din ele e riscantă.
DIRECTOARE_SCRIPTABILE = ("/tmp/", "/var/tmp/", "/dev/shm/")


def citeste_linii(cale):
  """Citește liniile dintr-un fișier, eliminând spațiile goale,

  liniile goale și comentariile (care încep cu #).
  """
  with open(cale, encoding="utf-8") as f:
    return [
        linie.strip()
        for linie in f
        if linie.strip() and not linie.strip().startswith("#")
    ]


def nume(cale):
  """Întoarce numele fișierului (ceea ce se află după ultimul '/')."""
  return cale.rsplit("/", 1)[-1]


def suid_constatari(cale):
  """Construiește o listă de dicționare sortată și unică pentru fișierele SUID."""
  # Mulțimea păstrează căile unice, apoi sortăm.
  cai_unice = sorted(set(citeste_linii(cale)))
  out = []
  for c in cai_unice:
    n = nume(c)
    out.append({
        "cale": c,
        "nume": n,
        "risc": "mare" if n in GTFO else "normal",
    })
  return out


def sudo_constatari(cale):
  """Analizează drepturile sudo din fișier."""
  out = []
  for ln in citeste_linii(cale):
    if " : " not in ln:
      print(f"avertisment: linie sudo ignorata (fara ' : '): {ln}",
            file=sys.stderr)
      continue
    user, drept = ln.split(" : ", 1)  # despachetare în tuplu
    out.append({
        "user": user.strip(),
        "drept": drept.strip(),
        "risc": "mare" if "NOPASSWD" in drept else "normal",
    })
  return out


def cron_constatari(cale):
  """Analizează sarcinile programate din crontab."""
  out = []
  for ln in citeste_linii(cale):
    campuri = ln.split()
    if len(campuri) >= 7:
      user = campuri[5]
      comanda = " ".join(campuri[6:])
      scriptabil = any(d in comanda for d in DIRECTOARE_SCRIPTABILE)
      out.append({
          "user": user,
          "comanda": comanda,
          "risc": "mare" if scriptabil else "normal",
      })
  return out


def citeste_sigur(functie, cale):
  """Rulează funcția de analiză; dacă fișierul lipsește, întoarce o listă goală."""
  try:
    return functie(cale)
  except FileNotFoundError:
    print(f"avertisment: lipseste fisierul {cale}", file=sys.stderr)
    return []


def enumereaza(d):
  """Grupează toate constatările într-un dicționar central."""
  return {
      "suid": citeste_sigur(suid_constatari, os.path.join(d, "suid.txt")),
      "sudo": citeste_sigur(sudo_constatari, os.path.join(d, "sudo.txt")),
      "cron": citeste_sigur(cron_constatari, os.path.join(d, "crontab.txt")),
  }


def main():
  p = argparse.ArgumentParser()
  p.add_argument("capturi")
  p.add_argument("--json", action="store_true")
  a = p.parse_args()

  raport = enumereaza(a.capturi)

  if a.json:
    print(json.dumps(raport, indent=2, ensure_ascii=False))
    return

  for categorie, lista in raport.items():
    mari = [c for c in lista if c.get("risc") == "mare"]
    print(f"{categorie}: {len(lista)} gasite, {len(mari)} cu risc mare")

  # Utilizatorii implicați: reuniunea mulțimilor de useri din sudo și cron.
  useri_sudo = {item["user"] for item in raport["sudo"]}
  useri_cron = {item["user"] for item in raport["cron"]}
  utilizatori_implicati = sorted(useri_sudo | useri_cron)
  print(f"utilizatori implicati: {', '.join(utilizatori_implicati)}")

  with open("enum.json", "w", encoding="utf-8") as f:
    json.dump(raport, f, indent=2, ensure_ascii=False)
  print("Raport salvat in enum.json")


if __name__ == "__main__":
  main()
