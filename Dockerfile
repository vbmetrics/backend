FROM python:3.13-slim as builder
WORKDIR /usr/src/app
ENV PIP_NO_CACHE_DIR=off
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /usr/src/app/wheels -r requirements.txt

FROM python:3.13-slim
WORKDIR /usr/src/app
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --no-cache /wheels/*
COPY ./app /usr/src/app/app
COPY ./alembic /usr/src/app/alembic
COPY ./alembic.ini /usr/src/app/
COPY ./.env /usr/src/app/
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-c", "app/gunicorn_conf.py", "app.main:app"]