# syntax=docker/dockerfile:1
# Refresh both pins together and validate before promotion.
FROM cgr.dev/chainguard/python:latest-dev@sha256:898360ca56a2a65c3facdd36a4e6151133a580aa367195261554e82948921ff1 AS builder
USER 0:0
WORKDIR /app
RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"
COPY --chmod=0644 requirements-oauth.txt /app/requirements-oauth.txt
RUN --mount=type=secret,id=proxy_ca,target=/tmp/proxy-ca \
    if [ -f /tmp/proxy-ca ]; then export PIP_CERT=/tmp/proxy-ca; fi; \
    pip install --disable-pip-version-check --no-cache-dir --only-binary=:all: -r /app/requirements-oauth.txt \
    && python -m pip uninstall --yes pip setuptools wheel

FROM cgr.dev/chainguard/python:latest@sha256:1a00964779bf570a8cb2ea4fa086614af19c35069029785c08fcec0c50b66ac0
WORKDIR /app
COPY --from=builder /app/venv /app/venv
COPY --chown=0:0 --chmod=0755 refactoredmemory /app/refactoredmemory
ENV PATH="/app/venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
USER 10001:10001
EXPOSE 8765 8766
ENTRYPOINT ["/app/venv/bin/python", "-m", "refactoredmemory", "--db", "/data/memory.sqlite3"]
CMD ["serve", "--host", "127.0.0.1"]
