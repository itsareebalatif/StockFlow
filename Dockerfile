FROM python:3.13-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Copy all project files
COPY . .

# Install dependencies into .venv
RUN uv sync --no-dev

# Use uv to run the app directly (--no-sync: venv is already built, don't re-resolve at runtime)
EXPOSE 8000
CMD ["uv", "run", "--no-sync", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]