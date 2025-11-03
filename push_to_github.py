#!/usr/bin/env python3
"""
Robust script to commit and push changes to GitHub (Windows-friendly)
"""
import subprocess
import sys
import os
from pathlib import Path


def run_git_command(args, cwd=None):
    """Run git command with credential manager and no prompts"""
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GIT_ASKPASS"] = "git-gui--askpass"

    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        return result
    except Exception as e:
        print(f"Error running git {' '.join(args)}: {e}")
        return None


def main():
    # Get repository root directory
    repo_dir = Path("C:/Users/g-kd/OneDrive/Desktop/My_FastAPI_Python")
    if not repo_dir.exists():
        print(f"Repository directory not found: {repo_dir}")
        sys.exit(1)

    print(f"Working in: {repo_dir}")

    # Setup Git credential manager
    run_git_command(["config", "--global", "credential.helper", "wincred"])

    # Stage all changes
    print("\nStaging changes...")
    stage = run_git_command(["add", "-A"], cwd=repo_dir)
    if stage and stage.returncode != 0:
        print(f"Failed to stage changes:\n{stage.stderr}")
        sys.exit(1)

    # Create commit
    print("\nCreating commit...")
    commit = run_git_command(
        [
            "commit",
            "-m",
            "feat(ai): add web-search and conversation features",
            "-m",
            "- Add Claude web search integration",
            "-m",
            "- Add conversation history support",
            "-m",
            "- Update AI endpoints with streaming",
        ],
        cwd=repo_dir,
    )

    if commit and "nothing to commit" in (commit.stdout + commit.stderr):
        print("No changes to commit")
    elif commit and commit.returncode != 0:
        print(f"Commit failed:\n{commit.stderr}")
        sys.exit(1)

    # Get current branch
    branch_result = run_git_command(["rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_dir)
    branch = "main" if not branch_result or branch_result.returncode != 0 else branch_result.stdout.strip()

    # Pull with rebase
    print(f"\nPulling latest changes from origin/{branch}...")
    pull = run_git_command(["pull", "--rebase", "origin", branch], cwd=repo_dir)
    if pull and pull.returncode != 0:
        print(f"Pull failed:\n{pull.stderr}")
        # Continue anyway - might be first push

    # Push changes
    print(f"\nPushing to origin/{branch}...")
    push = run_git_command(["push", "-u", "origin", branch], cwd=repo_dir)
    if push and push.returncode != 0:
        print(f"Push failed. Error:\n{push.stderr}")
        print("\nTroubleshooting steps:")
        print("1. Check GitHub credentials:")
        print("   git config --global credential.helper")
        print("2. Try authenticating:")
        print("   gh auth login")
        print("3. Push manually:")
        print(f"   git push -u origin {branch}")
        sys.exit(1)

    print("\nSuccess! Changes pushed to GitHub")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCanceled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
