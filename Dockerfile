FROM python:3.10-slim

ENV PORT 5000

WORKDIR /usr/src/app
COPY schemes ./schemes
COPY pyproject.toml .

RUN pip install --no-cache-dir .

CMD [ "sh", "-c", "gunicorn --bind 0.0.0.0:${PORT} --forwarded-allow-ips='*' 'schemes:create_app()'" ]
