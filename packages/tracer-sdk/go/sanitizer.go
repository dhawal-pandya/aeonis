package tracer

import (
	"fmt"
	"regexp"
	"strings"
)

// Sanitizer is the interface for sanitizing attributes.
type Sanitizer interface {
	Sanitize(attributes map[string]interface{}) map[string]interface{}
}

// NoOpSanitizer is a sanitizer that does nothing.
type NoOpSanitizer struct{}

// Sanitize returns the attributes without modification.
func (s *NoOpSanitizer) Sanitize(attributes map[string]interface{}) map[string]interface{} {
	return attributes
}

// PIISanitizer scrubs attributes for PII.
type PIISanitizer struct {
	emailRegex      *regexp.Regexp
	phoneRegex      *regexp.Regexp
	cardRegex *regexp.Regexp
}

// NewPIISanitizer creates a new PII sanitizer.
func NewPIISanitizer() *PIISanitizer {
	return &PIISanitizer{
		emailRegex:      regexp.MustCompile(`(?i)[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}`),
		phoneRegex:      regexp.MustCompile(`\b\d{10,15}\b`),
		cardRegex: regexp.MustCompile(`\b(?:\d[ -]*?){13,16}\b`),
	}
}

// Sanitize recursively scrubs map and string values for PII.
func (s *PIISanitizer) Sanitize(attributes map[string]interface{}) map[string]interface{} {
	sanitized := make(map[string]interface{}, len(attributes))
	for key, val := range attributes {
		sanitized[key] = s.sanitizeValue(val)
	}
	return sanitized
}

func (s *PIISanitizer) sanitizeValue(value interface{}) interface{} {
	switch v := value.(type) {
	case string:
		return s.sanitizeString(v)
	case map[string]interface{}:
		return s.Sanitize(v) // Recurse for nested maps
	case []interface{}:
		sanitizedSlice := make([]interface{}, len(v))
		for i, item := range v {
			sanitizedSlice[i] = s.sanitizeValue(item)
		}
		return sanitizedSlice
	default:
		return v
	}
}

func (s *PIISanitizer) sanitizeString(sVal string) string {
	sVal = s.cardRegex.ReplaceAllStringFunc(sVal, func(cc string) string {
		re := regexp.MustCompile(`\D`)
		digits := re.ReplaceAllString(cc, "")
		if len(digits) > 4 {
			return fmt.Sprintf("****-****-****-%s", digits[len(digits)-4:])
		}
		return "****"
	})

	sVal = s.emailRegex.ReplaceAllStringFunc(sVal, func(email string) string {
		parts := strings.Split(email, "@")
		if len(parts) != 2 {
			return "***@***"
		}
		local, domain := parts[0], parts[1]
		if len(local) > 4 {
			local = local[:4]
		}
		return fmt.Sprintf("%s...%s", local, domain)
	})

	sVal = s.phoneRegex.ReplaceAllStringFunc(sVal, func(phone string) string {
		if len(phone) > 4 {
			return fmt.Sprintf("...%s", phone[len(phone)-4:])
		}
		return "..."
	})

	return sVal
}
