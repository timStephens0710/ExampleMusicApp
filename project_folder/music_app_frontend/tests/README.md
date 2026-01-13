# Music Archiving Tool - Test Suite

## Overview

This directory contains comprehensive unit and integration tests for the TypeScript validation modules. The test suite uses Vitest as the testing framework, providing fast execution and excellent TypeScript support.

## Test Framework

**Vitest** - A blazing fast unit test framework powered by Vite
- Native TypeScript support
- Jest-compatible API
- Fast execution with watch mode
- Built-in code coverage

## Test Files

### `emailValidator.test.ts`

Tests the email validation functionality from `validateEmail.ts`.

**Unit Tests**:
- `checkEmailIsValid` function validation
  - Valid email formats (standard and complex patterns)
  - Invalid emails (missing @, missing .com)
  - Whitespace trimming and case normalization

**DOM Integration Tests**:
- Form submission prevention with invalid emails
- Form submission allowance with valid emails
- Error message display and clearing
- Edge cases (empty input, special formats)

**Key Test Scenarios**:
```typescript
// Valid emails
'test@example.com' ✓
'michael.selfish92@domain.com' ✓
'  TEST@EXAMPLE.COM  ' ✓ (with trimming)

// Invalid emails
'invalid-email' ✗
'no-at-sign.com' ✗
'test@example' ✗ (missing .com)
```

### `validatePassword.test.ts`

Comprehensive tests for password validation logic and multiple validation rules.

