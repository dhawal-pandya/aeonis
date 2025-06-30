# Aeonis: An AI-Powered DevSecOps Platform

Aeonis is an observability platform designed to provide deep, AI-powered insights into your applications. It combines distributed tracing with a conversational AI interface, allowing developers to not only visualize application flow but also ask complex questions about their system's behavior, security, and performance.

Our vision is to create a comprehensive DevSecOps tool that helps developers:
- **Identify Security Risks**: Proactively detect potential data leaks by asking questions like, *"Is this change logging sensitive data to a webhook?"*
- **Understand Code Impact**: Analyze the ripple effects of changes, asking *"Where would a new feature require the fewest changes?"*
- **Optimize Performance**: Compare performance characteristics across different versions or feature flags, asking *"How did the last commit affect database query times?"*

## Core Components

The Aeonis ecosystem is being built as a monorepo and consists of three primary components:

1.  **`aeonis-tracer`**: A suite of language-specific SDKs that developers integrate into their applications. These tracers are lightweight, performant, and capture detailed operational data (spans) according to the OpenTelemetry standard. The SDKs are designed to be "plug and play", automatically instrumenting popular frameworks and libraries to provide deep visibility into the entire request lifecycle. The goal is to capture a "stack trace for success" by tracing the full execution path of a request, from the initial API call, through every function call, down to the database query.

2.  **`aeonis-server`**: The central nervous system of the platform. This server (likely to be built in Python) is responsible for:
    *   Ingesting trace data from the various SDKs.
    *   Storing the data in a time-series database (e.g., PostgreSQL with TimescaleDB).
    *   Providing an API for the web UI to query and display traces.
    *   Hosting the MCP (Multi-Context Prompter) server, which uses AI and RAG to answer natural language questions about the trace data.

3.  **`aeonis-ui`**: A modern, intuitive web frontend for visualizing and analyzing the collected traces. It will provide a rich interface for exploring service maps, trace flows, and interacting with the AI chat component.

## Current Project Status

This project is under active development. Here is the current status of the core components:

*   **Go Tracer SDK (`packages/tracer-sdk/go`):** ✅ **Active and In Development**
    *   The Go SDK is currently being enhanced to provide automatic instrumentation for popular frameworks and libraries.
    *   The goal is to capture a rich, hierarchical trace of the entire request lifecycle, including function calls, database queries, and more.
    *   The SDK will provide a GORM plugin for automatic database tracing and enhanced Gin middleware for automatic request tracing.
    *   A `TraceFunc` helper is being developed to enable detailed, debugger-like tracing of the entire function call stack for a given operation.

*   **Ingestion Server (`apps/aeonis-server`):** ✅ **Active and In Development**
    *   The server is built on FastAPI and connects to a PostgreSQL database.
    *   It features a secure, multi-tenant ingestion endpoint (`/v1/traces`) that authenticates requests using project-specific API keys.
    *   A repository pattern is in place to abstract database logic, making the system adaptable for future database technologies.

*   **Web UI (`apps/aeonis-ui`):** 🚧 **Up Next**
    *   Development of a basic trace visualization UI is the next priority.

## Monorepo Structure

This project uses a monorepo structure to simplify dependency management and ensure consistency across components.

*   `apps/`: Contains deployable applications (the server, the UI).
*   `packages/`: Contains shared libraries, specifications, and the tracer SDKs.

---
*This README reflects the project status as of Monday, June 30, 2025.*