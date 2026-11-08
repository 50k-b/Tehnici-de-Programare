import os
import tempfile
import unittest

from arsenal.privesc import enum as enumerare


def scrie(folder, nume_fisier, text):
  cale = os.path.join(folder, nume_fisier)
  with open(cale, "w", encoding="utf-8") as f:
    f.write(text)
  return cale


class TesteEnumerare(unittest.TestCase):

  def setUp(self):
    self.tmp = tempfile.TemporaryDirectory()
    self.d = self.tmp.name

  def tearDown(self):
    self.tmp.cleanup()

  def test_citeste_linii_ignora_goale_si_comentarii(self):
    cale = scrie(self.d, "x.txt", "# comentariu\n\n  a  \nb\n")
    self.assertEqual(enumerare.citeste_linii(cale), ["a", "b"])

  def test_nume_ia_ce_e_dupa_ultimul_slash(self):
    self.assertEqual(enumerare.nume("/usr/bin/find"), "find")

  def test_suid_unic_sortat_si_risc(self):
    cale = scrie(self.d, "suid.txt",
                 "/usr/bin/vim\n/usr/bin/passwd\n/usr/bin/vim\n")
    rez = enumerare.suid_constatari(cale)
    self.assertEqual([r["cale"] for r in rez],
                     ["/usr/bin/passwd", "/usr/bin/vim"])
    self.assertEqual([r["risc"] for r in rez], ["normal", "mare"])

  def test_sudo_nopasswd_este_risc_mare(self):
    cale = scrie(self.d, "sudo.txt",
                 "alice : (ALL) NOPASSWD: /bin/vim\nbob : (ALL) /usr/bin/apt\n")
    rez = enumerare.sudo_constatari(cale)
    self.assertEqual(rez[0]["risc"], "mare")
    self.assertEqual(rez[1]["risc"], "normal")
    self.assertEqual(rez[0]["user"], "alice")

  def test_sudo_linie_gresita_este_ignorata(self):
    cale = scrie(self.d, "sudo.txt",
                 "alice NOPASSWD ALL\nbob : (ALL) /usr/bin/apt\n")
    rez = enumerare.sudo_constatari(cale)
    self.assertEqual([r["user"] for r in rez], ["bob"])

  def test_cron_user_comanda_si_risc(self):
    cale = scrie(self.d, "crontab.txt",
                 "*/5 * * * * root /opt/backup.sh\n"
                 "0 3 * * * www-data /tmp/job.sh --fast\n"
                 "linie scurta\n")
    rez = enumerare.cron_constatari(cale)
    self.assertEqual(len(rez), 2)
    self.assertEqual(rez[0]["user"], "root")
    self.assertEqual(rez[0]["risc"], "normal")
    self.assertEqual(rez[1]["comanda"], "/tmp/job.sh --fast")
    self.assertEqual(rez[1]["risc"], "mare")

  def test_fisier_lipsa_da_lista_goala(self):
    rez = enumerare.citeste_sigur(enumerare.cron_constatari,
                                  os.path.join(self.d, "nu_exista.txt"))
    self.assertEqual(rez, [])

  def test_enumereaza_are_toate_cheile(self):
    scrie(self.d, "suid.txt", "/usr/bin/find\n")
    scrie(self.d, "sudo.txt", "alice : (ALL) ALL\n")
    scrie(self.d, "crontab.txt", "0 3 * * * root /opt/x.sh\n")
    rez = enumerare.enumereaza(self.d)
    self.assertEqual(set(rez), {"suid", "sudo", "cron"})
    self.assertEqual(rez["suid"][0]["risc"], "mare")


if __name__ == "__main__":
  unittest.main()
