FROM python:3.10.4 as base

ENV PYTHONUNBUFFERED 1

WORKDIR /grpc

EXPOSE 50051/tcp

COPY ./requirements requirements
RUN pip install -r requirements/grpc.txt --no-cache-dir

COPY auth_grpc .
COPY utils ./utils

CMD ["python3", "auth_server.py"]
