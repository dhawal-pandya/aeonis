package tracer

import (
	"context"
	"testing"
)

// MockExporter is a fake exporter for testing.
type MockExporter struct {
	Spans []*Span
}

// Export appends the span to the Spans slice.
func (m *MockExporter) Export(span *Span) {
	m.Spans = append(m.Spans, span)
}

// Reset clears the recorded spans.
func (m *MockExporter) Reset() {
	m.Spans = nil
}

func TestTracer(t *testing.T) {
	mockExporter := &MockExporter{}
	sanitizer := &NoOpSanitizer{}
	tracer := NewTracerWithExporter("test-service", mockExporter, sanitizer)

	t.Run("Creates a root span correctly", func(t *testing.T) {
		mockExporter.Reset()
		_, span := tracer.StartSpan(context.Background(), "root-operation")
		span.End()

		if len(mockExporter.Spans) != 1 {
			t.Fatalf("Expected 1 span to be exported, got %d", len(mockExporter.Spans))
		}
		exportedSpan := mockExporter.Spans[0]
		if exportedSpan.TraceID == "" {
			t.Error("Expected a TraceID to be generated for a root span")
		}
		if exportedSpan.ParentSpanID != "" {
			t.Errorf("Expected ParentSpanID to be empty for a root span, got '%s'", exportedSpan.ParentSpanID)
		}
		if exportedSpan.Name != "root-operation" {
			t.Errorf("Expected span name 'root-operation', got '%s'", exportedSpan.Name)
		}
	})

	t.Run("Creates a child span correctly", func(t *testing.T) {
		mockExporter.Reset()
		ctx, parentSpan := tracer.StartSpan(context.Background(), "parent-op")
		_, childSpan := tracer.StartSpan(ctx, "child-op")
		childSpan.End()
		parentSpan.End()

		if len(mockExporter.Spans) != 2 {
			t.Fatalf("Expected 2 spans to be exported, got %d", len(mockExporter.Spans))
		}
		// The child span ends first, so it's usually exported first.
		// However, with channels, the order isn't guaranteed. So we find them.
		var exportedChild, exportedParent *Span
		for _, s := range mockExporter.Spans {
			if s.Name == "child-op" {
				exportedChild = s
			}
			if s.Name == "parent-op" {
				exportedParent = s
			}
		}

		if exportedChild == nil || exportedParent == nil {
			t.Fatal("Could not find both parent and child spans in exported data")
		}

		if exportedChild.TraceID != exportedParent.TraceID {
			t.Errorf("Expected child and parent to have the same TraceID. Parent: %s, Child: %s",
				exportedParent.TraceID, exportedChild.TraceID)
		}
		if exportedChild.ParentSpanID != exportedParent.SpanID {
			t.Errorf("Expected child's ParentSpanID ('%s') to match parent's SpanID ('%s')",
				exportedChild.ParentSpanID, exportedParent.SpanID)
		}
	})

	t.Run("SetAttributes uses the sanitizer", func(t *testing.T) {
		mockExporter.Reset()
		piiSanitizer := NewPIISanitizer()
		piiTracer := NewTracerWithExporter("pii-test-service", mockExporter, piiSanitizer)

		_, span := piiTracer.StartSpan(context.Background(), "pii-op")
		span.SetAttributes(map[string]interface{}{
			"email": "test@example.com",
		})
		span.End()

		if len(mockExporter.Spans) != 1 {
			t.Fatal("Expected 1 span to be exported")
		}
		exportedSpan := mockExporter.Spans[0]
		sanitizedEmail, ok := exportedSpan.Attributes["email"].(string)
		if !ok || sanitizedEmail != "test...example.com" {
			t.Errorf("Expected email to be sanitized, got: %v", exportedSpan.Attributes["email"])
		}
	})
}
