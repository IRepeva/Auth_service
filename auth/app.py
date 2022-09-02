import sys

from flask import Flask, request

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

sys.path.append('.')

from commands import create_superuser
from core.settings import BASE_CONFIG, additional_settings
from extensions import migrate, jwt, ma, bcrypt, rebar

from databases import db, configure_db
from api.v1.admin_api import admin_blueprint
from api.v1.user_api import user_blueprint
from api import models


resource = Resource(attributes={
    SERVICE_NAME: "auth_service"
})


def configure_app(app):
    @app.before_request
    def before_request():
        request_id = request.headers.get('X-Request-Id')
        if not request_id:
            raise RuntimeError('request id is required')


def init_extensions(app: Flask):
    jwt.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    ma.init_app(app)
    bcrypt.init_app(app)
    rebar.init_app(app)


def add_commands(app):
    app.cli.add_command(create_superuser)


def register_blueprints(app: Flask):
    app.register_blueprint(user_blueprint)
    app.register_blueprint(admin_blueprint)


def configure_tracer(app) -> None:
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    processor = BatchSpanProcessor(
        JaegerExporter(
            agent_host_name=additional_settings.JAEGER_AGENT_HOST,
            agent_port=additional_settings.JAEGER_AGENT_PORT,
        )
    )
    provider.add_span_processor(processor)

    FlaskInstrumentor().instrument_app(app)


def create_app(config=BASE_CONFIG):
    app = Flask(__name__)
    app.config.from_object(config)

    configure_app(app)
    configure_db(app)
    init_extensions(app)
    add_commands(app)
    register_blueprints(app)
    configure_tracer(app)

    return app


app = create_app()
