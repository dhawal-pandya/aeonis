package tracer

import "context"

type contextKey string

const spanContextKey = contextKey("aeonis.span")

type spanContext struct {
	traceID string
	spanID  string
}

func toContext(ctx context.Context, span *Span) context.Context {
	return context.WithValue(ctx, spanContextKey, spanContext{
		traceID: span.TraceID,
		spanID:  span.SpanID,
	})
}

func fromContext(ctx context.Context) (spanContext, bool) {
	sc, ok := ctx.Value(spanContextKey).(spanContext)
	return sc, ok
}
