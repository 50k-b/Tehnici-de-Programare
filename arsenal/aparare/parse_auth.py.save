import re
from collections import Counter

TIPAR = re.compile(r"Failed password for (?:invalid user )?(\S+) from (\S+) port")

def esec(linie):
    """
    Întoarce un tuplu (user, ip) dacă rândul reprezintă un eșec de autentificare, altfel None.
    """
    m = TIPAR.search(linie)
    if m is None:
        return None
    return (m.group(1), m.group(2))

def citeste_esecuri(cale):
    """
    Parcurge fișierul jurnal și strânge eșecurile într-o listă de dicționare.
    Gestionează excepția FileNotFoundError pentru a evita un traceback urât.
    """
    esecuri = []
    try:
        f = open(cale, encoding="utf-8")
    except FileNotFoundError:
        print("nu gasesc", cale)
        return esecuri
    
    with f:
        for linie in f:
            r = esec(linie)
            if r is not None:
                esecuri.append({"user": r[0], "ip": r[1]})
    return esecuri

def pe_ip(esecuri):
    """
    Întoarce un obiect Counter cu numărul de apariții pentru fiecare adresă IP.
    """
    return Counter(e["ip"] for e in esecuri)

def main():
    import sys
    cale = sys.argv[1] if len(sys.argv) > 1 else "arsenal/aparare/start/auth.log"
    esecuri = citeste_esecuri(cale)
    counts = pe_ip(esecuri)
    
    print(f"Esecuri de autentificare: {len(esecuri)}")
    for ip, n in counts.most_common():
        print(f"  {ip}: {n}")

if __name__ == "__main__":
    main()
