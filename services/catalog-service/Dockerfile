FROM python:3.14-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /workspace

COPY services/catalog-service/pyproject.toml \
     services/catalog-service/uv.lock \
     ./services/catalog-service/

COPY libs ./libs

WORKDIR /workspace/services/catalog-service

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project


FROM python:3.14-slim

WORKDIR /workspace/services/catalog-service

COPY libs /workspace/libs

COPY services/catalog-service/app ./app
COPY services/catalog-service/alembic.ini ./alembic.ini
COPY services/catalog-service/alembic ./alembic

COPY --from=builder \
    /workspace/services/catalog-service/.venv \
    ./.venv

ENV PATH="/workspace/services/catalog-service/.venv/bin:$PATH"
ENV PYTHONPATH="/workspace/services/catalog-service"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]