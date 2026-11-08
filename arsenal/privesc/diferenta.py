import os
from arsenal.privesc.enumerare import citeste_linii, nume, GTFO

def cai(fisier):
    """Întoarce mulțimea căilor citite dintr-un fișier SUID."""
    return set(citeste_linii(fisier))


def main():
    cale_baza = "start/baza_suid.txt"
    cale_acum = "start/suid.txt"     
    # Verificare existență fișiere în directorul curent sau ajustare cale dacă e cazul
    if not os.path.exists(cale_baza):
       cale_baza = "arsenal/privesc/start/baza_suid.txt"
       cale_acum = "arsenal/privesc/start/suid.txt"       
    baza = cai(cale_baza)
    acum = cai(cale_acum)

    print(f"baza: {len(baza)}  acum: {len(acum)}")

    # Diferența de mulțimi: ce e în 'acum' dar nu în 'baza'
    noi = acum - baza
    print(f"{len(noi)} SUID noi fata de sistemul curat")
    for c in sorted(noi):
        print(" ", c)

    # Dicționar de risc și filtrul pentru cele periculoase
    risc = {nume(c): ("mare" if nume(c) in GTFO else "normal") for c in noi}
    periculoase = [c for c in sorted(noi) if nume(c) in GTFO]

    print("periculoase NOI:", periculoase)


if __name__ == "__main__":
    main()
