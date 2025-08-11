# Color definitions
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[0;33m
BLUE = \033[0;34m
MAGENTA = \033[0;35m
CYAN = \033[0;36m
WHITE = \033[0;37m
RESET = \033[0m

.PHONY: help install format test clean all

help:  ## Show this help message
	@echo "$(CYAN)Available commands:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)  %-15s$(RESET) %s\n", $$1, $$2}'

install:  ## Install dependencies
	@echo "$(BLUE)Installing dependencies...$(RESET)"
	poetry install
	@echo "$(GREEN)✓ Dependencies installed$(RESET)"

format:  ## Format code and run linting checks with ruff
	@echo "$(BLUE)Formatting code with ruff...$(RESET)"
	poetry run ruff format .
	@echo "$(GREEN)✓ Code formatted$(RESET)"
	@echo "$(BLUE)Running ruff linting checks with auto-fix...$(RESET)"
	poetry run ruff check . --fix
	@echo "$(GREEN)✓ Linting passed$(RESET)"

test:  ## Run all tests (unit + integration)
	@echo "$(BLUE)Running unit tests...$(RESET)"
	poetry run pytest -q
	@echo "$(GREEN)✓ Unit tests passed$(RESET)"
	@echo "$(BLUE)Running integration tests...$(RESET)"
	poetry run pytest -m integration
	@echo "$(GREEN)✓ Integration tests passed$(RESET)"

clean:  ## Clean up cache files and build artifacts
	@echo "$(BLUE)Cleaning up...$(RESET)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	rm -rf build/ dist/ htmlcov/ .tox/ .cache/ 2>/dev/null || true
	@echo "$(GREEN)✓ Cleanup complete$(RESET)"

all: install format test  ## Install deps, format code, and run tests
	@echo "$(GREEN)✓ All tasks completed$(RESET)"