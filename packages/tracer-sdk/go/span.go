package tracer

import "time"

type spanKey struct{}

// Span represents a single unit of work in a trace.
type Span struct {
	TraceID      string                 `json:"trace_id"`
	SpanID       string                 `json:"span_id"`
	ParentSpanID string                 `json:"parent_span_id,omitempty"`
	CommitID     string                 `json:"commit_id,omitempty"`
	SDKVersion   string                 `json:"sdk_version,omitempty"`
	Name         string                 `json:"name"`
	StartTime    time.Time              `json:"start_time"`
	EndTime      time.Time              `json:"end_time"`
	Attributes   map[string]interface{} `json:"attributes,omitempty"`
	Error        *SpanError             `json:"error,omitempty"`

	// internal fields
	tracer    *Tracer
	exporter  Exporter
	sanitizer Sanitizer
}

// SpanError represents an error that occurred during a span.
type SpanError struct {
	Message    string `json:"message"`
	StackTrace string `json:"stack_trace,omitempty"`
}
