import shutil
from dataclasses import dataclass
from pathlib import Path

from git import Repo
from git.exc import GitCommandError

from backend.config.settings import get_settings
from backend.utils.repo_id import local_dir_name, repo_id_from_url
from backend.utils.url_parser import parse_github_url


@dataclass(frozen=True)
class CloneResult:
    repo_id: str
    repo_url: str
    local_path: Path
    cloned: bool
    message: str = ""

    def to_dict(self) -> dict:
        return {
            "repo_id": self.repo_id,
            "repo_url": self.repo_url,
            "local_path": str(self.local_path),
            "cloned": self.cloned,
            "message": self.message,
        }


def clone_repository(url: str, *, force: bool = False) -> CloneResult:
    """
    Clone a public GitHub repository into data/repos/{repo_id}.

    If the repo already exists and force=False, returns the existing path
    without re-cloning.
    """
    settings = get_settings()
    parsed = parse_github_url(url)
    repo_id = repo_id_from_url(parsed.normalized_url)
    target_dir = settings.repos_dir / local_dir_name(repo_id)

    if target_dir.exists():
        if not force:
            if (target_dir / ".git").is_dir():
                return CloneResult(
                    repo_id=repo_id,
                    repo_url=parsed.normalized_url,
                    local_path=target_dir.resolve(),
                    cloned=False,
                    message="Repository already present; skipped clone.",
                )
            raise FileExistsError(
                f"Path exists but is not a git repository: {target_dir}. "
                "Use force=True to replace it."
            )
        shutil.rmtree(target_dir)

    target_dir.parent.mkdir(parents=True, exist_ok=True)
    try:
        Repo.clone_from(
            parsed.clone_url,
            target_dir,
            depth=settings.git_clone_depth,
        )
    except GitCommandError as exc:
        raise RuntimeError(f"Failed to clone repository: {exc}") from exc

    return CloneResult(
        repo_id=repo_id,
        repo_url=parsed.normalized_url,
        local_path=target_dir.resolve(),
        cloned=True,
        message="Repository cloned successfully.",
    )
