package tracer

import (
	"context"
	"os"
	"reflect"
	"runtime"
	"time"

	"github.com/google/uuid"
)

const tracerVersion = "0.2.0"

// Tracer is the entry point for creating spans.
type Tracer struct {
	serviceName       string
	exporter          Exporter
	sanitizer         Sanitizer
	resourceAttributes map[string]interface{}
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

	resourceAttributes := map[string]interface{}{
		"telemetry.sdk.version": tracerVersion,
	}
	if commitID := os.Getenv("AEONIS_COMMIT_ID"); commitID != "" {
		resourceAttributes["service.version"] = commitID
	}

	return &Tracer{
		serviceName:       serviceName,
		exporter:          exporter,
		sanitizer:         sanitizer,
		resourceAttributes: resourceAttributes,
	}
}

// StartSpan starts a new span.
func (t *Tracer) StartSpan(ctx context.Context, name string) (context.Context, *Span) {
	parentSpan, _ := fromContext(ctx)

	span := &Span{
		Name:       name,
		StartTime:  time.Now().UTC(),
		Attributes: make(map[string]interface{}),
		tracer:     t,
		exporter:   t.exporter,
		sanitizer:  t.sanitizer,
	}

	// Add resource attributes to the span
	for k, v := range t.resourceAttributes {
		span.Attributes[k] = v
	}

	if parentSpan != nil {
		span.TraceID = parentSpan.TraceID
		span.ParentSpanID = parentSpan.SpanID
	} else {
		span.TraceID = uuid.New().String()
	}

	span.SpanID = uuid.New().String()

	return toContext(ctx, span), span
}

// SetAttributes sets the attributes for the span, applying sanitization.
func (s *Span) SetAttributes(attributes map[string]interface{}) {
	// Merge new attributes with existing (resource) attributes
	for k, v := range s.sanitizer.Sanitize(attributes) {
		s.Attributes[k] = v
	}
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

// ContextWithSpan returns a new context with the given span.
func ContextWithSpan(ctx context.Context, span *Span) context.Context {
	return context.WithValue(ctx, spanKey{}, span)
}

// Tracer returns the tracer that created the span.
func (s *Span) Tracer() *Tracer {
	return s.tracer
}

// TraceFunc is a helper function that wraps a function call in a span.
func (t *Tracer) TraceFunc(ctx context.Context, fn interface{}, params ...interface{}) []interface{} {

	funcName := runtime.FuncForPC(reflect.ValueOf(fn).Pointer()).Name()
	_, file, line, _ := runtime.Caller(1)

	ctx, span := t.StartSpan(ctx, funcName)
	defer span.End()

	span.SetAttributes(map[string]interface{}{
		"code.function": funcName,
		"code.filepath": file,
		"code.lineno":   line,
	})

	v := reflect.ValueOf(fn)
	in := make([]reflect.Value, len(params))
	for i, param := range params {
		in[i] = reflect.ValueOf(param)
	}
	out := v.Call(in)

	returnValues := make([]interface{}, len(out))
	for i, val := range out {
		if err, ok := val.Interface().(error); ok && err != nil {
			span.SetError(err.Error(), "") // assuming no stack trace for now
		}
		returnValues[i] = val.Interface()
	}
	span.SetAttributes(map[string]interface{}{
		"function.args":   params,
		"function.return": returnValues,
	})

	return returnValues
}
