package tracer

import "context"

// spanKey is an unexported type to be used as the key for the context value.
type spanKey struct{}

// toContext embeds a span into a new context.
func toContext(ctx context.Context, span *Span) context.Context {
	return context.WithValue(ctx, spanKey{}, span)
}

// fromContext retrieves a span from a context.
func fromContext(ctx context.Context) (*Span, bool) {
	s, ok := ctx.Value(spanKey{}).(*Span)
	return s, ok
}
