[![Coverage
Status](https://coveralls.io/repos/thumbor/remotecv/badge.svg?branch=master&service=github)](https://coveralls.io/github/thumbor/remotecv?branch=master)

# RemoteCV

RemoteCV is a background worker for OpenCV-based image detection. It is most
commonly used by [Thumbor][thumbor] to offload face and feature detection, but
it can also be integrated into any system that needs asynchronous image
analysis with cached results.

The worker supports:

- Redis + [PyRes][pyres] as the default queue backend
- [Celery][celery] with Amazon SQS
- Built-in OpenCV detectors for face, profile, glasses, feature, and combined
  detection
- Pluggable image loaders, metrics backends, and result stores
- Optional HTTP healthcheck endpoint

## Requirements

- Python `>=3.10,<3.15`
- Redis for the default backend and default result store
- OpenCV runtime dependencies supported by `opencv-python-headless`

If you want to run the Celery backend, install `celery` in the same
environment. The CLI supports it, but Celery is not part of the core runtime
dependencies installed by `pip install remotecv`.

## Installation

Install RemoteCV from PyPI:

```sh
pip install remotecv
```

For local development:

```sh
git clone https://github.com/thumbor/remotecv.git
cd remotecv
python -m venv .venv
. .venv/bin/activate
pip install -U pip
make setup
pre-commit install
```

## Running RemoteCV

The default worker uses the PyRes backend and connects to Redis on
`localhost:6379`:

```sh
remotecv
```

You can also use the Makefile shortcut:

```sh
make run
```

### Common examples

Start the default worker with a healthcheck endpoint:

```sh
remotecv --with-healthcheck --server-port=8888
```

Connect to a different Redis instance:

```sh
remotecv --host=redis.internal --port=6379 --database=1
```

Use Redis Sentinel mode:

```sh
remotecv \
  --redis-mode=sentinel \
  --sentinel-instances=sentinel-1:26379,sentinel-2:26379 \
  --master-instance=mymaster
```

Run with Celery + SQS (credentials come from the environment, see
[Secrets](#secrets)):

```sh
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...

remotecv \
  --backend=celery \
  --celery-commands=worker \
  --celery-commands=--loglevel=INFO
```

## Configuration

RemoteCV can be configured either by CLI flags or environment variables. These
are the options you are most likely to use:

| Purpose                         | CLI option                | Environment variable    | Default                                 |
| ------------------------------- | ------------------------- | ----------------------- | --------------------------------------- |
| Queue backend                   | `--backend`               | `BACKEND`               | `pyres`                                 |
| Redis host                      | `--host`                  | `REDIS_HOST`            | `localhost`                             |
| Redis port                      | `--port`                  | `REDIS_PORT`            | `6379`                                  |
| Redis mode                      | `--redis-mode`            | `REDIS_MODE`            | `single_node`                           |
| Redis TTL for stored detections | `--redis-key-expire-time` | `REDIS_KEY_EXPIRE_TIME` | `1209600`                               |
| Worker timeout                  | `--timeout`               | `DETECTOR_TIMEOUT`      | unset                                   |
| Worker TTL                      | `--worker-ttl`            | `WORKER_TTL`            | unset                                   |
| Result store backend            | `--store`                 | `DETECTOR_STORAGE`      | `remotecv.result_store.redis_store`     |
| Image loader                    | `--loader`                | `IMAGE_LOADER`          | `remotecv.http_loader`                  |
| Image fetch timeout (seconds)   | `--loader-timeout`        | `IMAGE_LOADER_TIMEOUT`  | `20.0`                                  |
| Image max size (bytes)          | `--loader-max-body-size`  | `IMAGE_LOADER_MAX_BODY_SIZE` | `0` (no limit)                     |
| Metrics backend                 | `--metrics`               | `METRICS_CLIENT`        | `remotecv.metrics.logger_metrics`       |
| Log level                       | `--level`                 | `LOG_LEVEL`             | `debug`                                 |
| Log format                      | `--format`                | `LOG_FORMAT`            | Python logging default for this project |
| Healthcheck bind address        | `--server-host`           | `HTTP_SERVER_HOST`      | `0.0.0.0`                               |
| Healthcheck port                | `--server-port`           | `HTTP_SERVER_PORT`      | `8080`                                  |
| Enable healthcheck              | `--with-healthcheck`      | `WITH_HEALTHCHECK`      | disabled                                |
| Sentry DSN                      | `--sentry-url`            | `SENTRY_URL`            | unset                                   |
| Clear image metadata            | `--clear-image-metadata`  | `CLEAR_IMAGE_METADATA`  | disabled                                |
| Max image pixels                | `--max-image-pixels`      | `MAX_IMAGE_PIXELS`      | `89478485` (Pillow default, 0 disables) |
| Memcached hosts                 | `--memcached-hosts`       | `MEMCACHED_HOSTS`       | `localhost:11211`                       |

### Secrets

Every option that carries a secret also has an environment variable, and
that is the form to use for it:

| Secret                         | Environment variable      | CLI option (avoid)    |
| ------------------------------ | ------------------------- | --------------------- |
| Redis password                 | `REDIS_PASSWORD`          | `--password`          |
| Redis Sentinel password        | `REDIS_SENTINEL_PASSWORD` | `--sentinel-password` |
| Redis Sentinel master password | `REDIS_MASTER_PASSWORD`   | `--master-password`   |
| AWS secret access key          | `AWS_SECRET_ACCESS_KEY`   | `--key-secret`        |

A value passed on the command line is visible to every user on the host
through `ps` and `/proc`, and is often captured verbatim by process
supervisors and container orchestrators in their own logs. A process's
environment is only readable by its owner and root. Under an orchestrator,
inject the variables from its secret store rather than writing the values
into the manifest, where everyone who can read the manifest sees them.
Running `--help` with the variables set is safe: `show_envvar` prints the
variable name, never its value.

### Built-in detectors

`ImageProcessor` ships with the following detector names:

- `face`
- `feature`
- `glass`
- `profile`
- `all`

You can combine detectors with `+` in queued jobs, for example `face+profile`.

## Result storage

By default, detection results are stored in Redis using the key pattern
`thumbor-detector-<key>`.

RemoteCV also includes a Memcached-backed result store implementation in
`remotecv.result_store.memcache_store`. If you use it, make sure the
appropriate Memcached client dependency is installed in your environment.

## Development workflow

Run unit tests:

```sh
make unit
```

Run the full local test flow with Redis containers:

```sh
make test
```

Start and stop the test Redis/Sentinel stack manually:

```sh
make run-redis
make stop-redis
```

Run code quality checks:

```sh
make black
make flake
make pylint
make lint
```

## Project layout

```text
remotecv/
  worker.py             CLI entry point and runtime configuration
  image_processor.py    Detector orchestration
  image.py              Image parsing and normalization
  http_loader.py        Remote image loading
  unique_queue.py       PyRes worker implementation
  celery_tasks.py       Celery/SQS integration
  detectors/            OpenCV detectors and cascade files
  metrics/              Metrics backends
  result_store/         Detection result store implementations
tests/
  fixtures/             Sample images and Redis/Sentinel fixtures
```

## Security

Please do not report security issues in public issues. See
[SECURITY.md](SECURITY.md) for the recommended disclosure process.

[thumbor]: https://github.com/thumbor/thumbor/wiki
[pyres]: https://github.com/binarydud/pyres
[celery]: https://www.celeryproject.org/
