package tracer

import (
	"context"
	"github.com/google/uuid"
	"time"
)

// Tracer is the entry point for creating spans.
type Tracer struct {
	serviceName string
	exporter    Exporter
	sanitizer   Sanitizer
}

// NewTracer creates a new tracer with a default HTTP exporter.
func NewTracer(serviceName, endpointURL, apiKey string, sanitizer Sanitizer) *Tracer {
	exporter := NewHTTPExporter(endpointURL, apiKey)
	return NewTracerWithExporter(serviceName, exporter, sanitizer)
}

// NewTracerWithExporter creates a new tracer with a custom exporter.
func NewTracerWithExporter(serviceName string, exporter Exporter, sanitizer Sanitizer) *Tracer {
	if sanitizer == nil {
		sanitizer = &NoOpSanitizer{}
	}
	return &Tracer{
		serviceName: serviceName,
		exporter:    exporter,
		sanitizer:   sanitizer,
	}
}

// StartSpan starts a new span.
func (t *Tracer) StartSpan(ctx context.Context, name string) (context.Context, *Span) {
	parentSpanContext, _ := fromContext(ctx)

	span := &Span{
		Name:       name,
		StartTime:  time.Now().UTC(),
		Attributes: make(map[string]interface{}),
		exporter:   t.exporter,
		sanitizer:  t.sanitizer,
	}

	if parentSpanContext.traceID != "" {
		span.TraceID = parentSpanContext.traceID
		span.ParentSpanID = parentSpanContext.spanID
	} else {
		span.TraceID = uuid.New().String()
	}

	span.SpanID = uuid.New().String()

	return toContext(ctx, span), span
}

// SetAttributes sets the attributes for the span, applying sanitization.
func (s *Span) SetAttributes(attributes map[string]interface{}) {
	s.Attributes = s.sanitizer.Sanitize(attributes)
}

// End completes the span, calculating the duration and exporting it.
func (s *Span) End() {
	s.EndTime = time.Now().UTC()
	if s.exporter != nil {
		s.exporter.Export(s)
	}
}
