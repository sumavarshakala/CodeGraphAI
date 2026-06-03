from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class FileContent:
    relative_path: str
    language: str
    text: str


@dataclass(frozen=True)
class CodeChunk:
    chunk_id: str
    repo_id: str
    relative_path: str
    language: str
    text: str
    start_line: int
    end_line: int
    symbol: str | None = None
    chunk_index: int = 0

    def to_metadata(self) -> dict[str, Any]:
        return {
            "repo_id": self.repo_id,
            "relative_path": self.relative_path,
            "language": self.language,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "symbol": self.symbol or "",
            "chunk_index": self.chunk_index,
        }


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: str
    relative_path: str
    language: str
    text: str
    start_line: int
    end_line: int
    score: float
    symbol: str | None = None

    @property
    def citation(self) -> str:
        if self.start_line == self.end_line:
            return f"{self.relative_path}:{self.start_line}"
        return f"{self.relative_path}:{self.start_line}-{self.end_line}"


@dataclass
class IngestResult:
    repo_id: str
    repo_url: str
    local_path: str
    files_read: int
    chunks_created: int
    chunks_indexed: int
    message: str = ""


@dataclass
class QueryResult:
    repo_id: str
    question: str
    answer: str
    sources: list[RetrievedChunk] = field(default_factory=list)
