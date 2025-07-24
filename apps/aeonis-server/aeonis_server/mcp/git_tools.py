import git
import os
import shutil
from functools import lru_cache
from ..db.repository import TraceRepository

# loaded from config in a real app
REPO_CACHE_DIR = "/tmp/aeonis_repos"

import git
import os
import shutil
import tempfile
from functools import lru_cache
from ..db.repository import TraceRepository

# loaded from config in a real app
REPO_CACHE_DIR = "/tmp/aeonis_repos"


@lru_cache(maxsize=32)  # cache up to 32 repositories
def get_repo(project_id: str, repo: TraceRepository):
    """
    returns a cached git.repo object for a project_id.
    clones if not cached.
    handles public and private repos.
    """
    project = repo.get_project_by_id(project_id)
    if not project or not project.git_repo_url:
        return None

    repo_dir = os.path.join(REPO_CACHE_DIR, str(project.id))

    # if repo cached, pull latest changes
    if os.path.exists(repo_dir):
        try:
            git_repo = git.Repo(repo_dir)
            # for private repos, set up ssh environment for pulling
            if project.is_private and project.git_ssh_key:
                with tempfile.NamedTemporaryFile(delete=False, mode="w") as tmp:
                    tmp.write(project.git_ssh_key)
                    ssh_key_path = tmp.name

                ssh_cmd = f"ssh -i {ssh_key_path} -o StrictHostKeyChecking=no"
                with git_repo.git.custom_environment(GIT_SSH_COMMAND=ssh_cmd):
                    git_repo.remotes.origin.pull()

                os.unlink(ssh_key_path)  # clean up key
            else:
                git_repo.remotes.origin.pull()

            return git_repo
        except git.exc.InvalidGitRepositoryError:
            shutil.rmtree(repo_dir)  # clean up corrupted repo
        except git.exc.GitCommandError as e:
            # could be auth error, try re-cloning
            print(
                f"Error pulling repo for project {project_id}, will try re-cloning: {e}"
            )
            shutil.rmtree(repo_dir)

    # if not cached, clone it
    try:
        if project.is_private and project.git_ssh_key:
            # create temporary file for ssh key
            with tempfile.NamedTemporaryFile(delete=False, mode="w") as tmp:
                tmp.write(project.git_ssh_key)
                ssh_key_path = tmp.name

            # set up ssh command to use key
            ssh_cmd = f"ssh -i {ssh_key_path} -o StrictHostKeyChecking=no"

            # clone with custom ssh environment
            git.Repo.clone_from(
                project.git_repo_url, repo_dir, env={"GIT_SSH_COMMAND": ssh_cmd}
            )

            # important: clean up temporary key file
            os.unlink(ssh_key_path)

            return git.Repo(repo_dir)
        else:
            # public repo, clone normally
            git_repo = git.Repo.clone_from(project.git_repo_url, repo_dir)
            return git_repo

    except git.exc.GitCommandError as e:
        print(f"Error cloning repo for project {project_id}: {e}")
        # clean up failed clone attempt
        if os.path.exists(repo_dir):
            shutil.rmtree(repo_dir)
        # also clean up key if it exists
        if "ssh_key_path" in locals() and os.path.exists(ssh_key_path):
            os.unlink(ssh_key_path)
        return None


def list_branches(project_id: str, repo: TraceRepository):
    """lists all branches in repository."""
    git_repo = get_repo(project_id, repo)
    if not git_repo:
        return {"error": "Git repository not found for this project."}

    return [head.name for head in git_repo.heads]


def get_default_branch(project_id: str, repo: TraceRepository) -> str | None:
    """returns the default branch name of the repository."""
    git_repo = get_repo(project_id, repo)
    if not git_repo:
        return None
    try:
        # get the symbolic ref for the remote's HEAD. this points to the default branch.
        sym_ref = git_repo.git.symbolic_ref(f"refs/remotes/origin/HEAD")
        # the output is usually 'refs/remotes/origin/main' or 'refs/remotes/origin/master'
        default_branch = sym_ref.split("/")[-1]
        return default_branch
    except git.exc.GitCommandError:
        # fallback for detached head or other issues
        return None


def get_commit_history(
    project_id: str, repo: TraceRepository, branch: str, limit: int = 10
):
    """
    returns commit history for a given branch.
    """
    git_repo = get_repo(project_id, repo)
    if not git_repo:
        return {"error": "Git repository not found for this project."}

    try:
        commits = list(git_repo.iter_commits(branch, max_count=limit))
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


def get_commit_diff(project_id: str, repo: TraceRepository, commit_hash: str):
    """
    returns diff for a specific commit.
    """
    git_repo = get_repo(project_id, repo)
    if not git_repo:
        return {"error": "Git repository not found for this project."}

    try:
        commit = git_repo.commit(commit_hash)
        # diff is against first parent of commit
        diffs = commit.diff(commit.parents[0])
        diff_text = "\n".join([str(d) for d in diffs])
        return {"hash": commit_hash, "diff": diff_text}
    except (git.exc.BadName, IndexError) as e:
        # handle case for initial commit or invalid hash
        if not commit.parents:
            diffs = commit.diff(None)
            diff_text = "\n".join([str(d) for d in diffs])
            return {"hash": commit_hash, "diff": diff_text}
        return {"error": f"Could not find commit '{commit_hash}'. Details: {e}"}


def read_file_at_commit(
    project_id: str, repo: TraceRepository, file_path: str, commit_hash: str
):
    """
    reads content of a file at a specific commit.
    """
    git_repo = get_repo(project_id, repo)
    if not git_repo:
        return {"error": "Git repository not found for this project."}

    try:
        commit = git_repo.commit(commit_hash)
        blob = commit.tree / file_path
        return {"file_content": blob.data_stream.read().decode("utf-8")}
    except (KeyError, git.exc.BadName) as e:
        return {
            "error": f"Could not read file '{file_path}' at commit '{commit_hash}'. Details: {e}"
        }


import subprocess
import json


def analyze_code_with_semgrep(project_id: str, repo: TraceRepository, commit_hash: str):
    """
    runs semgrep on the repository at a specific commit and returns the findings.
    """
    git_repo = get_repo(project_id, repo)
    if not git_repo:
        return {"error": "Git repository not found for this project."}

    repo_dir = os.path.join(REPO_CACHE_DIR, str(project_id))

    try:
        # checkout the specific commit
        git_repo.git.checkout(commit_hash, force=True)

        # run semgrep scan
        # using a general-purpose configuration
        config = "p/default"
        result = subprocess.run(
            ["semgrep", "scan", "--json", "--config", config],
            cwd=repo_dir,
            capture_output=True,
            text=True,
        )

        # checkout back to the main branch (or default)
        # assuming 'main' or 'master'
        try:
            git_repo.git.checkout("main", force=True)
        except git.exc.GitCommandError:
            git_repo.git.checkout("master", force=True)

        if result.returncode >= 2:  # semgrep returns >= 2 for critical errors
            return {"error": "Semgrep scan failed.", "details": result.stderr}

        findings = json.loads(result.stdout)
        return {"findings": findings["results"]}

    except git.exc.GitCommandError as e:
        return {"error": f"Could not checkout commit '{commit_hash}'. Details: {e}"}
    except json.JSONDecodeError:
        return {"error": "Failed to parse Semgrep JSON output."}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}
