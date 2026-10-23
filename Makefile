PYTHON ?= python3
UV_VERSION ?= $(shell awk '$$1 == "uv" {print $$2}' .tool-versions)
UV_BOOTSTRAP_DIR ?= .uv-venv
UV = $(shell command -v uv 2>/dev/null || printf '%s' "$(UV_BOOTSTRAP_DIR)/bin/uv")
UV_RUN = $(UV) run --locked

REDIS_CONTAINER := redis-test redis-sentinel-test

bootstrap-uv:
	@if ! "$(UV)" --version >/dev/null 2>&1; then \
		echo "Installing uv $(UV_VERSION) into $(UV_BOOTSTRAP_DIR)"; \
		$(PYTHON) -m pip install --disable-pip-version-check --upgrade \
			--target "$(UV_BOOTSTRAP_DIR)" "uv==$(UV_VERSION)"; \
	fi

setup: bootstrap-uv
	@$(UV) sync --locked
	@echo  "\n\nYou are strongly recommended to run 'make pre-commit'\n"

pre-commit:
	@$(UV_RUN) pre-commit install

run:
	@$(UV_RUN) remotecv

test: run-redis unit stop-redis

unit:
	@$(UV_RUN) pytest --cov=remotecv --cov-report term-missing --asyncio-mode=strict -s -r tests/

coverage:
	@$(UV_RUN) coverage report -m --fail-under=52
	@$(UV_RUN) coverage lcov

black:
	@$(UV_RUN) black . --config pyproject.toml

flake:
	@$(UV_RUN) flake8 --config .flake8

pylint:
	@$(UV_RUN) pylint remotecv tests

lint: black flake pylint

ci-test:
	@if [ "$$LINT_TEST" ]; then $(MAKE) flake; else $(MAKE) unit; fi

run-redis:
	@docker compose up -d $(REDIS_CONTAINER)

stop-redis:
	@docker compose stop $(REDIS_CONTAINER)
