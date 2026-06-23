# Releasing ticktick-mcp

This checklist covers the steps for publishing a new version to PyPI.
It is intended for maintainers; contributors do not need to follow it.

## 1. Pre-release checks

Run all local checks before tagging a release:

```bash
python -m compileall src
ruff check .
pytest
```

All three must pass with zero failures.

## 2. Bump the version

Edit `pyproject.toml` and update the `version` field:

```toml
version = "0.x.y"
```

Use [Semantic Versioning](https://semver.org/):

- **Patch** (`0.x.y+1`): bug fixes, doc updates, no new features.
- **Minor** (`0.x+1.0`): new features, backward-compatible.
- **Major** (`0+1.0.0`): breaking changes.

## 3. Build the distribution

```bash
python -m pip install --upgrade build
python -m build
```

This produces both a source distribution (`dist/*.tar.gz`) and a wheel
(`dist/*.whl`).

## 4. Upload to TestPyPI (optional but recommended)

Upload to TestPyPI first to verify the package installs cleanly:

```bash
python -m pip install --upgrade twine
python -m twine upload --repository testpypi dist/*
```

Verify in a clean virtual environment:

```bash
python -m venv /tmp/test-venv
source /tmp/test-venv/bin/activate
pip install --index-url https://test.pypi.org/simple/ ticktick-mcp==0.x.y
```

## 5. Upload to PyPI

```bash
python -m twine upload dist/*
```

## 6. Tag the release

```bash
git tag -a v0.x.y -m "Release v0.x.y"
git push upstream v0.x.y
```

## 7. Post-release

- Verify `pip install ticktick-mcp==0.x.y` works.
- Create a GitHub Release from the tag with a changelog summary.
- Update the `__version__` in `src/ticktick_mcp/__init__.py` to match.

## PyPI token safety

- Use a scoped **API token** from your PyPI account settings, not your password.
- Store the token in `~/.pypirc` or pass it via environment variable
  (`TWINE_PASSWORD`).
- **Never commit `.pypirc` or any file containing the token.**
- Rotate the token if you suspect it has been exposed.
