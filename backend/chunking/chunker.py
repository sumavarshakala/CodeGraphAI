import hashlib

from backend.chunking.language_handlers import split_by_language
from backend.config.settings import get_settings
from backend.models.schemas import CodeChunk, FileContent


def _chunk_id(repo_id: str, relative_path: str, start_line: int, end_line: int, index: int) -> str:
    raw = f"{repo_id}|{relative_path}|{start_line}|{end_line}|{index}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


def _split_window(
    text: str,
    *,
    max_chars: int,
    overlap_chars: int,
    base_start_line: int = 1,
) -> list[tuple[str, int, int]]:
    if len(text) <= max_chars:
        start = base_start_line
        line_count = text.count("\n") + (1 if text else 0)
        return [(text, start, start + max(line_count - 1, 0))]

    lines = text.splitlines(keepends=True)
    chunks: list[tuple[str, int, int]] = []
    current: list[str] = []
    current_len = 0
    window_start_line = base_start_line
    line_cursor = base_start_line

    for line in lines:
        line_len = len(line)
        if current and current_len + line_len > max_chars:
            body = "".join(current)
            end_line = line_cursor - 1
            chunks.append((body, window_start_line, max(end_line, window_start_line)))
            overlap = body[-overlap_chars:] if overlap_chars else ""
            current = [overlap, line] if overlap else [line]
            current_len = len("".join(current))
            window_start_line = end_line + 1 if end_line >= window_start_line else line_cursor
        else:
            if not current:
                window_start_line = line_cursor
            current.append(line)
            current_len += line_len
        line_cursor += 1

    if current:
        body = "".join(current)
        end_line = base_start_line + text.count("\n")
        chunks.append((body, window_start_line, end_line))

    return chunks


def _blocks_from_file(
    file_content: FileContent,
    *,
    max_chars: int,
    overlap_chars: int,
) -> list[tuple[str, int, int, str | None]]:
    structured = split_by_language(file_content.language, file_content.text)
    if structured:
        result: list[tuple[str, int, int, str | None]] = []
        for block in structured:
            if len(block.text) <= max_chars:
                result.append((block.text, block.start_line, block.end_line, block.symbol))
            else:
                for body, start, end in _split_window(
                    block.text,
                    max_chars=max_chars,
                    overlap_chars=overlap_chars,
                    base_start_line=block.start_line,
                ):
                    result.append((body, start, end, block.symbol))
        return result

    return [
        (body, start, end, None)
        for body, start, end in _split_window(
            file_content.text,
            max_chars=max_chars,
            overlap_chars=overlap_chars,
        )
    ]


def chunk_files(repo_id: str, files: list[FileContent]) -> list[CodeChunk]:
    settings = get_settings()
    chunks: list[CodeChunk] = []

    for file_content in files:
        blocks = _blocks_from_file(
            file_content,
            max_chars=settings.chunk_max_chars,
            overlap_chars=settings.chunk_overlap_chars,
        )
        for index, (text, start_line, end_line, symbol) in enumerate(blocks):
            stripped = text.strip()
            if not stripped:
                continue
            chunks.append(
                CodeChunk(
                    chunk_id=_chunk_id(repo_id, file_content.relative_path, start_line, end_line, index),
                    repo_id=repo_id,
                    relative_path=file_content.relative_path,
                    language=file_content.language,
                    text=stripped,
                    start_line=start_line,
                    end_line=end_line,
                    symbol=symbol,
                    chunk_index=index,
                )
            )

    return chunks
