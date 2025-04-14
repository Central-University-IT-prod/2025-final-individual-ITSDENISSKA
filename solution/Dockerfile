FROM python:3.12.3-slim-bullseye as base

ENV PYTHONUNBUFFERED 1
WORKDIR /build

RUN apt-get update && apt-get install -y gcc

FROM base as poetry
RUN pip install poetry==1.8.2
COPY poetry.lock pyproject.toml ./
RUN poetry export -o /requirements.txt --without-hashes

FROM base as common
COPY --from=poetry /requirements.txt .
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"
RUN pip install -r requirements.txt

RUN pip install uvicorn[standard]

RUN apt-get update && apt-get install -y postgresql-client

COPY src src
COPY alembic alembic
COPY alembic.ini .
COPY pyproject.toml .

RUN echo '#!/bin/sh \n\
alembic upgrade head \n\
exec runuser -u uvicorn -- /venv/bin/uvicorn src.main:app --app-dir /build --host REDACTED --port 8080 --workers 2 --loop uvloop' > /start.sh

RUN chmod +x /start.sh

RUN addgroup --gid 1001 --system uvicorn && \
    adduser --gid 1001 --shell /bin/false --disabled-password --uid 1001 uvicorn

RUN chown -R uvicorn:uvicorn /build

EXPOSE 8080
CMD ["/start.sh"]