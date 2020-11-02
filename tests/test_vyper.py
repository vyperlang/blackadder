import blackadder
import black


def test_vyper():
    blackadder.reformat_one(
        black.Path("data/Vault.vy"),
        fast=True,
        write_back=black.WriteBack.NO,
        mode=black.Mode(),
        report=black.Report(check=True),
    )


def test_vyper_stable():  # Same as above except fast = False
    blackadder.reformat_one(
        black.Path("data/Vault.vy"),
        fast=False,
        write_back=black.WriteBack.NO,
        mode=black.Mode(),
        report=black.Report(check=True),
    )
