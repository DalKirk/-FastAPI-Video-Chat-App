#!/usr/bin/env python3
"""
Robust script to commit and push changes to GitHub (non-interactive friendly)
"""
import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description, timeout=180):
    """Run a command, print output, and return (ok, stdout, stderr, rc)."""
    print(f"\n{'='*60}")
    print(f"??  {description}")
    print(f"$ {cmd}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        if result.stdout:
            print(result.stdout.rstrip())
        if result.stderr:
            print(f"??  Stderr: {result.stderr.rstrip()}")

        ok = result.returncode == 0
        if ok:
            print(f"? {description} - Success!")
        else:
            print(f"? {description} failed with return code {result.returncode}")
        return ok, result.stdout, result.stderr, result.returncode

    except subprocess.TimeoutExpired:
        print(f"? Command timed out after {timeout} seconds")
        return False, "", "timeout", -1
    except Exception as e:
        print(f"? Error: {e}")
        return False, "", str(e), -1


def main():
    print("\n" + "=" * 60)
    print("?? GitHub Push Script")
    print("=" * 60)

    # Ensure we run from the repo root (directory of this script)
    repo_root = Path(__file__).resolve().parent
    os.chdir(repo_root)
    print(f"?? Working directory: {repo_root}")

    # Step 1: Show status and remotes
    run_command("git status", "Checking git status")
    run_command("git remote -v", "Listing remotes")

    # Step 2: Stage ALL changes (new, modified, deleted)
    run_command("git add -A", "Staging all changes")

    # Step 3: Show what will be committed
    run_command("git diff --cached --name-only", "Files staged for commit")

    # Step 4: Commit changes (continue even if there's nothing to commit)
    commit_message = (
        "Update: AI service and related changes.\n"
        "- Ensure markdown handling and search flag wiring\n"
        "- Push script robustness: stage all, non-interactive, rebase before push"
    )
    ok, out, err, rc = run_command(
        f'git commit -m "{commit_message}"',
        "Creating commit",
        timeout=60,
    )

    if not ok:
        # Proceed if there's nothing to commit
        if (
            "nothing to commit" in (out + err).lower()
            or "no changes added to commit" in (out + err).lower()
        ):
            print("??  No changes to commit; continuing to push any existing commits...")
        else:
            print("??  Commit failed for another reason; attempting to continue...")

    # Step 5: Detect current branch (fallback to 'main')
    ok_branch, out_branch, _, _ = run_command(
        "git rev-parse --abbrev-ref HEAD",
        "Detecting current branch",
        timeout=30,
    )
    branch = (out_branch.strip() if ok_branch and out_branch.strip() else "main")
    print(f"?? Current branch: {branch}")

    # Step 6: Rebase latest from origin to avoid non-fast-forward errors
    run_command(f"git pull --rebase origin {branch}", "Rebasing latest from origin")

    # Step 7: Push to GitHub (set upstream if needed)
    print("\n" + "=" * 60)
    print("?? Pushing to GitHub...")
    print("=" * 60)

    ok_push, out_push, err_push, _ = run_command(
        f"git push -u origin {branch}",
        f"Pushing to origin/{branch}",
        timeout=240,
    )

    if ok_push:
        print("\n" + "=" * 60)
        print("? SUCCESS! Changes pushed to GitHub")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("? Push failed")
        print("\nPossible reasons:")
        print("  • Authentication required (use Git Credential Manager or gh CLI)")
        print("  • Network issues or VPN")
        print("  • Branch protection rules")
        print("  • Remote changes need to be pulled first")
        print("\n?? Try: git pull --rebase origin {branch} && git push -u origin {branch}")
        print("=" * 60)
        # Surface stderr for CI logs
        if err_push:
            print(f"\n?? git push stderr:\n{err_push}")
        sys.exit(1)

    print("\n?? All done!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n? Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n? Unexpected error: {e}")
        sys.exit(1)
