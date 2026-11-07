# syntax=docker/dockerfile:1
FROM python:3.12.16-slim-trixie@sha256:4840d514c583a4d3d8cad3940e68dee6f0f6f3635c12fcd0a3d74c21a5b93a54 AS wheels
WORKDIR /build
COPY requirements-oauth.txt .
# An optional build-only CA supports managed environments; it never enters the runtime.
RUN --mount=type=secret,id=proxy_ca,target=/tmp/proxy-ca \
    if [ -f /tmp/proxy-ca ]; then export PIP_CERT=/tmp/proxy-ca; fi; \
    python -m pip wheel --disable-pip-version-check --no-cache-dir --only-binary=:all: \
    --wheel-dir=/wheels -r requirements-oauth.txt

FROM python:3.12.16-slim-trixie@sha256:4840d514c583a4d3d8cad3940e68dee6f0f6f3635c12fcd0a3d74c21a5b93a54
WORKDIR /app
COPY requirements-oauth.txt /tmp/requirements-oauth.txt
COPY --from=wheels /wheels /tmp/wheels
RUN python -m pip install --disable-pip-version-check --no-cache-dir --no-index \
      --find-links=/tmp/wheels -r /tmp/requirements-oauth.txt \
    && rm -rf /tmp/wheels /tmp/requirements-oauth.txt \
    && groupadd --gid 10001 memory \
    && useradd --uid 10001 --gid 10001 --no-create-home --shell /usr/sbin/nologin memory
COPY --chown=0:0 refactoredmemory /app/refactoredmemory
RUN chmod -R a+rX /app/refactoredmemory
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
USER 10001:10001
EXPOSE 8765 8766
ENTRYPOINT ["python", "-m", "refactoredmemory", "--db", "/data/memory.sqlite3"]
CMD ["serve", "--host", "127.0.0.1"]
