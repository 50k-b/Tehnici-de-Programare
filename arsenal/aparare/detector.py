import argparse
import json
from collections import Counter
from arsenal.aparare.parse_auth import citeste_esecuri, pe_ip

def suspecti(counts, prag=10):
    """
    Întoarce o listă de tupluri (ip, n) cu n >= prag, sortate descrescător după n.
    Validează ca pragul să fie cel puțin 1, altfel ridică ValueError.
    """
    if prag < 1:
        raise ValueError(f"prag invalid: {prag} (cel putin 1)")
    
    # Filtrare și sortare descrescătoare după numărul de eșecuri (n)
    rezultat = [(ip, n) for ip, n in counts.items() if n >= prag]
    rezultat.sort(key=lambda x: x[1], reverse=True)
    return rezultat

def main():
    p = argparse.ArgumentParser(description="Detector de brute force din auth.log")
    p.add_argument("log", help="Calea către fișierul auth.log")
    p.add_argument("--prag", type=int, default=10, help="Pragul minim pentru suspiciune")
    p.add_argument("--json", action="store_true", help="Afișează rezultatul în format JSON")
    a = p.parse_args()
    
    esecuri = citeste_esecuri(a.log)
    counts = pe_ip(esecuri)
    
    try:
        sus = suspecti(counts, a.prag)
    except ValueError as e:
        print(e)
        return

    if a.json:
        raport = {
            "esecuri": len(esecuri),
            "pe_ip": dict(counts),
            "suspecti": sus
        }
        print(json.dumps(raport, indent=2))
    else:
        print(f"Esecuri de autentificare: {len(esecuri)}")
        for ip, n in counts.most_common():
            print(f"  {ip}: {n}")
        
        print(f"Suspecti (prag {a.prag}):")
        for ip, n in sus:
            print(f"  {ip}  ({n} incercari)  BRUTE FORCE")

if __name__ == "__main__":
    main()

