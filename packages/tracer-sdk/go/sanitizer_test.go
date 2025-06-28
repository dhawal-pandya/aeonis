package tracer

import (
	"reflect"
	"testing"
)

func TestPIISanitizer(t *testing.T) {
	sanitizer := NewPIISanitizer()

	testCases := []struct {
		name     string
		input    map[string]interface{}
		expected map[string]interface{}
	}{
		{
			name:     "Sanitize Email",
			input:    map[string]interface{}{"user_email": "test.user+alias@example.com"},
			expected: map[string]interface{}{"user_email": "test...example.com"},
		},
		{
			name:     "Sanitize Short Email",
			input:    map[string]interface{}{"user_email": "me@example.com"},
			expected: map[string]interface{}{"user_email": "me...example.com"},
		},
		{
			name:     "Sanitize Credit Card with dashes",
			input:    map[string]interface{}{"cc_number": "1234-5678-9012-3456"},
			expected: map[string]interface{}{"cc_number": "****-****-****-3456"},
		},
		{
			name:     "Sanitize Credit Card with spaces",
			input:    map[string]interface{}{"cc_number": "1234 5678 9012 3456"},
			expected: map[string]interface{}{"cc_number": "****-****-****-3456"},
		},
		{
			name:     "Sanitize 10-digit Phone Number",
			input:    map[string]interface{}{"phone": "1234567890"},
			expected: map[string]interface{}{"phone": "...7890"},
		},
		{
			name:     "Sanitize 12-digit Phone Number",
			input:    map[string]interface{}{"phone": "112345678901"},
			expected: map[string]interface{}{"phone": "...8901"},
		},
		{
			name: "Sanitize Nested Map",
			input: map[string]interface{}{
				"user": map[string]interface{}{
					"email": "nested.email@domain.org",
					"details": map[string]interface{}{
						"card": "1111222233334444",
					},
				},
			},
			expected: map[string]interface{}{
				"user": map[string]interface{}{
					"email": "nest...domain.org",
					"details": map[string]interface{}{
						"card": "****-****-****-4444",
					},
				},
			},
		},
		{
			name: "Sanitize Slice of strings",
			input: map[string]interface{}{
				"contacts": []interface{}{"some.one@pii.com", "1234567890"},
			},
			expected: map[string]interface{}{
				"contacts": []interface{}{"some...pii.com", "...7890"},
			},
		},
		{
			name:     "No PII",
			input:    map[string]interface{}{"message": "This is a safe message"},
			expected: map[string]interface{}{"message": "This is a safe message"},
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			sanitized := sanitizer.Sanitize(tc.input)
			if !reflect.DeepEqual(sanitized, tc.expected) {
				t.Errorf("\nExpected: %v\nGot:      %v", tc.expected, sanitized)
			}
		})
	}
}

func TestNoOpSanitizer(t *testing.T) {
	sanitizer := &NoOpSanitizer{}
	input := map[string]interface{}{
		"email": "test@example.com",
		"phone": "1234567890",
	}
	sanitized := sanitizer.Sanitize(input)
	if !reflect.DeepEqual(input, sanitized) {
		t.Errorf("NoOpSanitizer should not modify attributes. Expected %v, got %v", input, sanitized)
	}
}