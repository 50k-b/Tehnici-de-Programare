"""teste/test_decode.py

Testul din fisa (A7), plus câteva verificări suplimentare pentru
ghici_strat, bucla de decodare și spargerea XOR.

Rulare: pytest -q
"""

from arsenal.forensics.decode import citibil, desfa, ghici_strat, sparge_xor


def test_base64():
    strat, b = desfa("U2FsdXQ=")
    assert strat == "base64"
    assert b == b"Salut"


def test_ghici_strat_url():
    assert ghici_strat("%2Fetc") == "url"


def test_ghici_strat_hex():
    assert ghici_strat("48656c6c6f") == "hex"


def test_ghici_strat_necunoscut():
    assert ghici_strat("nu e codat deloc!") == "necunoscut"


def test_desfa_hex():
    strat, b = desfa("48656c6c6f")
    assert strat == "hex"
    assert b == b"Hello"


def test_citibil():
    assert citibil(b"text normal")
    assert not citibil(bytes([0, 1, 2, 255]))


def test_sparge_xor():
    cheie_adevarata = 0x5A
    mesaj = b"salut din laborator"
    date = bytes(b ^ cheie_adevarata for b in mesaj)
    rezultat = sparge_xor(date)
    assert rezultat is not None
    cheie, text = rezultat
    assert cheie == cheie_adevarata
    assert text == mesaj.decode()
