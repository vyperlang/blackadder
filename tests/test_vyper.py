# FIXME: proper asserts, not just smoke tests

import blackadder
import black
import pytest


def test_vyper():
    with open("tests/data/Vault.vy", "r") as f:
        src = f.read()
    assert blackadder.format_str_override(
        src,
    )


@pytest.mark.xfail(reason="Only --fast works atm")
def test_vyper_stable():  # Same as above except fast = False
    assert blackadder.reformat_one(
        black.Path("data/Vault.vy"),
        fast=False,
        write_back=black.WriteBack.NO,
        report=black.Report(check=True),
    )
