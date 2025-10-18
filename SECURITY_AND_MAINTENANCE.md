Security and maintenance checklist

1) Secrets and keys
- Rotate Bunny API key immediately if it was ever committed to a remote repo.
- Do not keep secrets in plaintext in the repo; use environment variables and secret stores.
- If a secret was committed, use `git filter-repo` or BFG to remove it from history, then force-push and rotate the key.

Example commands to remove a file containing secrets with git-filter-repo:

powershell:

  # Install git-filter-repo if not available, then:
  git filter-repo --invert-paths --path .env

  # Force push cleaned history (only after coordinating with collaborators):
  git push --force --all
  git push --force --tags

Note: Use with caution — history rewrite affects all collaborators.

2) Secrets scanning
- Use tools like GitHub's secret scanning, truffleHog, or detect-secrets to scan the repo and CI. Add a scan step in CI.

3) Pydantic / Python compatibility
- Short-term: pin Python runtime to 3.12 or 3.13 in CI and deployments to avoid Pydantic V1 warnings.
- Long-term: upgrade to Pydantic V2-compatible dependencies and audit Pydantic usage.

4) Tests and CI
- Add GitHub Action to run tests on push and PRs. Use the included `requirements.txt` and venv creation in the job.

5) Other notes
- Use `python -m pip install -r requirements.txt` in the project's venv.
- Avoid `--reload` during production runs; for Windows dev, use the provided `run.py` and `run_server.ps1`.
