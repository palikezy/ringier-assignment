FROM python:3.12-alpine AS base
ENV WORKDIR=/app
WORKDIR $WORKDIR


FROM base AS export
RUN pip install --no-cache-dir poetry
COPY pyproject.toml poetry.lock ./
RUN poetry export --without-hashes --format=requirements.txt > requirements.txt


FROM base AS production
RUN apk add --no-cache tini

COPY --from=export $WORKDIR/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Consume less memory
ENV PYTHONNODEBUGRANGES=0

ARG LLM_MODEL=llama3.2:1b
ENV LLM_MODEL=$LLM_MODEL

ENTRYPOINT ["tini", "--"]
CMD ["fastapi", "run", "app", "--port", "80"]
EXPOSE 80
