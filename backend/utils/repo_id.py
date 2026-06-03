from backend.utils.url_parser import parse_github_url


def repo_id_from_url(url: str) -> str:
    """Stable identifier used for data/repos folders and future collections."""
    parsed = parse_github_url(url)
    return repo_id_from_parts(parsed.owner, parsed.repo)


def repo_id_from_parts(owner: str, repo: str) -> str:
    return f"{owner.lower()}_{repo.lower()}"


def repo_slug_from_id(repo_id: str) -> str:
    """Convert owner_repo back to owner/repo for display."""
    if "_" not in repo_id:
        return repo_id
    owner, repo = repo_id.split("_", 1)
    return f"{owner}/{repo}"


def local_dir_name(repo_id: str) -> str:
    """Directory name under data/repos."""
    return repo_id
