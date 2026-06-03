from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from backend.config.ignore_patterns import (
    DEFAULT_IGNORE_DIRS,
    DEFAULT_IGNORE_EXTENSIONS,
    DEFAULT_IGNORE_FILE_NAMES,
    SPECIAL_FILE_NAMES,
    TEXT_CODE_EXTENSIONS,
)
from backend.config.settings import get_settings


@dataclass(frozen=True)
class FileContent:
    relative_path: str
    language: str
    text: str
    size_bytes: int
    line_count: int


@dataclass
class RepositoryStats:
    repo_path: str
    files_discovered: int = 0
    files_read: int = 0
    files_skipped_ignored: int = 0
    files_skipped_unsupported: int = 0
    files_skipped_too_large: int = 0
    files_skipped_empty: int = 0
    files_skipped_unreadable: int = 0
    total_bytes: int = 0
    total_lines: int = 0
    languages: dict[str, int] = field(default_factory=dict)
    extensions: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "repo_path": self.repo_path,
            "files_discovered": self.files_discovered,
            "files_read": self.files_read,
            "files_skipped_ignored": self.files_skipped_ignored,
            "files_skipped_unsupported": self.files_skipped_unsupported,
            "files_skipped_too_large": self.files_skipped_too_large,
            "files_skipped_empty": self.files_skipped_empty,
            "files_skipped_unreadable": self.files_skipped_unreadable,
            "total_bytes": self.total_bytes,
            "total_lines": self.total_lines,
            "languages": dict(self.languages),
            "extensions": dict(self.extensions),
        }


@dataclass
class ReadRepositoryResult:
    files: list[FileContent]
    stats: RepositoryStats


_LANGUAGE_BY_EXTENSION: dict[str, str] = {
    ".py": "python",
    ".pyi": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".kt": "kotlin",
    ".kts": "kotlin",
    ".rb": "ruby",
    ".php": "php",
    ".cs": "csharp",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".c": "c",
    ".h": "c",
    ".hpp": "cpp",
    ".swift": "swift",
    ".scala": "scala",
    ".lua": "lua",
    ".r": "r",
    ".sql": "sql",
    ".sh": "shell",
    ".bash": "shell",
    ".zsh": "shell",
    ".ps1": "powershell",
    ".bat": "batch",
    ".cmd": "batch",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".ini": "ini",
    ".json": "json",
    ".xml": "xml",
    ".html": "html",
    ".htm": "html",
    ".css": "css",
    ".scss": "scss",
    ".sass": "sass",
    ".less": "less",
    ".md": "markdown",
    ".mdx": "markdown",
    ".rst": "rst",
    ".txt": "text",
    ".vue": "vue",
    ".svelte": "svelte",
    ".dockerfile": "dockerfile",
    ".gradle": "gradle",
    ".cmake": "cmake",
}


def _language_for_path(path: Path) -> str:
    name = path.name.lower()
    if name == "dockerfile":
        return "dockerfile"
    if name in {"makefile", "gnumakefile"}:
        return "makefile"
    return _LANGUAGE_BY_EXTENSION.get(path.suffix.lower(), "text")


def _should_skip_dir(name: str) -> bool:
    lowered = name.lower()
    return lowered in DEFAULT_IGNORE_DIRS or name.startswith(".")


def _is_supported_source_file(path: Path) -> bool:
    name = path.name.lower()
    if name in DEFAULT_IGNORE_FILE_NAMES:
        return False
    suffix = path.suffix.lower()
    if suffix in DEFAULT_IGNORE_EXTENSIONS:
        return False
    if name in SPECIAL_FILE_NAMES:
        return True
    if suffix in TEXT_CODE_EXTENSIONS:
        return True
    if not suffix:
        return name in {"readme", "license", "changelog"}
    return False


def _read_text_file(path: Path, max_bytes: int) -> tuple[str | None, str]:
    """
    Read a text file. Returns (content, skip_reason).
    skip_reason is empty when content is returned.
    """
    try:
        data = path.read_bytes()
    except OSError:
        return None, "unreadable"

    if not data:
        return None, "empty"
    if len(data) > max_bytes:
        return None, "too_large"
    if b"\x00" in data[:8192]:
        return None, "unreadable"

    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            text = data.decode(encoding)
            if not text.strip():
                return None, "empty"
            return text, ""
        except UnicodeDecodeError:
            continue
    return None, "unreadable"


def read_repository(repo_path: Path) -> ReadRepositoryResult:
    """
    Walk a cloned repository and return source files plus statistics.
    """
    settings = get_settings()
    root = repo_path.resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"Repository path not found: {repo_path}")

    stats = RepositoryStats(repo_path=str(root))
    files: list[FileContent] = []

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue

        rel = path.relative_to(root)
        if any(_should_skip_dir(part) for part in rel.parts[:-1]):
            stats.files_skipped_ignored += 1
            continue

        stats.files_discovered += 1

        if not _is_supported_source_file(path):
            stats.files_skipped_unsupported += 1
            continue

        text, skip_reason = _read_text_file(path, settings.max_file_bytes)
        if skip_reason == "too_large":
            stats.files_skipped_too_large += 1
            continue
        if skip_reason == "empty":
            stats.files_skipped_empty += 1
            continue
        if skip_reason == "unreadable":
            stats.files_skipped_unreadable += 1
            continue

        language = _language_for_path(path)
        line_count = text.count("\n") + 1
        size_bytes = len(text.encode("utf-8"))

        files.append(
            FileContent(
                relative_path=rel.as_posix(),
                language=language,
                text=text,
                size_bytes=size_bytes,
                line_count=line_count,
            )
        )

        stats.files_read += 1
        stats.total_bytes += size_bytes
        stats.total_lines += line_count
        stats.languages[language] = stats.languages.get(language, 0) + 1

        ext = path.suffix.lower() or "(no extension)"
        stats.extensions[ext] = stats.extensions.get(ext, 0) + 1

    return ReadRepositoryResult(files=files, stats=stats)


def language_summary(result: ReadRepositoryResult) -> list[tuple[str, int]]:
    """Return languages sorted by file count (descending)."""
    counter = Counter(result.stats.languages)
    return counter.most_common()
