# Agent Observability

Reusable observability setup for MAF agents.

Supports:

- Langfuse
- Azure Application Insights
- Both at the same time

## Usage 

```python

from agent_observability import initialize_observability

initialize_observability(
    langfuse=True,
    application_insights=True
)

```

Note: Keep both langfuse and application insights or either of them.

## Telemetry

1. Langfuse receives traces
2. Application Insights receives traces, logs and metrics
