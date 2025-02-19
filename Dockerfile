FROM python:3.8-slim

WORKDIR /app

RUN apt-get update && apt-get install -y make && pip install --upgrade pip && pip install poetry

COPY pyproject.toml poetry.lock* /app/

# install packages into the system environment
RUN poetry config virtualenvs.create false && poetry install --no-dev

COPY . .

# Remove any local virtual environment if present to avoid conflicts with the system environment
RUN rm -rf .venv

EXPOSE 8000

CMD ["make", "run"]
