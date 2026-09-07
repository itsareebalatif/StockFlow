# FROM python:3.13-slim

# # Install uv
# COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# WORKDIR /app

# # Copy all project files
# COPY . .

# RUN uv sync --no-dev

# EXPOSE 8000
# CMD ["uv", "run", "--no-sync", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM python:3.13-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Copy dependency files first so packages are cached
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv sync --no-dev --no-install-project

# Copy project files
COPY . .

# Final project sync
RUN uv sync --no-dev

EXPOSE 8000

# Added --reload so Uvicorn watches for code updates live
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]