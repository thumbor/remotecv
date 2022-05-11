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

[thumbor]: https://github.com/thumbor/thumbor/wiki
[PyRes]: https://github.com/binarydud/pyres
[Celery]: https://www.celeryproject.org
[opencv]: https://opencv.org/
