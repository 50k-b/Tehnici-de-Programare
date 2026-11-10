from dataclasses import dataclass, asdict
import json
import argparse

CAI_SUSPECTE = ("\\Temp\\", "\\Roaming\\")
SUSPECTE_ID = {4625, 1102, 7045}

@dataclass
class Proces:
    pid: int
    nume: str
    user: str
    cale: str
    
    def e_suspect(self):
        # TODO rezolvat (A2): True dacă una din CAI_SUSPECTE este în self.cale
        return any(c in self.cale for c in CAI_SUSPECTE)

@dataclass
class Eveniment:
    id: int
    nivel: str
    sursa: str
    cont: str
    mesaj: str
    
    def e_suspect(self):
        # TODO rezolvat (A3): True dacă self.id în SUSPECTE_ID SAU self.nivel == "critical"
        return self.id in SUSPECTE_ID or self.nivel.lower() == "critical"

def procese_din_json(cale):
    with open(cale, encoding="utf-8") as f:
        # TODO rezolvat (A4): intoarce lista de obiecte Proces
        return [Proces(**d) for d in json.load(f)]

def evenimente_din_json(cale):
    with open(cale, encoding="utf-8") as f:
        return [Eveniment(**d) for d in json.load(f)]

@dataclass
class Inventar:
    procese: list
    
    @classmethod
    def din_json(cls, cale):
        with open(cale, encoding="utf-8") as f:
            # TODO rezolvat (B1): returnează instanța cls cu procesele mapate
            return cls([Proces(**d) for d in json.load(f)])
            
    def __len__(self):
        return len(self.procese)
    
    def suspecte(self):
        # TODO rezolvat (B2): lista proceselor cu p.e_suspect()
        return [p for p in self.procese if p.e_suspect()]
    
    def pe_user(self):
        # TODO rezolvat (B2): dict user -> lista de nume folosind setdefault
        rez = {}
        for p in self.procese:
            rez.setdefault(p.user, []).append(p.nume)
        return rez

def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("capturi")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    
    inv = Inventar.din_json(a.capturi + "/procese.json")
    ev = evenimente_din_json(a.capturi + "/evenimente.json")
    alarma = [e for e in ev if e.e_suspect()]
    
    # TODO rezolvat (B3): gestionarea parametru --json vs afișare simplă
    if a.json:
        raport = {
            "suspecte": [asdict(p) for p in inv.suspecte()],
            "alarma": [asdict(e) for e in alarma]
        }
        print(json.dumps(raport, indent=4, ensure_ascii=False))
    else:
        print(f"Procese: {len(inv)} | suspecte: {len(inv.suspecte())}")
        for p in inv.suspecte():
            print(f"  [{p.pid}] {p.nume}  ({p.user})  {p.cale}")
        print(f"Evenimente: {len(ev)} | alarma: {len(alarma)}")
        for e in alarma:
            print(f"  {e.id} [{e.nivel}] {e.cont}: {e.mesaj}")

if __name__ == "__main__":
    main()
