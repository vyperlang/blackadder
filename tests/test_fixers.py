from pathlib import Path

import black
import difflib
import itertools
import pytest

import blackadder
import vyper


DATA_DIR = Path(__file__).parent / "data"
# NOTE: Do this so pytest creates pretty test names
TEST_CASES = list(f.name for f in DATA_DIR.glob("*.ndiff"))

OUTPUT_FORMATS = ["abi", "bytecode", "bytecode_runtime"]


@pytest.mark.parametrize("test_case", TEST_CASES)
def test_apply_blackadder(test_case):
    # NOTE: Get the file from the test case name (undoing previous slimming)
    lines = list((DATA_DIR / test_case).read_text().splitlines())
    # Construct before/after fixer applied
    unchanged = "\n".join(difflib.restore(lines, 1))  # Lines starting with '-'
    expected = "\n".join(difflib.restore(lines, 2))  # Lines starting with '+'

    # Fixer works as expected
    fixed = blackadder.format_str_override(
        unchanged,
        mode=black.Mode(),
    )
    assert fixed == expected

    # Fixer doesn't change critical compiler artifacts in any way
    unchanged_compilation = vyper.compile_code(unchanged, output_formats=OUTPUT_FORMATS)
    fixed_compilation = vyper.compile_code(fixed, output_formats=OUTPUT_FORMATS)
    for artifact in OUTPUT_FORMATS:
        assert unchanged_compilation[artifact] == fixed_compilation[artifact]
