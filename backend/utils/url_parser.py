import re
from dataclasses import dataclass
from urllib.parse import urlparse

_GITHUB_HOSTS = frozenset({"github.com", "www.github.com"})

_PATH_RE = re.compile(
    r"^/?(?P<owner>[\w.\-]+)/(?P<repo>[\w.\-]+?)(?:\.git)?/?(?:#.*)?(?:\?.*)?$"
)

_SSH_RE = re.compile(
    r"^git@github\.com:(?P<owner>[\w.\-]+)/(?P<repo>[\w.\-]+?)(?:\.git)?$"
)


@dataclass(frozen=True)
class ParsedGitHubUrl:
    owner: str
    repo: str
    normalized_url: str

    @property
    def clone_url(self) -> str:
        return f"https://github.com/{self.owner}/{self.repo}.git"

    @property
    def web_url(self) -> str:
        return self.normalized_url


def parse_github_url(url: str) -> ParsedGitHubUrl:
    """
    Parse a public GitHub repository URL.

    Supports:
    - https://github.com/owner/repo
    - https://github.com/owner/repo.git
    - git@github.com:owner/repo.git
    - github.com/owner/repo (scheme added)
    """
    raw = url.strip()
    if not raw:
        raise ValueError("Repository URL is required.")

    if raw.startswith("git@"):
        match = _SSH_RE.match(raw)
        if not match:
            raise ValueError("Invalid GitHub SSH URL. Expected git@github.com:owner/repo")
        owner = match.group("owner")
        repo = _normalize_repo_name(match.group("repo"))
        return _build_parsed(owner, repo)

    if "://" not in raw:
        raw = f"https://{raw}"

    parsed = urlparse(raw)
    host = (parsed.netloc or "").lower().removeprefix("www.")
    if host not in _GITHUB_HOSTS:
        raise ValueError("Only github.com repository URLs are supported in Phase 1.")

    path_match = _PATH_RE.match(parsed.path or "")
    if not path_match:
        raise ValueError("URL must look like https://github.com/owner/repo")

    owner = path_match.group("owner")
    repo = _normalize_repo_name(path_match.group("repo"))
    return _build_parsed(owner, repo)


def _normalize_repo_name(repo: str) -> str:
    return repo.removesuffix(".git")


def _build_parsed(owner: str, repo: str) -> ParsedGitHubUrl:
    if not owner or not repo:
        raise ValueError("Owner and repository name are required.")
    normalized = f"https://github.com/{owner}/{repo}"
    return ParsedGitHubUrl(owner=owner, repo=repo, normalized_url=normalized)
