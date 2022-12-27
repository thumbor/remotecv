[![Coverage
Status](https://coveralls.io/repos/thumbor/remotecv/badge.svg?branch=master&service=github)](https://coveralls.io/github/thumbor/remotecv?branch=master)

# RemoteCV

RemoteCV is a queued mechanism to run [OpenCV][opencv] computations and store
them for later usage.

Currently, [Thumbor][thumbor] uses remotecv to outsource facial or feature
detection, but nothing stops you from integrating it into your product.

RemoteCV supports both [PyRes][PyRes] and [Celery][Celery] for queueing
back-end.

## Install

```sh
pip install remotecv
```

## Run local

Clone the repository:

```sh
git clone https://github.com/thumbor/remotecv.git
```

Create a virtualenv:

```
cd remotecv
mkvirtualenv remotecv
```

Install dependencies:

```sh
make setup
```

Run:

```sh
make run
```

After installing the project, you can execute

```sh
remotecv
```

If you want a healthcheck handler, you must pass an argument in remotecv
execution. You can also specify the http server port, the default http server
port is 8080.

```sh
remotecv --with-healthcheck --server-port=8888
```

## Tests

```sh
make unit
```

## RemoveCV parameters
```sh
Usage: remotecv [OPTIONS]

  Runs RemoteCV

Options:
  Worker Backend:
    -b, --backend [pyres|celery]  Worker backend  [env var: BACKEND]
  Pyres Connection Arguments:
    --host TEXT                   Redis host  [env var: REDIS_HOST]
    --port INTEGER                Redis port  [env var: REDIS_PORT]
    --database INTEGER            Redis database  [env var: REDIS_DATABASE]
    --password TEXT               Redis password  [env var: REDIS_PASSWORD]
    --redis-mode [single_node|sentinel]
                                  Redis mode  [env var: REDIS_MODE]
    --sentinel-instances TEXT     Redis Sentinel instances e.g.
                                  'localhost:26376,localhost:26377'  [env var:
                                  REDIS_SENTINEL_INSTANCES]
    --sentinel-password TEXT      Redis Sentinel password  [env var:
                                  REDIS_SENTINEL_PASSWORD]
    --master-instance TEXT        Redis Sentinel master instance  [env var:
                                  REDIS_MASTER_INSTANCE]
    --master-password TEXT        Redis Sentinel master password  [env var:
                                  REDIS_MASTER_PASSWORD]
    --master-database INTEGER     Redis Sentinel master database  [env var:
                                  REDIS_MASTER_DATABASE]
    --socket-timeout FLOAT        Redis Sentinel socket timeout  [env var:
                                  REDIS_SENTINEL_SOCKET_TIMEOUT]
  Celery/SQS Connection Arguments:
    --region TEXT                 AWS SQS Region  [env var: AWS_REGION]
    --key-id TEXT                 AWS access key id  [env var:
                                  AWS_ACCESS_KEY_ID]
    --key-secret TEXT             AWS access key secret  [env var:
                                  AWS_SECRET_ACCESS_KEY]
    --polling-interval INTEGER    AWS polling interval  [env var:
                                  SQS_POLLING_INTERVAL]
    --celery-commands TEXT        SQS command  [env var: CELERY_COMMANDS]
  Other arguments:
    --server-port INTEGER         HTTP server port  [env var:
                                  HTTP_SERVER_PORT]
    --with-healthcheck            Start a healthcheck http endpoint  [env var:
                                  WITH_HEALTHCHECK]
    -l, --level [debug|info|warning|error|critical]
                                  Logging level  [env var: LOG_LEVEL]
    -o, --loader TEXT             Image loader  [env var: IMAGE_LOADER]
    -s, --store TEXT              Detector result store  [env var:
                                  DETECTOR_STORAGE]
    -t, --timeout INTEGER         Timeout in seconds for image detection  [env
                                  var: DETECTOR_TIMEOUT]
    --sentry-url TEXT             Sentry URL  [env var: SENTRY_URL]
    --metrics TEXT                Metrics client, should be the full name of a
                                  python module  [env var: METRICS_CLIENT]
  Memcached store arguments:
    --memcached-hosts TEXT        Comma separated list of memcached hosts
                                  [env var: MEMCACHED_HOSTS]
  --help                          Show this message and exit.
```

RemoteCV can also be configured via environment variables

[thumbor]: https://github.com/thumbor/thumbor/wiki
[PyRes]: https://github.com/binarydud/pyres
[Celery]: https://www.celeryproject.org
[opencv]: https://opencv.org/
