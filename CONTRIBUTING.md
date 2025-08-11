# Contributing to poke-api-sdk

## Development Setup

1. Install Poetry: `curl -sSL https://install.python-poetry.org | python3 -`
2. Clone the repo: `git clone https://github.com/pprunty/poke-sdk.git`
3. Install dependencies: `poetry install`
4. Run tests: `poetry run pytest`

## Commit Message Format

This project uses [Conventional Commits](https://conventionalcommits.org/) for semantic versioning.

### Format
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types
- `feat`: A new feature (triggers minor version bump)
- `fix`: A bug fix (triggers patch version bump)
- `perf`: A code change that improves performance (triggers patch version bump)
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `test`: Adding missing tests or correcting existing tests
- `build`: Changes that affect the build system or external dependencies
- `ci`: Changes to our CI configuration files and scripts
- `chore`: Other changes that don't modify src or test files

### Examples

#### Features (minor version bump)
```
feat: add support for Pokemon generations API
feat(client): implement async de-duplication for requests
```

#### Bug fixes (patch version bump)
```
fix: handle 404 errors correctly in async client
fix(exceptions): map HTTP 429 to RateLimitError
```

#### Breaking changes (major version bump)
```
feat!: change default timeout from 10s to 30s

BREAKING CHANGE: The default timeout has been increased from 10 to 30 seconds to better handle slow network conditions.
```

### Scopes (optional)
- `api`: Changes to the API interface
- `client`: Changes to client classes
- `exceptions`: Changes to exception handling
- `tests`: Changes to test files
- `deps`: Changes to dependencies
- `config`: Changes to configuration files

## Release Process

Releases are automated using semantic versioning:

1. **Development**: Work on features and fixes in feature branches
2. **Pull Request**: Create a PR with a semantic commit title
3. **Merge**: When merged to `main`, GitHub Actions automatically:
   - Runs tests and linting
   - Analyzes commit messages
   - Bumps version based on semantic commits
   - Creates a GitHub release with changelog
   - Publishes to PyPI and TestPyPI

### Version Bumping
- `feat:` commits → minor version bump (0.1.0 → 0.2.0)
- `fix:`, `perf:` commits → patch version bump (0.1.0 → 0.1.1)
- `feat!:` or commits with `BREAKING CHANGE:` → major version bump (0.1.0 → 1.0.0)

## Testing

Run the test suite:
```bash
poetry run pytest                    # Basic tests
poetry run pytest --cov=poke_api    # With coverage
poetry run pytest -v                # Verbose output
```

## Code Quality

We use several tools to maintain code quality:

```bash
poetry run ruff check .              # Linting
poetry run ruff format .             # Code formatting
poetry run mypy src/poke_api         # Type checking
```

## PyPI Publishing

Publishing to PyPI is handled automatically by GitHub Actions when commits are pushed to `main`. The workflow:

1. Runs all tests and quality checks
2. Uses semantic commits to determine version bump
3. Publishes to TestPyPI first
4. If successful, publishes to PyPI
5. Creates GitHub release with auto-generated changelog

### Manual Publishing (if needed)

```bash
poetry build
poetry publish
```

## Project Structure

```
poke-sdk/
├── src/poke_api/          # Main package source
├── tests/                 # Test suite
├── examples/              # Usage examples
├── .github/workflows/     # CI/CD workflows
├── pyproject.toml         # Project configuration
├── CHANGELOG.md           # Auto-generated changelog
└── README.md              # Project documentation
```