import git
from functools import lru_cache

# This would be loaded from config in a real app
GIT_REPO_PATH = "/Users/dhawalpandya/Sandbox/aeonis" # Using the full path for now

@lru_cache(maxsize=1)
def get_repo():
    """
    Returns a cached git.Repo object.
    Using lru_cache to ensure we don't re-initialize the Repo object on every call.
    """
    try:
        repo = git.Repo(GIT_REPO_PATH, search_parent_directories=True)
        return repo
    except git.exc.InvalidGitRepositoryError:
        # Handle case where the path is not a git repo
        return None

def list_branches():
    """Lists all branches in the repository."""
    repo = get_repo()
    if not repo:
        return {"error": "Git repository not found."}
    
    return [head.name for head in repo.heads]

def get_commit_history(branch: str, limit: int = 10):
    """
    Returns the commit history for a given branch.
    """
    repo = get_repo()
    if not repo:
        return {"error": "Git repository not found."}
        
    try:
        commits = list(repo.iter_commits(branch, max_count=limit))
        return [
            {
                "hash": c.hexsha,
                "author": c.author.name,
                "date": c.committed_datetime.isoformat(),
                "message": c.message.strip(),
            }
            for c in commits
        ]
    except git.exc.GitCommandError as e:
        return {"error": f"Could not find branch '{branch}'. Details: {e}"}

def get_commit_diff(commit_hash: str):
    """
    Returns the diff for a specific commit.
    """
    repo = get_repo()
    if not repo:
        return {"error": "Git repository not found."}

    try:
        commit = repo.commit(commit_hash)
        # The diff is against the first parent of the commit
        diff_text = commit.tree.diff_to_tree(commit.parents[0]).__str__()
        return {"hash": commit_hash, "diff": diff_text}
    except (git.exc.BadName, IndexError) as e:
        # Handle case for initial commit (no parents) or invalid hash
        if not commit.parents:
            return {"hash": commit_hash, "diff": commit.tree.diff_to_tree(None).__str__()}
        return {"error": f"Could not find commit '{commit_hash}'. Details: {e}"}

def read_file_at_commit(file_path: str, commit_hash: str):
    """
    Reads the content of a file at a specific commit.
    """
    repo = get_repo()
    if not repo:
        return {"error": "Git repository not found."}
        
    try:
        commit = repo.commit(commit_hash)
        blob = commit.tree / file_path
        return {"file_content": blob.data_stream.read().decode("utf-8")}
    except (KeyError, git.exc.BadName) as e:
        return {"error": f"Could not read file '{file_path}' at commit '{commit_hash}'. Details: {e}"}
