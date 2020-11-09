"""
Parts of this file were taken from black (https://github.com/psf/black/)
"""
from setuptools import setup
import sys

assert sys.version_info >= (3, 6, 0), "black requires Python 3.6+"
from pathlib import Path  # noqa E402

CURRENT_DIR = Path(__file__).parent
sys.path.insert(0, str(CURRENT_DIR))  # for setuptools.build_meta


def get_long_description() -> str:
    return (
        (CURRENT_DIR / "README.md").read_text(encoding="utf8")
        + "\n\n"
        + (CURRENT_DIR / "CHANGES.md").read_text(encoding="utf8")
    )


setup(
    name="blackadder",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    description="The uncompromising code formatter.",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    packages=["blackadder"],
    python_requires=">=3.6",
    install_requires=["black>=20.8b1", "vyper>=0.2.7"],
    test_suite="tests",
    tests_require=["pytest"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
    ],
    entry_points={
        "console_scripts": [
            "blackadder=blackadder:patched_main",
        ]
    },
)
