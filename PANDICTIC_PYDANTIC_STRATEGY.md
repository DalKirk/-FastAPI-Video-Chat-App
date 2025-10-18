Pydantic Compatibility Strategy

Background:
- The project currently installs libraries that include Pydantic V1 compatibility layers which emit warnings on Python 3.14.

Options:
1) Short-term (recommended): pin Python to 3.12 or 3.13 in dev and CI. This avoids the compatibility warning with minimal code changes.

2) Medium-term: upgrade dependencies that require Pydantic V1 to versions compatible with Pydantic V2. Test the app under Python 3.14.

3) Long-term: migrate all models to Pydantic V2 idioms and ensure third-party dependencies are V2-ready.

Steps for migration:
- Run tests under Python 3.14 and capture failures/warnings.
- Replace Pydantic BaseModel imports to `from pydantic import BaseModel` and audit usages of `Config` and validators.
- Update any code using `validate_arguments` features or v1-only behaviors.
- Pin versions of libraries in `requirements.txt` and bump in small increments.

Recommendation: Pin python in CI to 3.12 while planning a migration to Pydantic V2 in the next milestone.
