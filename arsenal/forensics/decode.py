import argparse
import base64
import hashlib
import json
import re
from urllib.parse import unquote


def ghici_strat(s):
  if re.search(r"%[0-9A-Fa-f]{2}", s):
    return "url"
  if len(s) % 2 == 0 and re.fullmatch(r"[0-9A-Fa-f]+", s):
    return "hex"
  if re.fullmatch(r"[A-Za-z0-9+/=]+", s) and len(s) % 4 == 0:
    return "base64"
  return "necunoscut"


def desfa(s):
  strat = ghici_strat(s)
  if strat == "base64":
    try:
      return strat, base64.b64decode(s)
    except:
      pass
  elif strat == "hex":
    try:
      return strat, bytes.fromhex(s)
    except:
      pass
  elif strat == "url":
    try:
      return strat, unquote(s).encode("utf-8")
    except:
      pass
  return "necunoscut", s.encode("utf-8")


def citibil(b):
  return all(32 <= c < 127 for c in b)


if __name__ == "__main__":
  p = argparse.ArgumentParser()
  p.add_argument("intrare")
  p.add_argument("--fisier", action="store_true")
  a = p.parse_args()

  if a.fisier:
    val = open(a.intrare, "rb").read().decode("utf-8", errors="ignore").strip()
  else:
    val = a.intrare

  strat_final = "necunoscut"
  rezultat_final = val

  for _ in range(8):
    strat, b = desfa(val)
    if citibil(b):
      strat_final = strat
      rezultat_final = b.decode("utf-8", errors="ignore")
      break
    else:
      try:
        val = b.decode("utf-8")
      except:
        break

  fisa = {"strat": strat_final, "rezultat": rezultat_final}
  with open("arsenal/forensics/fisa.json", "w", encoding="utf-8") as f:
    json.dump(fisa, f, indent=4)

  print("Gata! Rezultat:", fisa)
