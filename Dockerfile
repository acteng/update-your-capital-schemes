FROM python:3.10

ENV PORT 5000

WORKDIR /usr/src/app
COPY schemes ./schemes
COPY pyproject.toml .

RUN pip install --no-cache-dir .

CMD [ "sh", "-c", "gunicorn --bind 0.0.0.0:${PORT} 'schemes:create_app()'" ]
