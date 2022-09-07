FROM python:3.10.4 as base

ENV PYTHONUNBUFFERED 1

WORKDIR /auth

EXPOSE 5000/tcp

RUN pip install --upgrade pip &&  \
    groupadd -r auth_group &&  \
    useradd -d /auth -r -g auth_group auth_user

COPY --chown=auth_user:auth_group ./requirements requirements
RUN pip install -r requirements/auth.txt --no-cache-dir

COPY --chown=auth_user:auth_group auth .
COPY --chown=auth_user:auth_group utils ./utils

CMD ["gunicorn", "--worker-class", "gevent", "-w", "10", "--bind", "0.0.0.0:5000", "wsgi_app:app"]


FROM base AS tests

WORKDIR /auth

COPY --from=base --chown=auth_user:auth_group /auth ./auth

RUN pip install -r requirements/tests.txt --no-cache-dir

COPY --chown=auth_user:auth_group tests/auth .

USER auth_user