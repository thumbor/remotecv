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
- **`--broker` selects the Celery broker.** It defaults to `redis`, the
  closest match to the old PyRes default. Deployments that used
  `--backend=celery` must pass `--broker=sqs` (or `CELERY_BROKER=sqs`). The
  worker refuses to start while the old `BACKEND` variable is set, so a stale
  setting cannot silently select the wrong broker.
- **SQS-specific flags are unchanged.** `--region`, `--key-id`,
  `--key-secret`, and `--polling-interval` continue to work as before when
  `--broker=sqs` is used. The SQS transport needs the `sqs` extra
  (`pip install 'remotecv[sqs]'`); the Docker image already includes it.
- **`--celery-commands` default changed.** If `--celery-commands` is not
  provided, `worker` is used automatically. Previously omitting it caused the
  worker to fail to start.
- **PyRes-only options removed.** `--worker-ttl` (`WORKER_TTL`) and
  `--prune-dead-members` (`PRUNE_DEAD_MEMBERS`) no longer exist. Remove them
  from your command line; the environment variables are ignored.
- **Metrics renamed.** `worker.pyres_task.time` and `worker.pyres_task.total`
  are now `worker.task.time` and `worker.task.total`, and
  `worker.read_queue.time` is no longer emitted. Update dashboards and alerts
  that use them.
