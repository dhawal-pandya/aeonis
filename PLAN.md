# Aeonis Development Plan

This document outlines the development roadmap for the Aeonis observability platform. It is a living document that will be updated as tasks are completed.

**Last Updated**: Saturday, June 28, 2025

---
## Guiding Principles

These principles are the "constitution" for the Aeonis project. They guide our technical decisions and ensure the project remains aligned with its core philosophy.

1.  **Developer Experience is Paramount:** The primary users of our SDKs and UI are developers. Every decision should prioritize ease of use, clear documentation, and low-friction setup. If a feature is powerful but complex to use, we must find a way to simplify it.
    *   *Keywords: Simple, Idiomatic, Low-Friction.*

2.  **Specification-Driven and Modular:** The system must be extensible. We will always define clear, language-agnostic schemas and interfaces *before* implementation. This allows components (like new SDKs) to be built independently and guarantees they will work with the rest of the system.
    *   *Keywords: Language-Agnostic, Decoupled, Scalable.*

3.  **Performance is a Non-Negotiable Feature:** Our code will run inside our users' applications. It *must* be highly performant and have a negligible resource footprint. We will always favor asynchronous operations, efficient data handling, and low overhead.
    *   *Keywords: Asynchronous, Efficient, Low-Overhead.*

4.  **Security and Privacy by Design:** We are handling potentially sensitive data. Security is not an afterthought. We will always build with a "secure by default" mindset, including robust PII sanitization and a clear understanding of data flow.
    *   *Keywords: Secure Defaults, PII-Aware, Data Integrity.*

5.  **Pragmatic, Not Dogmatic:** We will choose the right tool for the job. While we have preferences (like Python for the server), we will make technology choices based on the specific problem we are trying to solve, not just because it's a popular trend. Every significant architectural choice should be justifiable.
    *   *Keywords: Practical, Justified, Right Tool for the Job.*

---
### **Process Note**
After every significant change, the following must be done:
1.  Update the "Status" of the relevant task in this file.
2.  Update the main `README.md` to reflect the new overall project status.
3.  Ensure the "Last Updated" timestamp on this document is current.

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
-   **Description**: Implement a JS/TS tracer SDK for browser and Node.js environments that aheres to the `aeonis-specification`.

---

## Phase 2: The Aeonis Server

The goal of this phase is to build the central server that receives, processes, and stores trace data.

### Task 2.1: Basic Ingestion Endpoint

-   **Status**: ✅ `DONE`
-   **Description**: Set up a basic Python web server (using FastAPI or Flask) with a single endpoint: `/v1/traces`. This endpoint will accept `POST` requests containing an array of `Span` objects that validate against our `trace-schema.json`. The server's ability to receive and parse full, detailed spans from the Go SDK has been successfully validated.

### Task 2.2: Server Structural Refactoring

-   **Status**: ✅ `DONE`
-   **Description**: Refactored the ingestion server into a scalable, modular structure with clear separation of concerns (API, DB, Core, etc.). This prepares the codebase for future features like database integration and AI components.
-   **Artifacts**:
    -   `apps/aeonis-server/aeonis_server/` (new package structure)

### Task 2.3: Database Integration

-   **Status**: 🚧 `NEXT UP`
-   **Description**: Choose and integrate a database for storing trace data. A PostgreSQL database with the TimescaleDB extension is the primary candidate. The server will be updated to persist the ingested spans into the database.

### Task 2.4: API for UI

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

---
## Architectural Decisions

This section serves as a log of significant architectural choices and their justifications.

1.  **Initial Ingestion Protocol: `HTTP/JSON` over `gRPC`**
    *   **Decision Date**: 2025-06-28
    *   **Context**: We need a protocol for the tracer SDKs to send data to the server. The primary candidates were RESTful HTTP/JSON and gRPC/Protobuf.
    *   **Decision**: We will start with HTTP/JSON.
    *   **Justification**:
        *   **Simplicity & Universality**: Every language has excellent, mature support for HTTP/JSON, making it the lowest-friction way to build our first set of diverse SDKs (Principle #1).
        *   **Debuggability**: The text-based nature of JSON is easy to inspect and debug during initial development.
        *   **Extensibility**: The SDKs will be designed with an `Exporter` interface. This allows us to add a `gRPCExporter` in the future without changing the core tracer logic, mitigating the performance trade-offs at scale (Principle #2 & #5).
