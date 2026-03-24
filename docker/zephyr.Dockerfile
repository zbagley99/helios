FROM python:3.14-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-interaction --only main

COPY src/ ./src/

ENV PYTHONPATH=/app/src

EXPOSE 5555

CMD ["uvicorn", "zephyr.app:app", "--host", "0.0.0.0", "--port", "5555"]
