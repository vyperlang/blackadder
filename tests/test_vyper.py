# FIXME: proper asserts, not just smoke tests

import src
import pytest
from black import format_str
from black.mode import Mode


def test_vyper():
    with open("tests/data/Vault.vy", "r") as f:
        src = f.read()
    print(format_str(
        src,
        mode= Mode(),
    ))


# @pytest.mark.xfail(reason="Only --fast works atm")
# def test_vyper_stable():  # Same as above except fast = False
#     assert src.reformat_one(
#         black.Path("data/Vault.vy"),
#         fast=False,
#         write_back=black.WriteBack.NO,
#         mode=black.Mode(),
#         report=black.Report(check=True),
#     )
