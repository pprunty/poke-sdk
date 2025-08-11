# Contributing to poke-sdk

## Development Setup

1. Install Poetry: `curl -sSL https://install.python-poetry.org | python3 -`
2. Clone and install: `git clone https://github.com/pprunty/poke-sdk.git && cd poke-sdk && poetry install`
3. Run tests: `poetry run pytest`

## Commit Format

Use [Conventional Commits](https://conventionalcommits.org/) for automatic versioning:

- `feat:` - New feature (minor bump)
- `fix:` - Bug fix (patch bump) 
- `feat!:` or `BREAKING CHANGE:` - Breaking change (major bump)

Examples:
```
feat: add Pokemon search functionality
fix: handle 404 errors correctly
```

## Development

```bash
poetry run pytest              # Run tests
poetry run ruff check .        # Lint code
poetry run ruff format .       # Format code
```

Releases are automated via GitHub Actions when PRs are merged to `main`.