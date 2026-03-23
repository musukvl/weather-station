FROM python:3.14-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml .
COPY main.py .
COPY ws_parser.py .
COPY postgres_logger.py .

# Install dependencies
RUN uv pip install --system --no-cache -r pyproject.toml

# Run the application
CMD ["python", "main.py"]
