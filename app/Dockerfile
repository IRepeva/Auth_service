FROM python:3.10.4 as base

ENV PYTHONUNBUFFERED 1

WORKDIR /app

EXPOSE 8000/tcp

RUN pip install --upgrade pip &&  \
    groupadd -r app_group &&  \
    useradd -d /app -r -g app_group app_user

COPY --chown=app_user:app_group ./requirements requirements
RUN pip install -r requirements/app.txt --no-cache-dir

COPY --chown=app_user:app_group ./app .
COPY --chown=app_user:app_group utils ./utils
COPY --chown=app_user:app_group auth_grpc ./auth_grpc

CMD ["gunicorn", "main:app", "-w", "10", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]