package tracer

import "time"

// Span represents a single unit of work in a trace.
type Span struct {
	TraceID      string                 `json:"trace_id"`
	SpanID       string                 `json:"span_id"`
	ParentSpanID string                 `json:"parent_span_id,omitempty"`
	Name         string                 `json:"name"`
	StartTime    time.Time              `json:"start_time"`
	EndTime      time.Time              `json:"end_time"`
	Attributes   map[string]interface{} `json:"attributes,omitempty"`
	Error        *SpanError             `json:"error,omitempty"`

	// internal fields
	exporter  Exporter
	sanitizer Sanitizer
}

// SpanError represents an error that occurred during a span.
type SpanError struct {
	Message    string `json:"message"`
	StackTrace string `json:"stack_trace,omitempty"`
}
