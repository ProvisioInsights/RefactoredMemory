# Source-only upgrade over the qualified A23 private release, not a moving base.
# Operator MUST verify this local tag has the exact image ID below before build:
# sha256:312234c48884e7f6e72ee0a9b2698d5512daabc3ad71cef6dd0013397a44dda2
# No dependency or root-executed code changes. A new base needs a reviewed recipe.
FROM refactoredmemory:chainguard-client-app-158b57f
USER 0:0
COPY --chown=0:0 --chmod=0755 refactoredmemory /app/refactoredmemory
ARG REFMEM_REVISION
LABEL org.opencontainers.image.revision=${REFMEM_REVISION}
USER 10001:10001
