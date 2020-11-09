from black import format_str as black_format_str
from black import FileContent
from blackadder.vyper_compat import pre_format_str, post_format_str


def format_str_override(src_contents: str, **kwargs) -> FileContent:
    vyper_types_names, src_contents = pre_format_str(src_contents)
    dst_contents = black_format_str(src_contents=src_contents, **kwargs)
    dst_contents = post_format_str(vyper_types_names, dst_contents)
    return dst_contents


# Override black's `format_str`
import black  # noqa

black.format_str = format_str_override

from black import *  # noqa: F4, E4
