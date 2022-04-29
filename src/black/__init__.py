import io
import sys
import tokenize
import traceback
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Tuple
from warnings import warn

from vyper.ast import parse_to_ast

from black.comments import normalize_fmt_off
from black.linegen import LineGenerator, transform_line
from black.lines import EmptyLineTracker, Line
from black.mode import Mode
from black.parsing import lib2to3_parse
from black.report import Report, Changed, NothingChanged

# types
FileContent = str
Encoding = str
NewLine = str


class WriteBack(Enum):
    NO = 0
    YES = 1
    # todo(abner) enable DIFF/CHECK/COLOR_DIFF
    # DIFF = 2
    # CHECK = 3
    # COLOR_DIFF = 4

    @classmethod
    def from_configuration(
            cls, *, check: bool, diff: bool, color: bool = False
    ) -> "WriteBack":
        if check and not diff:
            return cls.CHECK

        if diff and color:
            return cls.COLOR_DIFF

        return cls.DIFF if diff else cls.YES


def reformat_code(
        content: str, fast: bool, write_back: WriteBack, mode: Mode, report: Report
) -> None:
    """
    Reformat and print out `content` without spawning child processes.
    Similar to `reformat_one`, but for string content.

    `fast`, `write_back`, and `mode` options are passed to
    :func:`format_file_in_place` or :func:`format_stdin_to_stdout`.
    """
    path = Path("<string>")
    try:
        changed = Changed.NO
        if format_stdin_to_stdout(
                content=content, fast=fast, write_back=write_back, mode=mode
        ):
            changed = Changed.YES
        report.done(path, changed)
    except Exception as exc:
        if report.verbose:
            traceback.print_exc()
        report.failed(path, str(exc))

def format_str(src_contents: str, *, mode: Mode) -> str:
    """Reformat a string and return new contents.

    `mode` determines formatting options, such as how many characters per line are
    allowed.  Example:

    >>> import black
    >>> print(black.format_str("def f(arg:str='')->None:...", mode=black.Mode()))
    def f(arg: str = "") -> None:
        ...

    A more complex example:

    >>> print(
    ...   black.format_str(
    ...     "def f(arg:str='')->None: hey",
    ...     mode=black.Mode(
    ...       target_versions={black.TargetVersion.PY36},
    ...       line_length=10,
    ...       string_normalization=False,
    ...     ),
    ...   ),
    ... )
    def f(
        arg: str = '',
    ) -> None:
        hey

    """
    dst_contents = _format_str_once(src_contents, mode=mode)
    # Forced second pass to work around optional trailing commas (becoming
    # forced trailing commas on pass 2) interacting differently with optional
    # parentheses.  Admittedly ugly.
    if src_contents != dst_contents:
        return _format_str_once(dst_contents, mode=mode)
    return dst_contents


def _format_str_once(src_contents: str, *, mode: Mode) -> str:
    src_node = lib2to3_parse(src_contents.lstrip(), mode.target_versions)
    dst_contents = []

    normalize_fmt_off(src_node, preview=mode.preview)
    lines = LineGenerator(mode=mode)
    elt = EmptyLineTracker(is_pyi=False)
    empty_line = Line(mode=mode)
    after = 0
    for current_line in lines.visit(src_node):
        dst_contents.append(str(empty_line) * after)
        before, after = elt.maybe_empty_lines(current_line)
        dst_contents.append(str(empty_line) * before)
        for line in transform_line(
            current_line, mode=mode
        ):
            dst_contents.append(str(line))
    return "".join(dst_contents)


def decode_bytes(src: bytes) -> Tuple[FileContent, Encoding, NewLine]:
    """Return a tuple of (decoded_contents, encoding, newline).

    `newline` is either CRLF or LF but `decoded_contents` is decoded with
    universal newlines (i.e. only contains LF).
    """
    srcbuf = io.BytesIO(src)
    encoding, lines = tokenize.detect_encoding(srcbuf.readline)
    if not lines:
        return "", encoding, "\n"

    newline = "\r\n" if b"\r\n" == lines[0][-2:] else "\n"
    srcbuf.seek(0)
    with io.TextIOWrapper(srcbuf, encoding) as tiow:
        return tiow.read(), encoding, newline


def format_file_contents(src_contents: str, *, fast: bool, mode: Mode) -> FileContent:
    """Reformat contents of a file and return new contents.

    If `fast` is False, additionally confirm that the reformatted code is
    valid by calling :func:`assert_equivalent` and :func:`assert_stable` on it.
    `mode` is passed to :func:`format_str`.
    """
    if not src_contents.strip():
        raise NothingChanged

    dst_contents = format_str(src_contents, mode=mode)
    if src_contents == dst_contents:
        raise NothingChanged

    return dst_contents


def format_stdin_to_stdout(
        fast: bool,
        *,
        content: Optional[str] = None,
        write_back: WriteBack = WriteBack.NO,
        mode: Mode,
) -> bool:
    """Format file on stdin. Return True if changed.

    If content is None, it's read from sys.stdin.

    If `write_back` is YES, write reformatted code back to stdout. If it is DIFF,
    write a diff to stdout. The `mode` argument is passed to
    :func:`format_file_contents`.
    """
    then = datetime.utcnow()

    if content is None:
        src, encoding, newline = decode_bytes(sys.stdin.buffer.read())
    else:
        src, encoding, newline = content, "utf-8", ""

    dst = src
    try:
        dst = format_file_contents(src, fast=fast, mode=mode)
        return True

    except NothingChanged:
        return False

    finally:
        f = io.TextIOWrapper(
            sys.stdout.buffer, encoding=encoding, newline=newline, write_through=True
        )
        if write_back == WriteBack.YES:
            # Make sure there's a newline after the content
            if dst and dst[-1] != "\n":
                dst += "\n"
            f.write(dst)
        # todo(abner) enable DIFF/COLOR_DIFF
        # elif write_back in (WriteBack.DIFF, WriteBack.COLOR_DIFF):
        #     now = datetime.utcnow()
        #     src_name = f"STDIN\t{then} +0000"
        #     dst_name = f"STDOUT\t{now} +0000"
        #     d = diff(src, dst, src_name, dst_name)
        #     if write_back == WriteBack.COLOR_DIFF:
        #         d = color_diff(d)
        #         f = wrap_stream_for_windows(f)
        #     f.write(d)
        f.detach()