"""stego.py

Lucrarea B (B5-B6): ascunde și dezvăluie un mesaj în ultimii biți ai
pixelilor unei imagini (steganografie LSB - Least Significant Bit).

Rulare:
    python stego.py ascunde probe/foto.jpg stego.png "mesaj secret"
    python stego.py dezvaluie stego.png
"""

import argparse

from PIL import Image

TERMINATOR = b"\x00"  # marcheaza finalul mesajului in fluxul de biti


# --------------------------------------------------------------------------
# B5. Ascunzi un mesaj prin LSB
# --------------------------------------------------------------------------
def ascunde_mesaj(cale_gazda: str, mesaj: bytes, cale_iesire: str = "stego.png") -> None:
    """Scrie `mesaj` (+ un octet 0x00 de final) în ultimul bit al fiecărui
    canal de culoare din imaginea `cale_gazda`, și salvează în `cale_iesire`.

    Imaginea rezultată arată identic cu ochiul liber, pentru că schimbăm cel
    mult cu 1 fiecare valoare de culoare (0-255).
    """
    img = Image.open(cale_gazda).convert("RGB")
    pixeli = list(img.getdata())

    date = mesaj + TERMINATOR
    biti = "".join(f"{octet:08b}" for octet in date)

    if len(biti) > len(pixeli) * 3:
        raise ValueError("Mesajul e prea lung pentru aceasta imagine.")

    pixeli_noi = []
    index_bit = 0
    for (r, g, b) in pixeli:
        canale = [r, g, b]
        for i in range(3):
            if index_bit < len(biti):
                bit = int(biti[index_bit])
                canale[i] = (canale[i] & ~1) | bit
                index_bit += 1
        pixeli_noi.append(tuple(canale))

    img.putdata(pixeli_noi)
    img.save(cale_iesire)  # PNG: fara pierdere, altfel biții se distrug


# --------------------------------------------------------------------------
# B6. Dezvălui mesajul înapoi
# --------------------------------------------------------------------------
def dezvaluie_mesaj(cale_stego: str) -> bytes:
    """Citește ultimul bit al fiecărui canal din `cale_stego`, regrupează
    câte 8 biți și reconstituie mesajul, oprindu-se la primul octet 0x00."""
    pixeli = list(Image.open(cale_stego).convert("RGB").getdata())

    biti = []
    for (r, g, b) in pixeli:
        biti.append(r & 1)
        biti.append(g & 1)
        biti.append(b & 1)

    octeti = bytearray()
    for i in range(0, len(biti) - 7, 8):
        valoare = 0
        for bit in biti[i:i + 8]:
            valoare = (valoare << 1) | bit
        if valoare == 0:  # am ajuns la terminator
            break
        octeti.append(valoare)

    return bytes(octeti)


def main():
    parser = argparse.ArgumentParser(description="Ascunde sau dezvaluie un mesaj prin steganografie LSB.")
    subparsers = parser.add_subparsers(dest="comanda", required=True)

    p_ascunde = subparsers.add_parser("ascunde")
    p_ascunde.add_argument("gazda", help="poza in care se ascunde mesajul")
    p_ascunde.add_argument("iesire", help="unde se salveaza poza cu mesaj (.png)")
    p_ascunde.add_argument("mesaj", help="textul de ascuns")

    p_dezvaluie = subparsers.add_parser("dezvaluie")
    p_dezvaluie.add_argument("stego", help="poza din care se extrage mesajul")

    args = parser.parse_args()

    if args.comanda == "ascunde":
        ascunde_mesaj(args.gazda, args.mesaj.encode(), args.iesire)
        print(f"Mesaj ascuns in {args.iesire}")
    else:
        mesaj = dezvaluie_mesaj(args.stego)
        print("Mesaj gasit:", mesaj.decode(errors="replace"))


if __name__ == "__main__":
    main()
