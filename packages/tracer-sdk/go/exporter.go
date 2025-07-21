package tracer

import (
	"bytes"
	"encoding/json"
	"log"
	"net/http"
	"os"
	"time"
)

// exporter is the interface for exporting spans.
type Exporter interface {
	Export(span *Span)
}

// fileexporter writes spans to a file.
type FileExporter struct {
	file *os.File
}

// newfileexporter creates a new file exporter.
func NewFileExporter(filename string) *FileExporter {
	f, err := os.OpenFile(filename, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Fatalf("failed to open file: %v", err)
	}
	return &FileExporter{file: f}
}

// export writes a span to the file.
func (e *FileExporter) Export(span *Span) {
	data, err := json.Marshal(span)
	if err != nil {
		log.Printf("failed to marshal span: %v", err)
		return
	}
	if _, err := e.file.Write(append(data, '\n')); err != nil {
		log.Printf("failed to write span to file: %v", err)
	}
}

// close closes the file.
func (e *FileExporter) Close() {
	if err := e.file.Close(); err != nil {
		log.Printf("failed to close file: %v", err)
	}
}

// httpexporter sends spans to an http endpoint.
type HTTPExporter struct {
	endpointURL string
	apiKey      string
	client      *http.Client
	spanChannel chan *Span
}

// newhttpexporter creates a new http exporter.
func NewHTTPExporter(endpointURL string, apiKey string) *HTTPExporter {
	exporter := &HTTPExporter{
		endpointURL: endpointURL,
		apiKey:      apiKey,
		client:      &http.Client{Timeout: 5 * time.Second},
		spanChannel: make(chan *Span, 1000),
	}

	go exporter.startBatchProcessor()

	return exporter
}

// export sends a span to the exporter's channel.
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
	req.Header.Set("X-Aeonis-API-Key", e.apiKey)

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
