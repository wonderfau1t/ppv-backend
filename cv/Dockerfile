FROM python:3.12-slim-trixie

COPY --from=ghcr.io/astral-sh/uv:0.8.3 /uv /uvx /bin/
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
 && rm -rf /var/lib/apt/lists/*

ADD . /app

WORKDIR /app

RUN uv sync --locked

EXPOSE 8080

# ENTRYPOINT [ "./entrypoint.sh" ]
CMD ["uv", "run", "main.py"]