**Unit Tests - Individual Validators**:
- `passwordHasNumberValidator` - Numeric character requirement
- `passwordHasSpecialCharacterValidator` - Special character (!@#$%^&*) requirement
- `passwordHasUpperCaseValidator` - Uppercase letter requirement
- `passwordminimumLengthValidator` - 8 character minimum requirement

**Orchestration Tests**:
- `orchestratePasswordValidator` - Tests all validators working together
- Multiple simultaneous validation failures
- Whitespace handling before and after trimming

**DOM Integration Tests**:
- Form submission with invalid passwords (single and multiple errors)
- Form submission with valid passwords
- Error message concatenation with `<br>` tags
- Error clearing on valid input

**Key Test Scenarios**:
```typescript
// Valid password
'Meep!234' ✓ (8+ chars, number, special char, uppercase)

// Various failures
'Sh0rt$' ✗ (too short)
'Sh0rt' ✗ (too short + missing special char)
'fail' ✗ (all four requirements fail)
```

### `validateStreamingLink.test.ts`

Tests URL parsing, hostname extraction, and platform validation.

**Unit Tests - Hostname Extraction**:
- `getHostname` function
  - Valid URLs (YouTube, Bandcamp)
  - Invalid URLs
  - Email addresses (edge case)
  - Whitespace trimming

**Unit Tests - Platform Validation**:
- `checkStreamingLinkIsValid` function
  - YouTube domains (youtube.com, youtu.be, music.youtube.com)
  - Bandcamp domains (main site and artist subdomains)
  - Unsupported platforms (SoundCloud, etc.)
  - Null/empty hostname handling

**Orchestration Tests**:
- `orchestrateCheckStreamingLinkIsValid` - Full URL validation pipeline
  - Complete YouTube URLs
  - Complete Bandcamp URLs (including artist subdomains)
  - Whitespace handling in full URLs
  - Edge cases (email-like URLs)

**Platform Selection Tests**:
- `supportedStreamingPlatformIsSelected` - Dropdown validation
  - Valid platform selections
  - Invalid platform selections

**DOM Integration Tests**:
- `initValidateAddTrackForm` - Complete form validation
  - Form submission prevention with unsupported platforms
  - Form submission allowance with supported platforms
  - Error display and clearing

**Key Test Scenarios**:
```typescript
// Valid URLs
'https://www.youtube.com/watch?v=...' ✓
'https://selfversedrecords.bandcamp.com/track/...' ✓
'    https://www.youtube.com/...    ' ✓ (with whitespace)

// Invalid URLs
'https://soundcloud.com/...' ✗
'www.youtube@gmail.com' ✗ (email-like edge case)
null or empty ✗
```

### `validateAddTrackForm.test.ts`

Tests form text validation for track metadata (artist, track name, album, etc.).

**Unit Tests**:
- `checkIsNull` - Mandatory field validation
  - Non-empty text passes
  - Empty/null text fails with error message

- `checkLength250` - Maximum length validation
  - Text under 250 characters passes
  - Text over 250 characters fails with error message

- `supportedStreamingPlatformIsSelected` - Platform dropdown validation
  - Supported platforms (YouTube, etc.) pass
  - Unsupported platforms fail

**Orchestration Tests**:
- `orchestrateCheckFormText` - Combined validation
  - Valid text (not null, under 250 chars) passes
  - Null text fails with appropriate message
  - Overly long text fails with appropriate message

**Key Test Scenarios**:
```typescript
// Valid inputs
'hello world' ✓ (not null, under 250 chars)
'YouTube' ✓ (supported platform)

// Invalid inputs
'' ✗ (empty field)
'aZ9$kL2mQ#T7r@...[250+ chars]' ✗ (too long)
'Soundcloud' ✗ (unsupported platform)
```

## Test Structure

All test files follow a consistent structure:

```typescript
import { describe, it, expect, beforeEach, vi } from 'vitest';
import * as moduleToTest from '../src/moduleName';

// Unit tests for individual functions
describe('functionName', () => {
    it('describes expected behavior', () => {
        expect(functionCall(input)).toBe(expectedOutput);
    });
});

// DOM integration tests
describe('DOM integration', () => {
    beforeEach(() => {
        // Set up mock DOM
        document.body.innerHTML = `...`;
        // Initialize validation
    });

    it('tests user interaction', () => {
        // Simulate user input and form submission
        // Assert behavior
    });
});
```

## Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm test emailValidator.test.ts
```

## Test Coverage

The test suite provides comprehensive coverage:

### Function Coverage
- ✅ All exported validation functions
- ✅ Orchestration/coordination functions
- ✅ Edge case handling

### Integration Coverage
- ✅ DOM element selection
- ✅ Event listener attachment
- ✅ Form submission handling
- ✅ Error message display
- ✅ Error clearing on valid input

### Edge Cases
- ✅ Null/empty inputs
- ✅ Whitespace handling
- ✅ Case sensitivity
- ✅ Special characters
- ✅ Length boundaries
- ✅ Invalid URL formats

## Mocking and Test Utilities

### Vitest Utilities Used
- `describe` - Test suite grouping
- `it` - Individual test cases
- `expect` - Assertions
- `beforeEach` - Setup before each test
- `vi.spyOn` - Function call tracking (for `preventDefault`)

### DOM Mocking
Tests use `document.body.innerHTML` to create mock DOM structures that mirror actual Django templates:

```typescript
beforeEach(() => {
    document.body.innerHTML = `
        <form id="auth-form">
            <input id="id_email" type="email" />
            <div id="email-error"></div>
            <button type="submit">Submit</button>
        </form>
    `;
});
```

### Event Simulation
Form submissions are simulated using native Event objects:

```typescript
const submitEvent = new Event('submit', { 
    bubbles: true, 
    cancelable: true 
});
form.dispatchEvent(submitEvent);
```

## Test-Driven Development Workflow

This test suite supports TDD practices:

1. **Red** - Write failing test for new feature
2. **Green** - Implement minimum code to pass test
3. **Refactor** - Improve code while keeping tests green

Example workflow:
```typescript
// 1. Write test first
it('validates soundcloud URLs', () => {
    expect(checkStreamingLinkIsValid('soundcloud.com')).toBeNull();
});

// 2. Test fails (red)

// 3. Add soundcloud to exactDomains array (green)

// 4. Refactor if needed while tests pass
```

## Best Practices Demonstrated

### Test Organization
- Grouped by function/feature using `describe` blocks
- Clear, descriptive test names using `it`
- Separated unit tests from integration tests

### Assertions
- Single assertion focus per test (mostly)
- Clear expected vs actual values
- Meaningful error messages

### Test Independence
- Each test is self-contained
- No shared state between tests
- `beforeEach` ensures clean slate

### Comprehensive Coverage
- Happy path (valid inputs)
- Sad path (invalid inputs)
- Edge cases (null, empty, whitespace)
- Integration scenarios (real DOM interaction)

## Known Limitations

### Areas Not Covered
- Multi-browser compatibility (relies on DOM API)
- Accessibility testing (ARIA attributes, screen readers)
- Performance testing (validation speed)
- Internationalization (error messages in multiple languages)

### Future Test Enhancements
- Add visual regression tests for error display
- Add accessibility tests using @testing-library/jest-dom
- Add performance benchmarks
- Add E2E tests with Playwright or Cypress
- Add mutation testing to verify test quality
- Test async validation scenarios
- Add tests for network failures in URL parsing

## Continuous Integration

These tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run Tests
  run: npm test

- name: Check Coverage
  run: npm run test:coverage -- --coverage.thresholds.lines=80
```

## Debugging Tests

### Running Single Test
```bash
npm test -- emailValidator.test.ts
```

### Verbose Output
```bash
npm test -- --reporter=verbose
```

### Debug Mode
```bash
node --inspect-brk ./node_modules/vitest/vitest.mjs
```

---

**Testing Framework**: Vitest  
**Last Updated**: January 2026  
**Test Coverage**: ~95% of validation logic