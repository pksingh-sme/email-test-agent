# Email QA Agentic Platform - Deterministic Tests

## Overview

The deterministic QA engine performs automated, rule-based checks on email content without requiring LLM inference. These tests are fast, reliable, and cover common email QA issues.

## Test Functions

### check_alt_text()

**File**: [backend/deterministic_tests.py](backend/deterministic_tests.py)

Checks for missing ALT text attributes on images.

**Logic**:
- Finds all `<img>` tags in the HTML
- Verifies each has an `alt` attribute
- Flags images with missing or empty ALT text

**Return Format**:
```json
{
  "test_name": "alt_text",
  "status": "pass|fail",
  "details": "string"
}
```

### check_links()

**File**: [backend/deterministic_tests.py](backend/deterministic_tests.py)

Validates links for proper formatting.

**Logic**:
- Finds all `<a>` tags with `href` attributes
- Checks if URLs start with valid protocols (http://, https://, mailto:, #)
- Flags malformed or suspicious links

**Return Format**:
```json
{
  "test_name": "links",
  "status": "pass|fail",
  "details": "string"
}
```

### check_subject_line()

**File**: [backend/deterministic_tests.py](backend/deterministic_tests.py)

Ensures emails have a subject line.

**Logic**:
- Checks metadata for `subject` field
- Verifies subject is not empty or whitespace-only

**Return Format**:
```json
{
  "test_name": "subject_line",
  "status": "pass|fail",
  "details": "string"
}
```

### check_preheader()

**File**: [backend/deterministic_tests.py](backend/deterministic_tests.py)

Ensures emails have preheader text.

**Logic**:
- Checks metadata for `preheader` field
- Verifies preheader is not empty or whitespace-only

**Return Format**:
```json
{
  "test_name": "preheader",
  "status": "pass|fail",
  "details": "string"
}
```

### check_template_meta()

**File**: [backend/deterministic_tests.py](backend/deterministic_tests.py)

Verifies template metadata completeness.

**Logic**:
- Checks for `template_name` in metadata
- Checks for `locale` in metadata
- Flags missing or empty metadata fields

**Return Format**:
```json
{
  "test_name": "template_meta",
  "status": "pass|fail",
  "details": "string"
}
```

### check_width()

**File**: [backend/deterministic_tests.py](backend/deterministic_tests.py)

Checks for element width specifications.

**Logic**:
- Searches HTML for width-related attributes (`width=`, `style=`)
- Flags emails with no width specifications

**Return Format**:
```json
{
  "test_name": "width",
  "status": "pass|fail",
  "details": "string"
}
```

### check_background_color()

**File**: [backend/deterministic_tests.py](backend/deterministic_tests.py)

Checks for background color declarations.

**Logic**:
- Searches HTML for background color declarations (`background-color:`, `bgcolor=`)
- Flags emails with no background color specifications

**Return Format**:
```json
{
  "test_name": "background_color",
  "status": "pass|fail",
  "details": "string"
}
```

### check_image_dimensions()

**File**: [backend/deterministic_tests.py](backend/deterministic_tests.py)

Ensures images have dimension attributes.

**Logic**:
- Finds all `<img>` tags
- Checks for `width` and `height` attributes
- Flags images missing both dimensions

**Return Format**:
```json
{
  "test_name": "image_dimensions",
  "status": "pass|fail",
  "details": "string"
}
```

### check_long_copy()

**File**: [backend/deterministic_tests.py](backend/deterministic_tests.py)

Identifies excessively long text lines.

**Logic**:
- Extracts text content from HTML
- Checks for text lines longer than 200 characters
- Flags long text blocks

**Return Format**:
```json
{
  "test_name": "long_copy",
  "status": "pass|fail",
  "details": "string"
}
```

## Running Tests

To run all deterministic tests:

```python
from deterministic_tests import run_all_deterministic_tests

results = run_all_deterministic_tests(html_content, metadata)
```

## Test Results Format

All deterministic tests return results in a consistent format:

```json
[
  {
    "test_name": "string",
    "status": "pass|fail",
    "details": "string"
  }
]
```

## Adding New Tests

To add a new deterministic test:

1. Create a new function in [backend/deterministic_tests.py](backend/deterministic_tests.py)
2. Follow the naming convention `check_[test_name]()`
3. Ensure the function returns the standard result format
4. Add the test to `run_all_deterministic_tests()`
5. Add unit tests in [backend/tests/test_deterministic_tests.py](backend/tests/test_deterministic_tests.py)
6. Update this documentation

## Performance

Deterministic tests are designed to be fast and lightweight:
- Average execution time: < 100ms per email
- Memory usage: < 10MB
- No external API calls required