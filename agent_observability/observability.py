import base64
import os

from dotenv import load_dotenv

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from agent_framework.observability import configure_otel_providers
from azure.monitor.opentelemetry import configure_azure_monitor


_configured = False


def initialize_observability(
    langfuse: bool = False,
    application_insights: bool = False,
):
    """
    Initializes observability for an agent.

    Options:
        langfuse=True
        application_insights=True

    Examples:

        initialize_observability(langfuse=True)

        initialize_observability(application_insights=True)

        initialize_observability(
            langfuse=True,
            application_insights=True,
        )
    """

    global _configured

    if _configured:
        return

    load_dotenv()

    if not langfuse and not application_insights:
        _configured = True
        return

    # Application Insights (Azure monitor: traces, logs, metrics)
  
    if application_insights:
        connection_string = os.getenv(
            "APPLICATIONINSIGHTS_CONNECTION_STRING"
        )

        if not connection_string:
            raise ValueError(
                "APPLICATIONINSIGHTS_CONNECTION_STRING is missing."
            )

        configure_azure_monitor(
            connection_string=connection_string
        )

    # Langfuse only (MAF Opentelemetry if azure monitor is not selected)
 
    if langfuse and not application_insights:
        langfuse_exporter = _create_langfuse_exporter()

        configure_otel_providers(
            exporters=[langfuse_exporter]
        )

    # Langfuse + Application Insights (Azure Monitor = OTel providers & Langfuse = another trace exporter).
    
    elif langfuse and application_insights:
        langfuse_exporter = _create_langfuse_exporter()

        tracer_provider = trace.get_tracer_provider()

        tracer_provider.add_span_processor(
            BatchSpanProcessor(langfuse_exporter)
        )

    _configured = True


def _create_langfuse_exporter():
    #Create the Langfuse OTLP trace exporter

    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    base_url = os.getenv("LANGFUSE_BASE_URL")

    if not public_key:
        raise ValueError("LANGFUSE_PUBLIC_KEY is missing.")

    if not secret_key:
        raise ValueError("LANGFUSE_SECRET_KEY is missing.")

    if not base_url:
        raise ValueError("LANGFUSE_BASE_URL is missing.")

    auth = base64.b64encode(
        f"{public_key}:{secret_key}".encode()
    ).decode()

    return OTLPSpanExporter(
        endpoint=f"{base_url}/api/public/otel/v1/traces",
        headers={
            "Authorization": f"Basic {auth}",
            "x-langfuse-ingestion-version": "4",
        },
    )
