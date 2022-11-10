ARG PYTHON_VERSION
FROM python:${PYTHON_VERSION}-bullseye AS builder-image

ARG TARGETPLATFORM
ARG DEBIAN_FRONTEND=noninteractive
ARG REMOTECV_VERSION

RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get -y autoremove && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


RUN python3 -m venv /home/remotecv/venv
ENV PATH="/home/remotecv/venv/bin:$PATH"

RUN pip3 install --no-cache-dir wheel && \
    pip3 install --no-cache-dir remotecv==${REMOTECV_VERSION}

FROM python:${PYTHON_VERSION}-slim-bullseye AS runner-image

RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get -y autoremove && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN useradd --create-home remotecv
COPY --from=builder-image /home/remotecv/venv /home/remotecv/venv

USER remotecv

EXPOSE 8888

ENV PYTHONUNBUFFERED=1

ENV VIRTUAL_ENV=/home/remotecv/venv
ENV PATH="/home/remotecv/venv/bin:$PATH"

ENTRYPOINT ["remotecv"]
