package tracer

import (
	"bytes"
	"encoding/json"
	"log"
	"net/http"
	"time"
)

// Exporter is the interface for exporting spans.
type Exporter interface {
	Export(span *Span)
}

// HTTPExporter sends spans to an HTTP endpoint.
type HTTPExporter struct {
	endpointURL string
	client      *http.Client
	spanChannel chan *Span
}

// NewHTTPExporter creates a new HTTP exporter.
func NewHTTPExporter(endpointURL string) *HTTPExporter {
	exporter := &HTTPExporter{
		endpointURL: endpointURL,
		client:      &http.Client{Timeout: 5 * time.Second},
		spanChannel: make(chan *Span, 1000),
	}

	go exporter.startBatchProcessor()

	return exporter
}

// Export sends a span to the exporter's channel.
func (e *HTTPExporter) Export(span *Span) {
	e.spanChannel <- span
}

func (e *HTTPExporter) startBatchProcessor() {
	ticker := time.NewTicker(5 * time.Second)
	defer ticker.Stop()

	var batch []*Span
	for {
		select {
		case span := <-e.spanChannel:
			batch = append(batch, span)
			if len(batch) >= 50 {
				e.sendBatch(batch)
				batch = nil
			}
		case <-ticker.C:
			if len(batch) > 0 {
				e.sendBatch(batch)
				batch = nil
			}
		}
	}
}

func (e *HTTPExporter) sendBatch(batch []*Span) {
	jsonData, err := json.Marshal(batch)
	if err != nil {
		log.Printf("failed to marshal spans: %v", err)
		return
	}

	req, err := http.NewRequest("POST", e.endpointURL, bytes.NewBuffer(jsonData))
	if err != nil {
		log.Printf("failed to create request: %v", err)
		return
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := e.client.Do(req)
	if err != nil {
		log.Printf("failed to send spans: %v", err)
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		log.Printf("server returned error: %s", resp.Status)
	}
}
