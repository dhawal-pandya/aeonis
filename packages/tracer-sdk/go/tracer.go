package tracer

import (
	"context"
	"os"
	"reflect"
	"runtime"
	"time"

	"github.com/google/uuid"
)

const tracerVersion = "0.3.0"

// tracer is the entry point for creating spans.
type Tracer struct {
	serviceName       string
	exporter          Exporter
	sanitizer         Sanitizer
	commitID          string
	sdkVersion        string
	resourceAttributes map[string]interface{}
}

// newtracer creates a new tracer with a default http exporter.
func NewTracer(serviceName, endpointURL, apiKey string, sanitizer Sanitizer) *Tracer {
	exporter := NewHTTPExporter(endpointURL, apiKey)
	return NewTracerWithExporter(serviceName, exporter, sanitizer)
}

// newtracerwithexporter creates a new tracer with a custom exporter.
func NewTracerWithExporter(serviceName string, exporter Exporter, sanitizer Sanitizer) *Tracer {
	if sanitizer == nil {
		sanitizer = &NoOpSanitizer{}
	}

	commitID := os.Getenv("AEONIS_COMMIT_ID")
	if commitID == "" {
		commitID = "local"
	}

	return &Tracer{
		serviceName:       serviceName,
		exporter:          exporter,
		sanitizer:         sanitizer,
		commitID:          commitID,
		sdkVersion:        tracerVersion,
		resourceAttributes: make(map[string]interface{}),
	}
}

// setapikey sets the api key for the http exporter.
// this is useful for testing, but not recommended for production use.
func (t *Tracer) SetAPIKey(apiKey string) {
	if exporter, ok := t.exporter.(*HTTPExporter); ok {
		exporter.apiKey = apiKey
	}
}

// shutdown calls the exporter's shutdown method.
func (t *Tracer) Shutdown() {
	if exporter, ok := t.exporter.(interface{ Shutdown() }); ok {
		exporter.Shutdown()
	}
}

// startspan starts a new span.
func (t *Tracer) StartSpan(ctx context.Context, name string) (context.Context, *Span) {
	parentSpan, _ := fromContext(ctx)

	span := &Span{
		Name:       name,
		StartTime:  time.Now().UTC(),
		Attributes: make(map[string]interface{}),
		tracer:     t,
		exporter:   t.exporter,
		sanitizer:  t.sanitizer,
		CommitID:   t.commitID,
		SDKVersion: t.sdkVersion,
	}

	// add resource attributes to the span
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

// setattributes sets the attributes for the span, applying sanitization.
func (s *Span) SetAttributes(attributes map[string]interface{}) {
	// merge new attributes with existing (resource) attributes
	for k, v := range s.sanitizer.Sanitize(attributes) {
		s.Attributes[k] = v
	}
}

// end completes the span, calculating the duration and exporting it.
func (s *Span) End() {
	s.EndTime = time.Now().UTC()
	if s.exporter != nil {
		s.exporter.Export(s)
	}
}

// seterror adds error information to the span.
func (s *Span) SetError(message, stackTrace string) {
	s.Error = &SpanError{
		Message:    message,
		StackTrace: stackTrace,
	}
}

type tracerKey struct{}

// contextwithtracer returns a new context with the given tracer.
func (t *Tracer) ContextWithTracer(ctx context.Context, tracer *Tracer) context.Context {
	return context.WithValue(ctx, tracerKey{}, tracer)
}

// tracerfromcontext returns the tracer from the given context.
func TracerFromContext(ctx context.Context) (*Tracer, bool) {
	t, ok := ctx.Value(tracerKey{}).(*Tracer)
	return t, ok
}

// spanfromcontext returns the span from the given context.
func SpanFromContext(ctx context.Context) (*Span, bool) {
	s, ok := ctx.Value(spanKey{}).(*Span)
	return s, ok
}

// contextwithspan returns a new context with the given span.
func ContextWithSpan(ctx context.Context, span *Span) context.Context {
	return context.WithValue(ctx, spanKey{}, span)
}

// tracer returns the tracer that created the span.
func (s *Span) Tracer() *Tracer {
	return s.tracer
}

// tracefunc is a helper function that wraps a function call in a span.
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
