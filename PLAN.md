# Aeonis Development Plan

This document outlines the development roadmap for the Aeonis observability platform. It is a living document that will be updated as tasks are completed.

**Last Updated**: Saturday, June 28, 2025

---

## Phase 1: The Tracer SDKs

The goal of this phase is to build robust, language-specific SDKs to collect trace data from user applications.

### Task 1.1: Language-Agnostic Specification

-   **Status**: ✅ `DONE`
-   **Description**: Define a clear, language-agnostic specification for the trace data format (`Span`) and the HTTP export protocol. This ensures all future SDKs are compatible.
-   **Artifacts**:
    -   `packages/specification/trace-schema.json`
    -   `packages/specification/README.md`

### Task 1.2: Go Tracer SDK

-   **Status**: ✅ `DONE`
-   **Description**: Implement the first tracer SDK for the Go programming language. It must be performant, include PII sanitization, and be easy to use.
-   **Artifacts**:
    -   `packages/tracer-sdk/go/` (complete module)
    -   `packages/tracer-sdk/go/sanitizer_test.go`
    -   `packages/tracer-sdk/go/tracer_test.go`

### Task 1.3: Python Tracer SDK

-   **Status**: ⏳ `TODO`
-   **Description**: Implement a Python tracer SDK that adheres to the `aeonis-specification`.

### Task 1.4: JavaScript/TypeScript Tracer SDK

-   **Status**: ⏳ `TODO`
-   **Description**: Implement a JS/TS tracer SDK for browser and Node.js environments that adheres to the `aeonis-specification`.

---

## Phase 2: The Ingestion Server

The goal of this phase is to build the central server that receives, processes, and stores trace data.

### Task 2.1: Basic Ingestion Endpoint

-   **Status**: 🚧 `NEXT UP`
-   **Description**: Set up a basic Python web server (using FastAPI or Flask) with a single endpoint: `/v1/traces`. This endpoint will accept `POST` requests containing an array of `Span` objects that validate against our `trace-schema.json`. For now, the server will simply print the received spans to the console. This will validate our Go SDK's exporter.

### Task 2.2: Database Integration

-   **Status**: ⏳ `TODO`
-   **Description**: Choose and integrate a database for storing trace data. A PostgreSQL database with the TimescaleDB extension is the primary candidate. The server will be updated to persist the ingested spans into the database.

### Task 2.3: API for UI

-   **Status**: ⏳ `TODO`
-   **Description**: Develop a set of REST or GraphQL APIs that the `aeonis-ui` can use to query for traces, services, and spans.

---

## Phase 3: The AI-Powered Chat Interface

This phase focuses on building the AI-driven query and analysis capabilities.

### Task 3.1: MCP Server Setup

-   **Status**: ⏳ `TODO`
-   **Description**: Set up the MCP (Multi-Context Prompter) server. This will likely be a component within the main `aeonis-server`.

### Task 3.2: Database Tooling for AI

-   **Status**: ⏳ `TODO`
-   **Description**: Give the MCP server the ability to construct and execute SQL queries against the trace database in response to user questions.

### Task 3.3: RAG Implementation

-   **Status**: ⏳ `TODO`
-   **Description**: Implement a Retrieval-Augmented Generation (RAG) pipeline. The MCP server will fetch relevant trace data from the DB and use it as context for a Large Language Model (LLM) to generate accurate, data-driven answers.

---

## Phase 4: The Web UI

This phase involves creating the user-facing frontend for visualization and interaction.

### Task 4.1: Basic Trace Visualization
-   **Status**: ⏳ `TODO`
-   **Description**: Create a web application (likely using React or Vue) that can fetch and display a list of traces from the server.

### Task 4.2: Detailed Span Waterfall
-   **Status**: ⏳ `TODO`
-   **Description**: Implement a detailed view for a single trace, showing the waterfall diagram of parent and child spans.

### Task 4.3: Chat Interface
-   **Status**: ⏳ `TODO`
-   **Description**: Integrate the chat component that interacts with the MCP server.

---

## Phase 5: Advanced AI-Powered Code Analysis

This phase extends the AI capabilities beyond runtime trace data to include static code analysis and version control history, enabling powerful DevSecOps insights.

### Task 5.1: Git Integration
-   **Status**: ⏳ `TODO`
-   **Description**: Connect the `aeonis-server` to the project's Git repository. The server will need to be able to read files, analyze diffs between commits, and correlate code changes with runtime behavior.

### Task 5.2: Static Code Analysis Tooling
-   **Status**: ⏳ `TODO`
-   **Description**: Integrate static analysis tools (linters, security scanners) into the `aeonis-server`. The AI will use the output of these tools as another source of context.

### Task 5.3: Security and Data Leak Analysis
-   **Status**: ⏳ `TODO`
-   **Description**: Develop the AI models and RAG pipelines required to answer security-focused questions. This involves correlating trace data (e.g., an HTTP call to a third-party webhook) with static analysis of the code that triggered it to identify potential PII leaks.

### Task 5.4: Code Impact and Optimization Analysis
-   **Status**: ⏳ `TODO`
-   **Description**: Build the capabilities to answer questions about code structure and optimization. This will involve analyzing code complexity, dependency graphs, and comparing trace data across different code versions to provide optimization suggestions.
