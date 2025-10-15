import os
import tempfile
import shutil
from git import Repo
from config.logger import setup_logger
from trasnsformers.transform import transform_code

logger, _ = setup_logger()


def detect_repo_url(ci: str, repo: str):
    if os.path.exists(repo):
        return repo

    if not ci:
        logger.warning("No CI provider specified — defaulting to GitHub SSH")
        ci = "GitHub"

    ci = ci.lower()

    if ci == "github":
        return f"git@github.com:{repo}.git"
    elif ci == "gitlab":
        return f"git@gitlab.com:{repo}.git"
    elif ci == "bitbucket":
        return f"git@bitbucket.org:{repo}.git"
    elif ci == "azuredevops":
        if repo.startswith("https://"):
            return repo
        return f"https://dev.azure.com/{repo}"
    elif ci == "bamboo":
        return f"git@bitbucket.org:{repo}.git"
    elif ci == "circleci":
        return f"git@github.com:{repo}.git"
    else:
        return f"git@github.com:{repo}.git"


def build_branch_url(ci: str, repo: str, branch: str):
    if not repo or os.path.exists(repo):
        return None

    ci = (ci or "GitHub").lower()

    if ci == "github":
        return f"https://github.com/{repo}/tree/{branch}"
    elif ci == "gitlab":
        return f"https://gitlab.com/{repo}/-/tree/{branch}"
    elif ci == "bitbucket":
        return f"https://bitbucket.org/{repo}/src/{branch}"
    elif ci == "azuredevops":
        return f"{repo}?version=GB{branch}"
    elif ci == "bamboo":
        return None
    elif ci == "circleci":
        return f"https://github.com/{repo}/tree/{branch}"
    else:
        return None


def run_refactor(
    repo: str,
    ref: str = "main",
    rules=None,
    output_dir: str = None,
    ci: str = None,
    run_id: str = None,
    workflow_name: str = None,
    workflow_id: str = None,
    commit_hash: str = None,
):
    logger.info(f"[CI={ci}] Starting refactor for repo: {repo} on branch: {ref}")

    empty_result = {
        "branch_url": None,
        "transformations": [],
        "base_commit_sha": None,
        "refactor_commit_sha": None,
        "new_branch": None,
        "message": None,
        "output_dir": output_dir,
    }

    if not rules:
        logger.info("No transformation rules specified: skipping refactor")
        empty_result["message"] = "No transformation rules provided; no refactor performed"
        return empty_result

    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix="greencoderefactor_output_")
        logger.info(f"No output_dir provided. Using temporary directory: {output_dir}")
    else:
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Using provided output directory: {output_dir}")

    if os.path.exists(repo):
        repo_dir = repo
        repo_obj = Repo(repo_dir)
        logger.info(f"Using existing local repository: {repo}")
    else:
        repo_url = detect_repo_url(ci, repo)
        logger.info(f"Cloning repository from {repo_url}")
        repo_dir = tempfile.mkdtemp(prefix="repo_")
        repo_obj = Repo.clone_from(repo_url, repo_dir, branch=ref)

    transformations = []
    any_changes = False

    for root, _, files in os.walk(repo_dir):
        for fname in files:
            if fname.endswith(".py"):
                full_path_repo = os.path.join(root, fname)
                rel_path = os.path.relpath(full_path_repo, repo_dir)
                output_path = os.path.join(output_dir, rel_path)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                logger.info(f"Transforming file: {full_path_repo}")
                result = transform_code(full_path_repo, output_path, rules)
                if result and result.get("changed"):
                    any_changes = True
                transformations.append(result)

    if not any_changes:
        logger.info("No code changes detected: skipping branch creation, commit and push")
        empty_result["message"] = "No code changes detected; no new branch or commit performed"
        empty_result["transformations"] = transformations
        return empty_result

    new_branch = f"GREENCODEREFACTOR_from_{ref}"
    try:
        new_branch_ref = repo_obj.heads[new_branch]
        logger.info(f"Branch {new_branch} exists, checking out to update it")
        new_branch_ref.checkout()
    except IndexError:
        logger.info(f"Branch {new_branch} does not exist, creating it")
        new_branch_ref = repo_obj.create_head(new_branch, commit=ref)
        new_branch_ref.checkout()

    for root, _, files in os.walk(output_dir):
        for fname in files:
            full_path_output = os.path.join(root, fname)
            rel_path = os.path.relpath(full_path_output, output_dir)
            full_path_repo = os.path.join(repo_dir, rel_path)
            os.makedirs(os.path.dirname(full_path_repo), exist_ok=True)
            shutil.copy2(full_path_output, full_path_repo)

    base_commit_sha = repo_obj.commit(ref).hexsha
    repo_obj.git.add(A=True)
    repo_obj.index.commit(f"Auto refactor from {workflow_name or 'GreencodeRefactor'} ({ci or 'local'})")
    new_commit_sha = repo_obj.commit(new_branch).hexsha

    logger.info(f"Pushing branch {new_branch} via SSH/HTTPS")
    repo_obj.remote(name="origin").push(refspec=f"{new_branch}:{new_branch}")

    branch_url = build_branch_url(ci, repo, new_branch)
    logger.info(f"Refactor completed successfully. New branch: {branch_url or new_branch}")

    return {
        "branch_url": branch_url,
        "transformations": transformations,
        "base_commit_sha": base_commit_sha,
        "refactor_commit_sha": new_commit_sha,
        "new_branch": new_branch,
        "message": "Refactor completed successfully",
        "output_dir": output_dir,
    }
