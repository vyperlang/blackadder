import re
from vyper.ast.pre_parser import VYPER_CLASS_TYPES, VYPER_EXPRESSION_TYPES, pre_parse

WHITESPACE_EXCEPT_LINEBREAK = r"[^\S\r\n]"
# Whitespace plus optional (multiple) `\` followed by a line break
MIDDLE_WHITESPACE = (
    rf"{WHITESPACE_EXCEPT_LINEBREAK}+"
    rf"(?:\\{WHITESPACE_EXCEPT_LINEBREAK}*\r?\n{WHITESPACE_EXCEPT_LINEBREAK}*)*"
)
REPLACEMENT_CHARACTER = "_"  # character used in variable name replacements

VYPER_DEPRECATED_CLASS_TYPES = {"contract"}
VYPER_CLASS_TYPES |= VYPER_DEPRECATED_CLASS_TYPES


def pre_format_str(src_contents):
    src_contents = src_contents.lstrip()

    vyper_types_names = re.findall(
        rf"^(?:[^\S\r\n]*)"
        fr"(?P<vyper_type>{'|'.join(VYPER_CLASS_TYPES.union(VYPER_EXPRESSION_TYPES))})"
        fr"{MIDDLE_WHITESPACE}"
        fr"(?P<name>\w+).*$",
        src_contents,
        flags=re.M,
    )
    assert len(vyper_types_names) == len(pre_parse(src_contents)[0])

    REGEX_SUBSTITUTE_VYPER_TYPES = re.compile(
        fr"^(?P<leading_whitespace>[^\S\r\n]*)"
        fr"(?P<vyper_type>{'|'.join(VYPER_CLASS_TYPES.union(VYPER_EXPRESSION_TYPES))})"
        fr"(?P<middle_whitespace>{MIDDLE_WHITESPACE})"
        fr"(?P<name>\w+)"
        fr"(?P<trailing_characters>.*)$",
        flags=re.M,
    )

    # Convert vyper-specific declarations to valid Python
    for vyper_type, vyper_name in vyper_types_names:
        if vyper_type in VYPER_CLASS_TYPES:
            replacement_type = "class"
        elif vyper_type in VYPER_EXPRESSION_TYPES:
            replacement_type = "yield"
        else:
            raise RuntimeError(f"Unknown vyper type: {vyper_type}")

        type_length_difference = len(vyper_type) - len(replacement_type)
        # We will replace the variable name by an arbitrary name
        # so that the number of characters of type + name match
        replacement_name_length = len(vyper_name) + type_length_difference
        if replacement_name_length < 1:
            # Variable name length must be at least 1
            replacement_name_length = 1

        replacement_name = REPLACEMENT_CHARACTER * replacement_name_length

        # TODO: can fail if `vyper_name` is too short
        # (when using `log` with a variable of less than 3 characters length)
        # assert ( len(vyper_type) + len(vyper_name) == \
        #   len(replacement_type) + len(replacement_name)))
        def _replacement_function(match):
            return (
                f"{match.group('leading_whitespace')}"
                f"{replacement_type}"
                f"{match.group('middle_whitespace')}"
                f"{replacement_name}"
                f"{match.group('trailing_characters')}"
            )

        # Substitute the original string
        src_contents = REGEX_SUBSTITUTE_VYPER_TYPES.sub(
            _replacement_function, string=src_contents, count=1
        )

    return vyper_types_names, src_contents


def post_format_str(
    vyper_types_names,
    dst_contents,
):
    # ?P<name> saves the group under match.group("$name")
    REGEX_EXTRACT_VYPER_NAMES = re.compile(
        fr"^(?P<leading_whitespace>[^\S\r\n]*)(?:class|yield)"
        fr"(?P<middle_whitespace>{MIDDLE_WHITESPACE})"
        fr"(?P<name>{REPLACEMENT_CHARACTER}+)"
        fr"(?P<trailing_characters>.*)$",
        flags=re.MULTILINE,
    )

    for vyper_type, var_name in vyper_types_names:

        def _replacement_function(match):
            return (
                f"{match.group('leading_whitespace')}"
                f"{vyper_type}"
                f"{match.group('middle_whitespace')}"
                f"{var_name}"
                f"{match.group('trailing_characters')}"
            )

        dst_contents = REGEX_EXTRACT_VYPER_NAMES.sub(
            _replacement_function, string=dst_contents, count=1
        )

    return dst_contents
