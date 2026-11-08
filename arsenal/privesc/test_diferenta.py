from arsenal.privesc.diferenta import cai


def test_doar_ce_e_nou():
    acum = {"a", "b", "c"}
    baza = {"a", "b"}
    assert acum - baza == {"c"}


def test_cai_citeste_multime(tmp_path):
    f = tmp_path / "suid.txt"
    f.write_text("# comentariu\n/bin/a\n/bin/a\n\n/bin/b\n")
    assert cai(str(f)) == {"/bin/a", "/bin/b"}

