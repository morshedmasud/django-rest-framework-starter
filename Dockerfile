# === Stage 1: Builder ===
FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

WORKDIR /app

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

# === Stage 2: Final ===
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PATH="/opt/venv/bin:$PATH"

WORKDIR /app

RUN useradd --create-home --uid 1000 app

COPY --from=builder /opt/venv /opt/venv
COPY --chown=app:app . .
RUN chmod +x /app/entrypoint.sh && mkdir -p /app/staticfiles /app/media && chown app:app /app/staticfiles /app/media

USER app

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uvicorn", "main.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
