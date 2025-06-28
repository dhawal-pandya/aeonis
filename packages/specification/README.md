# Aeonis Specification

This directory contains the language-agnostic specification for the Aeonis Tracing project. All Aeonis-compatible SDKs and servers MUST adhere to these definitions.

## Trace Schema

The canonical definition of a trace segment is the `Span`. Its structure is formally defined in `trace-schema.json` using the JSON Schema standard.

A `Span` represents a single, named unit of work (e.g., a function call, a database query, an incoming HTTP request).

### Span Fields

- **`trace_id`** (string, uuid): The ID for the entire execution flow. All spans in a single trace share this ID.
- **`span_id`** (string, uuid): The unique ID for this specific span.
- **`parent_span_id`** (string, uuid, optional): The `span_id` of the parent operation. If this is null or omitted, it is a "root span".
- **`name`** (string): A human-readable name for the operation (e.g., `HTTP GET /users`, `db.query`, `process_image`).
- **`start_time`** (string, date-time): The UTC timestamp in ISO 8601 format when the operation started.
- **`end_time`** (string, date-time): The UTC timestamp in ISO 8601 format when the operation completed.
- **`attributes`** (object, optional): A key-value map of sanitized, arbitrary metadata about the operation. This can include function arguments, return values, HTTP status codes, etc.
- **`error`** (object, optional): An object describing an error that occurred during the operation.
  - **`message`** (string): The error message.
  - **`stack_trace`** (string, optional): The stack trace, if available.

## HTTP Export Protocol

Tracers must send completed spans to an ingestion server via HTTP.

- **Endpoint**: The endpoint URL must be configurable by the user. It defaults to `http://localhost:8080/v1/traces`.
- **Method**: `POST`
- **Headers**:
  - `Content-Type: application/json`
- **Request Body**: The body must be a JSON array of `Span` objects, where each object in the array validates against the `trace-schema.json`.

  ```json
  [
    {
      "trace_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
      "span_id": "b2c3d4e5-f6a7-8901-2345-67890abcdef0",
      "name": "HTTP GET /api/data",
      "start_time": "2025-06-28T10:00:00.000Z",
      "end_time": "2025-06-28T10:00:00.150Z",
      "attributes": {
        "http.method": "GET",
        "http.status_code": 200
      }
    }
  ]
  ```
