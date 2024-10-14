# syntax=docker/dockerfile:1

# Use BuildKit's build-time cache mounts, it makes a huge difference on rebuilds.
# - https://vsupalov.com/buildkit-cache-mount-dockerfile/
# - https://github.com/FernandoMiguel/Buildkit#mounttypecache

FROM python:3.13-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive
ENV TERM=linux

# Install Git, it is needed for `versioningit`.
RUN rm -f /etc/apt/apt.conf.d/docker-clean; echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache
RUN --mount=type=cache,id=apt,target=/var/cache/apt --mount=type=cache,id=apt,target=/var/lib/apt \
    true \
    && apt-get update \
    && apt-get install --no-install-recommends --no-install-suggests --yes git

# Copy sources
COPY . /src

# Install package.
RUN --mount=type=cache,id=pip,target=/root/.cache/pip \
    pip install --use-pep517 --prefer-binary '/src[all]'

# Uninstall Git again.
RUN apt-get --yes remove --purge git && apt-get --yes autoremove

# Purge /src and /tmp directories.
RUN rm -rf /src /tmp/*

# Copy selftest.sh to the image
COPY release/oci/selftest.sh /usr/local/bin
