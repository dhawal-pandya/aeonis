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
	parentSpan, _ := fromContext(ctx)

	span := &Span{
		Name:       name,
		StartTime:  time.Now().UTC(),
		Attributes: make(map[string]interface{}),
		tracer:     t, // Attach the tracer to the span
		exporter:   t.exporter,
		sanitizer:  t.sanitizer,
	}

	if parentSpan != nil {
		span.TraceID = parentSpan.TraceID
		span.ParentSpanID = parentSpan.SpanID
	} else {
		// This is a new root span
		span.TraceID = uuid.New().String()
	}

	span.SpanID = uuid.New().String()

	// Return a new context containing this new span
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

// SetError adds error information to the span.
func (s *Span) SetError(message, stackTrace string) {
	s.Error = &SpanError{
		Message:    message,
		StackTrace: stackTrace,
	}
}

type tracerKey struct{}

// ContextWithTracer returns a new context with the given tracer.
func (t *Tracer) ContextWithTracer(ctx context.Context, tracer *Tracer) context.Context {
	return context.WithValue(ctx, tracerKey{}, tracer)
}

// TracerFromContext returns the tracer from the given context.
func TracerFromContext(ctx context.Context) (*Tracer, bool) {
	t, ok := ctx.Value(tracerKey{}).(*Tracer)
	return t, ok
}

// SpanFromContext returns the span from the given context.
func SpanFromContext(ctx context.Context) (*Span, bool) {
	s, ok := ctx.Value(spanKey{}).(*Span)
	return s, ok
}

// Tracer returns the tracer that created the span.
func (s *Span) Tracer() *Tracer {
	return s.tracer
}
