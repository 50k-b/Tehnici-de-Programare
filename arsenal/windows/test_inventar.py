from arsenal.windows.inventar import Proces, Eveniment, Inventar

def test_proces_din_temp_e_suspect():
    p = Proces(1, "x.exe", "ana", "C:\\Users\\ana\\AppData\\Local\\Temp\\x.exe")
    assert p.e_suspect() is True

def test_proces_din_windows_nu_e_suspect():
    p = Proces(2, "svchost.exe", "SYSTEM", "C:\\Windows\\System32\\svchost.exe")
    assert p.e_suspect() is False

def test_eveniment_alarma():
    e = Eveniment(4625, "warning", "Security", "administrator", "Failed login")
    assert e.e_suspect() is True
