import os
from functools import lru_cache


def is_tracing_enabled() -> bool:
    return os.environ.get("OTEL_TRACING_ENABLED", "false").lower() == "true"


def setup_tracing(app=None, service_name: str = "kaban-backend"):
    if not is_tracing_enabled():
        print(f"[TRACING] Disabled (ENVIRONMENT={os.environ.get('ENVIRONMENT')})")
        return None

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter, Compression
        from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
        from opentelemetry.instrumentation.redis import RedisInstrumentor
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
    except ImportError as e:
        print(f"[TRACING] OpenTelemetry packages not installed: {e}")
        return None

    try:
        otlp_endpoint = os.environ.get(
            "OTEL_EXPORTER_OTLP_ENDPOINT",
            "http://adot-collector.aws-otel-eks.svc.cluster.local:4317"
        )

        print(f"[TRACING] Initializing OpenTelemetry for {service_name}")
        print(f"[TRACING] Sending traces to: {otlp_endpoint}")

        resource = Resource.create({
            SERVICE_NAME: service_name,
            SERVICE_VERSION: os.environ.get("APP_VERSION", "1.0.0"),
            "deployment.environment": os.environ.get("ENVIRONMENT", "staging"),
        })

        provider = TracerProvider(resource=resource)

        otlp_exporter = OTLPSpanExporter(
            endpoint=otlp_endpoint,
            insecure=True,
            compression=Compression.Gzip
        )

        provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
        trace.set_tracer_provider(provider)

        if app:
            FastAPIInstrumentor.instrument_app(app)

        HTTPXClientInstrumentor().instrument()
        RedisInstrumentor().instrument()
        SQLAlchemyInstrumentor().instrument()

        print("[TRACING] OpenTelemetry initialized successfully")
        print("[TRACING] Instrumented: FastAPI, HTTPX, Redis, SQLAlchemy")

        return provider

    except Exception as e:
        print(f"[TRACING] Failed to initialize OpenTelemetry: {e}")
        import traceback
        traceback.print_exc()
        return None


def setup_celery_tracing():
    if not is_tracing_enabled():
        print(f"[TRACING] Celery tracing disabled")
        return None

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter, Compression
        from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
        from opentelemetry.instrumentation.celery import CeleryInstrumentor
        from opentelemetry.instrumentation.redis import RedisInstrumentor
        from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
    except ImportError as e:
        print(f"[TRACING] OpenTelemetry packages not installed: {e}")
        return None

    try:
        otlp_endpoint = os.environ.get(
            "OTEL_EXPORTER_OTLP_ENDPOINT",
            "http://adot-collector.aws-otel-eks.svc.cluster.local:4317"
        )

        resource = Resource.create({
            SERVICE_NAME: "kaban-celery-worker",
            SERVICE_VERSION: os.environ.get("APP_VERSION", "1.0.0"),
            "deployment.environment": os.environ.get("ENVIRONMENT", "staging"),
        })

        provider = TracerProvider(resource=resource)
        otlp_exporter = OTLPSpanExporter(
            endpoint=otlp_endpoint,
            insecure=True,
            compression=Compression.Gzip
        )
        provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
        trace.set_tracer_provider(provider)

        CeleryInstrumentor().instrument()
        RedisInstrumentor().instrument()
        HTTPXClientInstrumentor().instrument()
        SQLAlchemyInstrumentor().instrument()

        print(f"[TRACING] Celery tracing initialized in PID {os.getpid()}, sending to {otlp_endpoint}")
        print("[TRACING] Instrumented: Celery, Redis, HTTPX, SQLAlchemy")

        return provider

    except Exception as e:
        print(f"[TRACING] Failed to initialize Celery tracing: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_tracer(name: str = __name__):
    if not is_tracing_enabled():
        from contextlib import contextmanager
        
        class NoOpSpan:
            def set_attribute(self, key, value): pass
            def add_event(self, name, attributes=None): pass
            def __enter__(self): return self
            def __exit__(self, *args): pass
        
        class NoOpTracer:
            @contextmanager
            def start_as_current_span(self, name, **kwargs):
                yield NoOpSpan()
        
        return NoOpTracer()
    
    from opentelemetry import trace
    return trace.get_tracer(name)