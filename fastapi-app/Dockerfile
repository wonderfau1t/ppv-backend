FROM python:3.12-slim-trixie

COPY --from=ghcr.io/astral-sh/uv:0.8.3 /uv /uvx /bin/

ADD . /app

WORKDIR /app

RUN uv sync --locked

EXPOSE 8000

ENTRYPOINT [ "./entrypoint.sh" ]