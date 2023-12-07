FROM python:3.11-slim

ENV PORT 5000

WORKDIR /usr/src/app
COPY schemes ./schemes
COPY pyproject.toml .

RUN pip install --no-cache-dir . \
    && useradd schemes

USER schemes

CMD [ "sh", "-c", "gunicorn --bind 0.0.0.0:${PORT} --timeout 0 --forwarded-allow-ips='*' 'schemes:create_app()'" ]
