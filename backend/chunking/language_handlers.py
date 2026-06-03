import ast
import re
from dataclasses import dataclass

_JS_FUNC_RE = re.compile(
    r"^(?:export\s+)?(?:async\s+)?function\s+(\w+)|"
    r"^(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\(",
    re.MULTILINE,
)
_JS_CLASS_RE = re.compile(r"^(?:export\s+)?class\s+(\w+)", re.MULTILINE)
_GO_FUNC_RE = re.compile(r"^func\s+(?:\([^)]+\)\s+)?(\w+)\s*\(", re.MULTILINE)


@dataclass(frozen=True)
class SymbolBlock:
    symbol: str | None
    start_line: int
    end_line: int
    text: str


def split_python(text: str) -> list[SymbolBlock] | None:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return None

    lines = text.splitlines()
    blocks: list[SymbolBlock] = []

    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        start = node.lineno
        end = getattr(node, "end_lineno", None) or start
        symbol = node.name
        chunk_lines = lines[start - 1 : end]
        blocks.append(
            SymbolBlock(
                symbol=symbol,
                start_line=start,
                end_line=end,
                text="\n".join(chunk_lines),
            )
        )

    return blocks or None


def split_javascript_like(text: str) -> list[SymbolBlock] | None:
    lines = text.splitlines()
    boundaries: list[tuple[str | None, int]] = []

    for index, line in enumerate(lines, start=1):
        func_match = _JS_FUNC_RE.match(line.strip())
        if func_match:
            name = func_match.group(1) or func_match.group(2)
            boundaries.append((name, index))
            continue
        class_match = _JS_CLASS_RE.match(line.strip())
        if class_match:
            boundaries.append((class_match.group(1), index))

    if not boundaries:
        return None

    blocks: list[SymbolBlock] = []
    for i, (symbol, start_line) in enumerate(boundaries):
        end_line = boundaries[i + 1][1] - 1 if i + 1 < len(boundaries) else len(lines)
        chunk_lines = lines[start_line - 1 : end_line]
        blocks.append(
            SymbolBlock(
                symbol=symbol,
                start_line=start_line,
                end_line=end_line,
                text="\n".join(chunk_lines),
            )
        )
    return blocks


def split_go(text: str) -> list[SymbolBlock] | None:
    lines = text.splitlines()
    boundaries: list[tuple[str | None, int]] = []
    for index, line in enumerate(lines, start=1):
        match = _GO_FUNC_RE.match(line.strip())
        if match:
            boundaries.append((match.group(1), index))

    if not boundaries:
        return None

    blocks: list[SymbolBlock] = []
    for i, (symbol, start_line) in enumerate(boundaries):
        end_line = boundaries[i + 1][1] - 1 if i + 1 < len(boundaries) else len(lines)
        chunk_lines = lines[start_line - 1 : end_line]
        blocks.append(
            SymbolBlock(
                symbol=symbol,
                start_line=start_line,
                end_line=end_line,
                text="\n".join(chunk_lines),
            )
        )
    return blocks


def split_by_language(language: str, text: str) -> list[SymbolBlock] | None:
    if language == "python":
        return split_python(text)
    if language in {"javascript", "typescript"}:
        return split_javascript_like(text)
    if language == "go":
        return split_go(text)
    return None
