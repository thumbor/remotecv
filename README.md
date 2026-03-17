[![Coverage
Status](https://coveralls.io/repos/thumbor/remotecv/badge.svg?branch=master&service=github)](https://coveralls.io/github/thumbor/remotecv?branch=master)

# RemoteCV

RemoteCV is a background worker for OpenCV-based image detection. It is most
commonly used by [Thumbor][thumbor] to offload face and feature detection, but
it can also be integrated into any system that needs asynchronous image
analysis with cached results.

The worker uses [Celery][celery] and supports:

- Redis or Amazon SQS as the Celery broker
- Built-in OpenCV detectors for face, profile, glasses, feature, and combined
  detection
- Pluggable image loaders, metrics backends, and result stores
- Optional HTTP healthcheck endpoint

## Upgrading from 5.x to 6.0

Version 6.0 is a breaking release. The following changes are required if you
are upgrading from 5.x:

- **PyRes removed.** The PyRes queue backend has been replaced by Celery.
  The `--backend` option no longer exists. All workers now run via Celery.
- **`--broker` is now required to select the broker.** Use `--broker=redis`
  (or `CELERY_BROKER=redis`) to use Redis, or `--broker=sqs` for Amazon SQS.
  The default remains `sqs` for backwards compatibility with deployments that
  relied on the old Celery/SQS mode.
- **SQS-specific flags are unchanged.** `--region`, `--key-id`,
  `--key-secret`, and `--polling-interval` continue to work as before when
  `--broker=sqs` is used.
- **`--celery-commands` default changed.** If `--celery-commands` is not
  provided, `worker` is used automatically. Previously omitting it caused the
  worker to fail to start.

## Requirements

- Python `>=3.10,<3.15`
- Redis for the unique job queue and default result store
- OpenCV runtime dependencies supported by `opencv-python-headless`

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

### Redis broker (default for local use)

Start the worker using Redis as the Celery broker (connects to
`localhost:6379` by default):

```sh
remotecv --broker=redis
```

With a specific Redis host and database:

```sh
remotecv --broker=redis --host=redis.internal --port=6379 --database=1
```

With Redis Sentinel:

```sh
remotecv \
  --broker=redis \
  --redis-mode=sentinel \
  --sentinel-instances=sentinel-1:26379,sentinel-2:26379 \
  --master-instance=mymaster
```

### SQS broker

```sh
remotecv \
  --broker=sqs \
  --region=us-east-1 \
  --key-id="$AWS_ACCESS_KEY_ID" \
  --key-secret="$AWS_SECRET_ACCESS_KEY"
```

### With healthcheck endpoint

```sh
remotecv --broker=redis --with-healthcheck --server-port=8888
```

### Passing extra Celery arguments

Use `--celery-commands` (repeatable) to forward arguments to the Celery
worker. When omitted, `worker` is used by default:

```sh
remotecv --broker=redis --celery-commands=worker --celery-commands=--concurrency=4
```

## Configuration

RemoteCV can be configured either by CLI flags or environment variables.

### Redis connection

| Purpose                            | CLI option                  | Environment variable          | Default            |
| ---------------------------------- | --------------------------- | ----------------------------- | ------------------ |
| Redis host                         | `--host`                    | `REDIS_HOST`                  | `localhost`        |
| Redis port                         | `--port`                    | `REDIS_PORT`                  | `6379`             |
| Redis database                     | `--database`                | `REDIS_DATABASE`              | `0`                |
| Redis password                     | `--password`                | `REDIS_PASSWORD`              | unset              |
| Redis mode                         | `--redis-mode`              | `REDIS_MODE`                  | `single_node`      |
| Redis TTL for dedup keys           | `--redis-key-expire-time`   | `REDIS_KEY_EXPIRE_TIME`       | `1209600`          |
| Sentinel instances                 | `--sentinel-instances`      | `REDIS_SENTINEL_INSTANCES`    | `localhost:26376`  |
| Sentinel password                  | `--sentinel-password`       | `REDIS_SENTINEL_PASSWORD`     | unset              |
| Sentinel master name               | `--master-instance`         | `REDIS_MASTER_INSTANCE`       | unset              |
| Sentinel master password           | `--master-password`         | `REDIS_MASTER_PASSWORD`       | unset              |
| Sentinel master database           | `--master-database`         | `REDIS_MASTER_DATABASE`       | `0`                |
| Sentinel socket timeout            | `--socket-timeout`          | `REDIS_SENTINEL_SOCKET_TIMEOUT` | `10.0`           |

### Celery broker

| Purpose                            | CLI option                  | Environment variable          | Default            |
| ---------------------------------- | --------------------------- | ----------------------------- | ------------------ |
| Broker backend                     | `--broker`                  | `CELERY_BROKER`               | `sqs`              |
| Extra Celery arguments             | `--celery-commands`         | `CELERY_COMMANDS`             | `worker`           |

#### SQS-specific options

| Purpose                            | CLI option                  | Environment variable          | Default            |
| ---------------------------------- | --------------------------- | ----------------------------- | ------------------ |
| AWS region                         | `--region`                  | `AWS_REGION`                  | `us-east-1`        |
| AWS access key ID                  | `--key-id`                  | `AWS_ACCESS_KEY_ID`           | unset              |
| AWS access key secret              | `--key-secret`              | `AWS_SECRET_ACCESS_KEY`       | unset              |
| SQS polling interval               | `--polling-interval`        | `SQS_POLLING_INTERVAL`        | `20`               |

### Other options

| Purpose                            | CLI option                  | Environment variable          | Default                             |
| ---------------------------------- | --------------------------- | ----------------------------- | ----------------------------------- |
| Detection timeout                  | `--timeout`                 | `DETECTOR_TIMEOUT`            | unset                               |
| Result store backend               | `--store`                   | `DETECTOR_STORAGE`            | `remotecv.result_store.redis_store` |
| Image loader                       | `--loader`                  | `IMAGE_LOADER`                | `remotecv.http_loader`              |
| Metrics backend                    | `--metrics`                 | `METRICS_CLIENT`              | `remotecv.metrics.logger_metrics`   |
| Log level                          | `--level`                   | `LOG_LEVEL`                   | `debug`                             |
| Log format                         | `--format`                  | `LOG_FORMAT`                  | Python logging default              |
| Healthcheck port                   | `--server-port`             | `HTTP_SERVER_PORT`            | `8080`                              |
| Enable healthcheck                 | `--with-healthcheck`        | `WITH_HEALTHCHECK`            | disabled                            |
| Sentry DSN                         | `--sentry-url`              | `SENTRY_URL`                  | unset                               |
| Clear image metadata               | `--clear-image-metadata`    | `CLEAR_IMAGE_METADATA`        | disabled                            |
| Memcached hosts                    | `--memcached-hosts`         | `MEMCACHED_HOSTS`             | `localhost:11211`                   |

## Built-in detectors

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

RemoteCV also includes a Memcached-backed result store in
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
make lint
```

## Project layout

```text
remotecv/
  worker.py             CLI entry point and runtime configuration
  celery_tasks.py       Celery broker integration (Redis and SQS)
  image_processor.py    Detector orchestration
  image.py              Image parsing and normalization
  http_loader.py        Remote image loading
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
[celery]: https://www.celeryproject.org/