- **Producers must move to Celery too.** Workers no longer read the PyRes
  `Detect` queue, so jobs enqueued by 5.x producers (thumbor's
  `QueuedDetector` or `remotecv.unique_queue.UniqueQueue`) stay in Redis
  unprocessed. Drain that queue before switching. `CeleryTasks` now takes a
  broker URL instead of AWS credentials. See
  [Enqueuing detection jobs](#enqueuing-detection-jobs).

## Requirements

- Python `>=3.11,<3.16`
- Redis for the default broker and result store, and for de-duplicating jobs
  enqueued with `enqueue_unique`
- OpenCV runtime dependencies supported by `opencv-python-headless`

## Installation

Install RemoteCV from PyPI:

```sh
pip install remotecv
```

The SQS broker needs boto3, which comes with the `sqs` extra:

```sh
pip install 'remotecv[sqs]'
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

### Redis broker (default)

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

Credentials come from the environment, see [Secrets](#secrets):

```sh
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...

remotecv --broker=sqs
```

`--key-id` and `--key-secret` must be given together. Leave both unset to let
boto3 resolve credentials on its own, for example from an instance profile or
an ECS task role.

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

## Enqueuing detection jobs

Producers enqueue jobs through `remotecv.celery_tasks.CeleryTasks`, pointing
at the same broker as the worker. `enqueue_unique` skips a key that is already
queued. It needs a `CeleryUniqueQueue` backed by the same Redis database the
worker is configured with, because the worker releases the key when it picks
up the job:

```python
from redis import Redis

from remotecv.celery_tasks import CeleryTasks, CeleryUniqueQueue

tasks = CeleryTasks(
    "redis://localhost:6379/0",
    unique_queue=CeleryUniqueQueue(Redis(host="localhost", port=6379, db=0)),
)
tasks.enqueue_unique("all", image_url, image_url)
```

For SQS (with the `sqs` extra installed), `build_sqs_broker` returns the
broker URL and transport options the worker uses, including the
`celery-remotecv-` queue prefix:

```python
from remotecv.celery_tasks import CeleryTasks, build_sqs_broker

tasks = CeleryTasks(*build_sqs_broker(key_id, key_secret, "us-east-1"))
tasks.get_detect_task().delay("all", image_url, image_url)
```

`CeleryUniqueQueue` keeps each key for 14 days by default. Pass
`expire_time` (in seconds) to change it.

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
| Redis TTL for stored detections    | `--redis-key-expire-time`   | `REDIS_KEY_EXPIRE_TIME`       | `1209600`          |
| Sentinel instances                 | `--sentinel-instances`      | `REDIS_SENTINEL_INSTANCES`    | `localhost:26376`  |
| Sentinel password                  | `--sentinel-password`       | `REDIS_SENTINEL_PASSWORD`     | unset              |
| Sentinel master name               | `--master-instance`         | `REDIS_MASTER_INSTANCE`       | unset              |
| Sentinel master password           | `--master-password`         | `REDIS_MASTER_PASSWORD`       | unset              |
| Sentinel master database           | `--master-database`         | `REDIS_MASTER_DATABASE`       | `0`                |
| Sentinel socket timeout            | `--socket-timeout`          | `REDIS_SENTINEL_SOCKET_TIMEOUT` | `10.0`           |

### Celery broker

| Purpose                            | CLI option                  | Environment variable          | Default            |
| ---------------------------------- | --------------------------- | ----------------------------- | ------------------ |
| Broker backend                     | `--broker`                  | `CELERY_BROKER`               | `redis`            |
| Extra Celery arguments             | `--celery-commands`         | `CELERY_COMMANDS`             | `worker`           |

#### SQS-specific options

| Purpose                            | CLI option                  | Environment variable          | Default            |
| ---------------------------------- | --------------------------- | ----------------------------- | ------------------ |
| AWS region                         | `--region`                  | `AWS_REGION`                  | `us-east-1`        |
| AWS access key ID                  | `--key-id`                  | `AWS_ACCESS_KEY_ID`           | unset              |
| AWS access key secret              | `--key-secret`              | `AWS_SECRET_ACCESS_KEY`       | unset              |
| SQS polling interval               | `--polling-interval`        | `SQS_POLLING_INTERVAL`        | `20`               |

### Other options

| Purpose                            | CLI option                  | Environment variable          | Default                                 |
| ---------------------------------- | --------------------------- | ----------------------------- | --------------------------------------- |
| Detection timeout                  | `--timeout`                 | `DETECTOR_TIMEOUT`            | unset                                   |
| Result store backend               | `--store`                   | `DETECTOR_STORAGE`            | `remotecv.result_store.redis_store`     |
| Image loader                       | `--loader`                  | `IMAGE_LOADER`                | `remotecv.http_loader`                  |
| Image fetch timeout (seconds)      | `--loader-timeout`          | `IMAGE_LOADER_TIMEOUT`        | `20.0`                                  |
| Image max size (bytes)             | `--loader-max-body-size`    | `IMAGE_LOADER_MAX_BODY_SIZE`  | `0` (no limit)                          |
| Image fetch User-Agent             | `--loader-user-agent`       | `IMAGE_LOADER_USER_AGENT`     | `remotecv/<version>`                    |
| Metrics backend                    | `--metrics`                 | `METRICS_CLIENT`              | `remotecv.metrics.logger_metrics`       |
| Log level                          | `--level`                   | `LOG_LEVEL`                   | `debug`                                 |
| Log format                         | `--format`                  | `LOG_FORMAT`                  | Python logging default                  |
| Healthcheck bind address           | `--server-host`             | `HTTP_SERVER_HOST`            | `0.0.0.0`                               |
| Healthcheck port                   | `--server-port`             | `HTTP_SERVER_PORT`            | `8080`                                  |
| Enable healthcheck                 | `--with-healthcheck`        | `WITH_HEALTHCHECK`            | disabled                                |
| Sentry DSN                         | `--sentry-url`              | `SENTRY_URL`                  | unset                                   |
| Clear image metadata               | `--clear-image-metadata`    | `CLEAR_IMAGE_METADATA`        | disabled                                |
| Max image pixels                   | `--max-image-pixels`        | `MAX_IMAGE_PIXELS`            | `89478485` (Pillow default, 0 disables) |
| Memcached hosts                    | `--memcached-hosts`         | `MEMCACHED_HOSTS`             | `localhost:11211`                       |

Sentry events are tagged with the release `remotecv@<version>` unless the SDK
detects one on its own, for example from `SENTRY_RELEASE`, the git revision or
a platform variable such as `HEROKU_SLUG_COMMIT`.

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
