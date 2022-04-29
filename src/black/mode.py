"""Data structures configuring Black behavior.

Mostly around Python language feature support per version and Black configuration
chosen by the user.
"""

from hashlib import sha256
import sys

from dataclasses import dataclass, field
from enum import Enum, auto
from operator import attrgetter
from typing import Dict, Set
from warnings import warn

if sys.version_info < (3, 8):
    from typing_extensions import Final
else:
    from typing import Final

from black.const import DEFAULT_LINE_LENGTH


class TargetVersion(Enum):
    PY33 = 3
    PY34 = 4
    PY35 = 5
    PY36 = 6
    PY37 = 7
    PY38 = 8
    PY39 = 9
    PY310 = 10
    PY311 = 11


class Feature(Enum):
    F_STRINGS = 2
    NUMERIC_UNDERSCORES = 3
    TRAILING_COMMA_IN_CALL = 4
    TRAILING_COMMA_IN_DEF = 5
    # The following two feature-flags are mutually exclusive, and exactly one should be
    # set for every version of python.
    ASYNC_IDENTIFIERS = 6
    ASYNC_KEYWORDS = 7
    ASSIGNMENT_EXPRESSIONS = 8
    POS_ONLY_ARGUMENTS = 9
    RELAXED_DECORATORS = 10
    PATTERN_MATCHING = 11
    UNPACKING_ON_FLOW = 12
    ANN_ASSIGN_EXTENDED_RHS = 13
    EXCEPT_STAR = 14
    FORCE_OPTIONAL_PARENTHESES = 50

    # __future__ flags
    FUTURE_ANNOTATIONS = 51


FUTURE_FLAG_TO_FEATURE: Final = {
}

VERSION_TO_FEATURES: Dict[TargetVersion, Set[Feature]] = {
}


def supports_feature(target_versions: Set[TargetVersion], feature: Feature) -> bool:
    return all(feature in VERSION_TO_FEATURES[version] for version in target_versions)


class Preview(Enum):
    """Individual preview style features."""

    string_processing = auto()
    remove_redundant_parens = auto()
    one_element_subscript = auto()
    annotation_parens = auto()


class Deprecated(UserWarning):
    """Visible deprecation warning."""


@dataclass
class Mode:
    target_versions: Set[TargetVersion] = field(default_factory=set)
    line_length: int = DEFAULT_LINE_LENGTH
    string_normalization: bool = True
    magic_trailing_comma: bool = True
    experimental_string_processing: bool = False
    preview: bool = False

    def __post_init__(self) -> None:
        if self.experimental_string_processing:
            warn(
                "`experimental string processing` has been included in `preview`"
                " and deprecated. Use `preview` instead.",
                Deprecated,
            )

    def __contains__(self, feature: Preview) -> bool:
        """
        Provide `Preview.FEATURE in Mode` syntax that mirrors the ``preview`` flag.

        The argument is not checked and features are not differentiated.
        They only exist to make development easier by clarifying intent.
        """
        if feature is Preview.string_processing:
            return self.preview or self.experimental_string_processing
        return self.preview

    def get_cache_key(self) -> str:
        if self.target_versions:
            version_str = ",".join(
                str(version.value)
                for version in sorted(self.target_versions, key=attrgetter("value"))
            )
        else:
            version_str = "-"
        parts = [
            version_str,
            str(self.line_length),
            str(int(self.string_normalization)),
            str(int(self.magic_trailing_comma)),
            str(int(self.experimental_string_processing)),
            str(int(self.preview)),
        ]
        return ".".join(parts)