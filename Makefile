# Color definitions
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[0;33m
BLUE = \033[0;34m
MAGENTA = \033[0;35m
CYAN = \033[0;36m
WHITE = \033[0;37m
RESET = \033[0m

.PHONY: help install format test clean all example

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

test:  ## Run all tests with coverage
	@echo "$(BLUE)Running all tests with coverage...$(RESET)"
	poetry run pytest --cov=src/poke_api --cov-report=html --cov-report=term-missing
	@echo "$(GREEN)✓ All tests passed$(RESET)"
	@echo "$(YELLOW)Coverage report generated in htmlcov/index.html$(RESET)"

clean:  ## Clean up cache files and build artifacts
	@echo "$(BLUE)Cleaning up...$(RESET)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	rm -rf build/ dist/ htmlcov/ .tox/ .cache/ .coverage 2>/dev/null || true
	@echo "$(GREEN)✓ Cleanup complete$(RESET)"

example:  ## Run an example script (usage: make example <filename>)
	@if [ -z "$(filter-out $@,$(MAKECMDGOALS))" ]; then \
		echo "$(RED)Error: Please provide an example filename$(RESET)"; \
		echo "$(YELLOW)Usage: make example <filename>$(RESET)"; \
		echo "$(YELLOW)Examples:$(RESET)"; \
		echo "$(YELLOW)  make example list_pokemon_sync.py$(RESET)"; \
		echo "$(YELLOW)  make example examples/pokemon/get_pokemon_async.py$(RESET)"; \
		exit 1; \
	fi
	@FILENAME="$(filter-out $@,$(MAKECMDGOALS))"; \
	if [ -f "$$FILENAME" ]; then \
		echo "$(BLUE)Running example: $$FILENAME$(RESET)"; \
		poetry run python $$FILENAME; \
	elif [ -f "examples/pokemon/$$FILENAME" ]; then \
		echo "$(BLUE)Running Pokemon example: $$FILENAME$(RESET)"; \
		poetry run python examples/pokemon/$$FILENAME; \
	elif [ -f "examples/generation/$$FILENAME" ]; then \
		echo "$(BLUE)Running Generation example: $$FILENAME$(RESET)"; \
		poetry run python examples/generation/$$FILENAME; \
	else \
		echo "$(RED)Error: Example file '$$FILENAME' not found$(RESET)"; \
		echo "$(YELLOW)Available examples:$(RESET)"; \
		find examples/ -name "*.py" -type f | sort | sed 's/^/  - /'; \
		exit 1; \
	fi

# This prevents make from interpreting the filename argument as a target
%:
	@:

all: install format test  ## Install deps, format code, and run tests
	@echo "$(GREEN)✓ All tasks completed$(RESET)"