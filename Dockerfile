FROM python:3.11-slim

LABEL NAME=apPRoved-llm
LABEL VERSION=1.0.0

WORKDIR /app

RUN pip install poetry==1.8.3

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && poetry install

COPY ./ ./

CMD ["python", "-m", "src.main"]
