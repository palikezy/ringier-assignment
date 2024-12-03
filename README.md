# Ringier Assignment

## Setup

Prerequisites:

- Python 3.12
- Python Poetry
- Ollama

```bash
poetry install
poetry shell
pre-commit install
```

## Start

Default setup uses smallest model - `llama3.2:1b`.
Model can be changed through environment variables and docker build arguments.

### Development

```bash
fastapi dev app
```

## Docker Compose

Docker Compose does not require Python and virtual environment setup.

```bash
docker compose up -d --build
```
