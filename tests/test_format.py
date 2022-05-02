from pathlib import Path
from typing import List, Tuple

import pytest
from black.mode import Mode
from tests.util import assert_format

THIS_DIR = Path(__file__).parent
DATA_DIR = THIS_DIR / "data"
PROJECT_ROOT = THIS_DIR.parent
EMPTY_LINE = "# EMPTY LINE WITH WHITESPACE" + " (this comment will be removed)"

SIMPLE_CASES: List[str] = [
    "Vault.vy",
    "Interface.vy"
]

DEFAULT_MODE = Mode()


def read_data_from_file(file_name: Path) -> Tuple[str, str]:
    with open(file_name, "r", encoding="utf8") as test:
        lines = test.readlines()
    _input: List[str] = []
    _output: List[str] = []
    result = _input
    for line in lines:
        line = line.replace(EMPTY_LINE, "")
        if line.rstrip() == "# output":
            result = _output
            continue

        result.append(line)
    if _input and not _output:
        # If there's no output marker, treat the entire file as already pre-formatted.
        _output = _input[:]
    return "".join(_input).strip() + "\n", "".join(_output).strip() + "\n"


def check_file(filename: str, mode: Mode, *, data: bool = True) -> None:
    source, expected = read_data(filename, data=data)
    assert_format(source, expected, mode, fast=False)


def read_data(name: str, data: bool = True) -> Tuple[str, str]:
    """read_data('test_name') -> 'input', 'output'"""
    if not name.endswith((".py", ".pyi", ".out", ".diff", ".vy")):
        name += ".py"
    base_dir = DATA_DIR if data else PROJECT_ROOT
    return read_data_from_file(base_dir / name)


@pytest.mark.parametrize("filename", SIMPLE_CASES)
def test_simple_format(filename: str) -> None:
    check_file(filename, DEFAULT_MODE)
