[![Build
Status](https://travis-ci.org/thumbor/remotecv.svg?branch=master)](https://travis-ci.org/thumbor/remotecv)
[![Coverage
Status](https://coveralls.io/repos/thumbor/remotecv/badge.svg?branch=master&service=github)](https://coveralls.io/github/thumbor/remotecv?branch=master)

# Remotecv remotecv is a queued mechanism to run OpenCV computations and store
them for later usage.

Currently, [Thumbor](https://github.com/thumbor/thumbor/wiki) uses remotecv to
outsource facial or feature detection, but nothing stops you from integrating
it into your product.

remotecv supports both [PyRes](https://github.com/binarydud/pyres) and
[Celery](http://www.celeryproject.org/) for queueing back-end.

---

## install

```sh
make setup
```

---

## run local

```sh
make run-redis make run
```

---

## tests

```sh
make unit
```
