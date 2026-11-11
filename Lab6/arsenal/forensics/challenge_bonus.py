"""arsenal/forensics/challenge_bonus.py

Bonus ("pentru vârful sălii"): probe/challenge.bin combină un strat de
encoding (base64) peste un XOR cu cheie de un octet. Spre deosebire de
sparge_xor() din decode.py (care alege candidatul ce SEAMĂNĂ cel mai mult
cu text normal), aici avem ceva mai bun: un hash de verificat
(probe/challenge_hash.txt), deci alegem candidatul al cărui SHA-256 se
potrivește exact, fără ghiceli.

Rulare: python -m arsenal.forensics.challenge_bonus
"""

import hashlib
import os

from arsenal.forensics.decode import desfa

PROBE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "probe")


def rezolva():
    cale_challenge = os.path.join(PROBE_DIR, "challenge.bin")
    cale_hash = os.path.join(PROBE_DIR, "challenge_hash.txt")

    val = open(cale_challenge).read().strip()
    strat, date = desfa(val)  # primul strat: base64
    print("strat exterior desfacut:", strat)

    hash_tinta = open(cale_hash).read().strip()
    print("hash de verificat:", hash_tinta)

    for cheie in range(256):
        candidat = bytes(b ^ cheie for b in date)
        if hashlib.sha256(candidat).hexdigest() == hash_tinta:
            print(f"cheie XOR gasita: {cheie}")
            print("flag:", candidat.decode())
            return cheie, candidat.decode()

    print("Nicio cheie nu produce hash-ul asteptat.")
    return None


if __name__ == "__main__":
    rezolva()
