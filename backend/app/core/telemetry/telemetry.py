from fastapi import FastAPI
from openinference.instrumentation.langchain import LangChainInstrumentor
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter


def setup_telemetry(app: FastAPI):
    """
    Configures OpenTelemetry for FastAPI and LangChain.
    This provides end-to-end tracing for API requests and LLM lifecycles.
    """
    provider = TracerProvider()
    trace.set_tracer_provider(provider)

    # Export traces to the console. In production, swap ConsoleSpanExporter
    # with OTLPSpanExporter to send traces to Jaeger, Datadog, or Langfuse.
    processor = BatchSpanProcessor(ConsoleSpanExporter())
    provider.add_span_processor(processor)

    FastAPIInstrumentor.instrument_app(app)
    LangChainInstrumentor().instrument()
