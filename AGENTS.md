# AGENTS.md

remotecv is a Python worker service that performs OpenCV-based image
detection jobs outside the main application flow. It is commonly used by
thumbor to offload face and feature detection, but it can also be integrated
into other systems. The worker supports Redis/PyRes and Celery/SQS backends,
optional healthchecks, and pluggable metrics/result stores.

## Dev environment setup

- **Prerequisites:** Python 3.9+, Redis, and Docker Compose for the local
  Redis/Sentinel test stack.
- Install the project in editable mode with development dependencies:

  ```
  make setup
  ```

  Equivalent to: `pip install -Ue .[dev]`

- Install pre-commit hooks once after setup:

  ```
  pre-commit install
  ```

## Running locally

- Start the default worker:

  ```
  make run
  ```

- The package also exposes a CLI entry point:

  ```
  remotecv
  ```

- Useful runtime variants:

  ```
  remotecv --with-healthcheck --server-port=8888
  remotecv --backend=pyres
  remotecv --backend=celery
  ```

- Redis/PyRes is the default backend. Celery mode expects AWS/SQS-related
  environment variables such as `AWS_REGION`, `AWS_ACCESS_KEY_ID`, and
  `AWS_SECRET_ACCESS_KEY`.

## Running tests

- Full local test flow with Redis containers:

  ```
  make test
  ```

- Unit tests only:

  ```
  make unit
  ```

- Start and stop the local Redis/Sentinel stack manually when needed:

  ```
  make run-redis
  make stop-redis
  ```

- The Docker Compose test stack exposes Redis on `6379` and Sentinel fixtures
  on `26379` and `26380`.

## Code style

- **Formatter:** `black` using [pyproject.toml](/home/metal/work/remotecv/pyproject.toml).
  Run with `make black`.
- **Linter:** `flake8` using [.flake8](/home/metal/work/remotecv/.flake8).
  Run with `make flake`.
- **Static analysis:** `pylint` using [.pylintrc](/home/metal/work/remotecv/.pylintrc).
  Run with `make pylint`.
- Combined lint target:

  ```
  make lint
  ```

- Pre-commit also enforces trailing whitespace, final newlines, YAML validity,
  `black`, `flake8`, and `pylint`.

## Project structure

```
remotecv/                     <- main package
  worker.py                   <- CLI entry point and backend/bootstrap wiring
  image_processor.py          <- detector orchestration
  image.py                    <- image loading and normalization helpers
  http_loader.py              <- remote image fetching
  unique_queue.py             <- PyRes worker implementation
  celery_tasks.py             <- Celery/SQS worker integration
  error_handler.py            <- Sentry/error handling integration
  healthcheck.py              <- optional HTTP healthcheck handler
  importer.py                 <- dynamic class loading utilities
  detectors/                  <- built-in OpenCV detectors and cascade data
  metrics/                    <- metrics backends
  result_store/               <- result store implementations
  storages/                   <- storage helpers
tests/                        <- pytest suite
tests/fixtures/               <- image and Redis/Sentinel fixtures
docker/                       <- image/build support
docker-compose.yaml           <- local Redis/Sentinel test stack
Makefile                      <- primary task runner
```

## Contribution guidelines

- Keep changes focused and add or update tests when behavior changes.
- Prefer using the Makefile targets over ad hoc commands so local and CI flows
  stay aligned.
- When changing worker startup, CLI flags, or environment-variable handling,
  update [README.md](/home/metal/work/remotecv/README.md) as part of the same
  change.
- Be careful with detector fixtures and large binary files; reuse existing test
  assets unless a new fixture is necessary.

## Operational notes

- `remotecv` can expose a healthcheck endpoint, but it is off by default.
- Image-processing dependencies such as Pillow and OpenCV are security- and
  stability-sensitive; keep them updated when touching packaging.
- Restrict access to Redis/SQS and any healthcheck port in production.
- If you modify queueing or result-storage behavior, validate both the runtime
  code and the corresponding tests (`test_pyres_tasks.py`,
  `test_redis.py`, `test_result_store.py`, `test_redis_storage.py`).
