# Music Archiving Tool - Test Suite

## Overview

This directory contains comprehensive unit and integration tests for the TypeScript validation modules. The test suite uses Vitest as the testing framework, providing fast execution and excellent TypeScript support.

There are 80 unit tests in total.

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

### `dynamicAddTrackForm.test.ts`

Tests dynamic form behavior that adapts the UI based on track type selection (track vs. mix).

**Form Initialization Tests**:
- Element discovery and validation
  - All required form elements found
  - All optional container elements found
  - Graceful handling of missing forms

**Track Type: "track" Selected**:
- Label updates to "Track Name"
- Mix page container hidden
- Album name container visible
- Record label container visible
- Purchase link container visible

**Track Type: "mix" Selected**:
- Label updates to "Mix Name"
- Mix page container visible
- Album name container hidden
- Record label container hidden
- Purchase link container hidden

**Event Handling Tests**:
- Form updates on track type change
- Pre-filled values handled correctly (Django forms)
- Real-time UI adaptation

**MutationObserver Behavior**:
- Detects when form is added to DOM
- Stops observing after form is found
- Handles asynchronous DOM injection

**Edge Cases**:
- Missing optional containers handled gracefully
- Invalid track type values default to "mix" behavior
- No errors thrown with incomplete DOM

**Key Test Scenarios**:
```typescript
// Track type selection
'track' → Show album fields, hide mix fields ✓
'mix' → Show mix fields, hide album fields ✓

// Label updates
'track' → "Track Name" ✓
'mix' → "Mix Name" ✓

// DOM injection
Form added after page load → Detected and initialized ✓
```

### `deletePlaylists.test.ts` 

Tests the playlist deletion workflow including UI state management, modal interactions, and API requests.

**Initialization Tests**:
- Element discovery and validation
- Bootstrap Modal instantiation
- Event listener attachment
- CSRF token extraction from cookies

**Edit Button Behavior**:
- Shows checkboxes in all table rows
- Shows checkbox column header
- Reveals Delete and Cancel buttons
- Hides Edit button itself

**Cancel Button Behavior**:
- Hides all checkboxes and checkbox header
- Unchecks all previously checked checkboxes
- Hides Delete and Cancel buttons
- Shows Edit button again
- Resets UI to initial state

**Delete Button Behavior**:
- Shows confirmation modal when checkboxes are selected
- Shows confirmation modal even with no checkboxes selected (allows graceful no-op)
- Collects playlist IDs from checked rows using `data-playlist-id` attributes
- Uses Set collection to prevent duplicate IDs

**Confirm Delete Button Behavior**:
- Sends DELETE request to correct URL (from `data-delete-url` attribute)
- Includes correct headers:
  - `Content-Type: application/json`
  - `X-CSRFToken` with value from cookies
- Sends correct payload format: `{ playlist_id: [1, 2, 3] }`
- Hides modal on successful deletion
- Reloads page on success
- Does not reload page on failure
- Unchecks all checkboxes after successful deletion

**Mock Testing Patterns**:
- Bootstrap Modal mocked with `show()` and `hide()` methods
- `fetch` API mocked to avoid real network requests
- `window.location.reload` mocked to prevent actual page reload
- CSRF token injected via `document.cookie`

**Key Test Scenarios**:
```typescript
// UI State Management
Edit → Checkboxes visible ✓
Cancel → UI reset, checkboxes unchecked ✓

// API Integration
DELETE request sent with correct payload ✓
CSRF token included in headers ✓
Correct URL endpoint called ✓

// Success Flow
success: true → Modal hidden, page reloaded ✓

// Failure Flow
success: false → No page reload ✓
```

### `deletePlaylistTracks.test.ts` 

Tests the track deletion workflow within playlists, including UI controls, confirmation flow, and DELETE requests.

**Initialization Tests**:
- Element discovery with track-specific selectors
- Bootstrap Modal setup
- Event listener binding
- CSRF token handling

**Edit Button Behavior**:
- Shows track checkboxes in all table rows
- Shows checkbox column header
- Reveals Delete and Cancel buttons
- Hides Edit button

**Cancel Button Behavior**:
- Hides all track checkboxes and header
- Unchecks all selected checkboxes
- Hides Delete and Cancel buttons
- Shows Edit button
- Complete UI state reset

**Delete Button Behavior**:
- Shows modal when tracks are selected
- Shows modal with no selections (graceful handling)
- Collects playlist track IDs from `data-playlist-track-id` attributes
- Uses integer IDs (contrast with UUID in actual implementation)
- Set collection for ID deduplication

**Confirm Delete Button Behavior**:
- Sends DELETE request to track-specific endpoint
- Includes proper headers:
  - `Content-Type: application/json`
  - `X-CSRFToken` from cookies
- Sends payload: `{ playlist_track_id: [1, 2] }`
- Hides modal after successful deletion
- Reloads page on success
- No reload on API failure
- Clears checkbox selections post-deletion

**Mock Testing Patterns**:
- Bootstrap Modal mocked globally
- `fetch` API completely mocked
- `window.location.reload` stubbed
- Cookie-based CSRF token injection

**Key Differences from deletePlaylists.test.ts**:
- Uses `data-playlist-track-id` instead of `data-playlist-id`
- Different CSS classes: `.playlist-track-checkbox-cell` vs `.playlist-checkbox-cell`
- Different button IDs: `#edit-playlist-tracks-btn` vs `#edit-playlists-btn`
- Different endpoint URL pattern
- Same testing patterns but different DOM structure

**Key Test Scenarios**:
```typescript
// UI State
Edit → Track checkboxes shown ✓
Cancel → Checkboxes hidden, unchecked ✓

// Deletion Flow
Modal shown on delete click ✓
DELETE request with correct track IDs ✓
CSRF protection via headers ✓

// Response Handling
Success → Modal hidden, page reloaded ✓
Failure → No reload, user can retry ✓
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
npm test dynamicAddTrackForm.test.ts
npm test deletePlaylists.test.ts
npm test deletePlaylistTracks.test.ts

# Run deletion tests only
npm test delete
```

## Test Coverage

The test suite provides comprehensive coverage:

### Function Coverage
- ✅ All exported validation functions
- ✅ Orchestration/coordination functions
- ✅ Edge case handling
- ✅ Dynamic UI behavior
- ✅ Deletion workflows (edit, cancel, delete, confirm)

### Integration Coverage
- ✅ DOM element selection
- ✅ Event listener attachment
- ✅ Form submission handling
- ✅ Error message display
- ✅ Error clearing on valid input
- ✅ Dynamic form field visibility
- ✅ MutationObserver patterns
- ✅ Bootstrap Modal integration
- ✅ Fetch API requests
- ✅ CSRF token handling
- ✅ Page reload behavior

### Edge Cases
- ✅ Null/empty inputs
- ✅ Whitespace handling
- ✅ Case sensitivity
- ✅ Special characters
- ✅ Length boundaries
- ✅ Invalid URL formats
- ✅ Missing DOM elements
- ✅ Asynchronous DOM injection
- ✅ No items selected for deletion
- ✅ Failed API responses
- ✅ Missing CSRF token

## Mocking and Test Utilities

### Vitest Utilities Used
- `describe` - Test suite grouping
- `it`/`test` - Individual test cases
- `expect` - Assertions
- `beforeEach` - Setup before each test
- `afterEach` - Cleanup after each test
- `vi.spyOn` - Function call tracking (for `preventDefault`)
- `vi.fn()` - Mock function creation
- `vi.clearAllMocks()` - Mock cleanup
- `vi.stubGlobal()` - Global object mocking (fetch, bootstrap, location)
- `vi.unstubAllGlobals()` - Restore global objects after tests
- `vi.waitFor()` - Async assertion helper

### Testing Library Integration
- `@testing-library/jest-dom/matchers` - Enhanced DOM assertions
  - `toBeInTheDocument()` - Element presence
  - Additional matchers for better readability

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
Form submissions and changes are simulated using native Event objects:

```typescript
const submitEvent = new Event('submit', { 
    bubbles: true, 
    cancelable: true 
});
form.dispatchEvent(submitEvent);

// Select change events
selectElement.dispatchEvent(new Event('change'));

// Button clicks
button.click();
```

### Bootstrap Modal Mocking

Deletion tests mock Bootstrap's Modal class:

```typescript
const mockShow = vi.fn();
const mockHide = vi.fn();

vi.stubGlobal('bootstrap', {
    Modal: vi.fn().mockImplementation(function(this: any) {
        this.show = mockShow;
        this.hide = mockHide;
    }),
});

// Later in tests
expect(mockShow).toHaveBeenCalledTimes(1);
expect(mockHide).toHaveBeenCalledTimes(1);
```

### Fetch API Mocking

DELETE requests are tested using mocked fetch:

```typescript
const mockFetch = vi.fn();
vi.stubGlobal('fetch', mockFetch);

mockFetch.mockResolvedValueOnce({
    json: async () => ({ success: true, deleted_count: 2 }),
});

// Assert fetch was called correctly
const [url, options] = mockFetch.mock.calls[0];
expect(options.method).toBe('DELETE');
expect(options.headers['X-CSRFToken']).toBe('testcsrftoken123');
```

### Location Reload Mocking

Page reload behavior is tested without actually reloading:

```typescript
const reloadMock = vi.fn();
vi.stubGlobal('location', {
    ...window.location,
    reload: reloadMock,
});

// Later
expect(reloadMock).toHaveBeenCalledTimes(1);
```

### CSRF Token Injection

Tests inject CSRF tokens via document.cookie:

```typescript
Object.defineProperty(document, 'cookie', {
    writable: true,
    value: 'csrftoken=testcsrftoken123',
});
```

### MutationObserver Testing
Dynamic DOM changes are tested using MutationObserver:

```typescript
const observer = new MutationObserver((mutations, obs) => {
    const form = document.getElementById('auth-form');
    if (form) {
        // Form detected
        obs.disconnect();
    }
});

observer.observe(document.body, {
    childList: true,
    subtree: true
});
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
- Clear, descriptive test names using `it`/`test`
- Separated unit tests from integration tests
- Logical test hierarchy (initialization → behavior → edge cases)

### Assertions
- Single assertion focus per test (mostly)
- Clear expected vs actual values
- Meaningful error messages
- Testing Library matchers for improved readability
- Async assertions with `vi.waitFor()`

### Test Independence
- Each test is self-contained
- No shared state between tests
- `beforeEach` ensures clean slate
- `afterEach` cleanup prevents side effects
- Mock cleanup with `vi.clearAllMocks()` and `vi.unstubAllGlobals()`

### Comprehensive Coverage
- Happy path (valid inputs)
- Sad path (invalid inputs)
- Edge cases (null, empty, whitespace, no selections)
- Integration scenarios (real DOM interaction)
- Asynchronous behavior (MutationObserver, fetch)
- Error handling and graceful degradation
- API response scenarios (success, failure)

### Deletion Test Patterns
- UI state transitions (edit → delete → cancel)
- Modal interaction flow
- Checkbox selection tracking
- API request validation (method, headers, payload)
- Success and failure response handling
- CSRF token inclusion
- Page reload behavior

## Known Limitations

### Areas Not Covered
- Multi-browser compatibility (relies on DOM API)
- Accessibility testing (ARIA attributes, screen readers)
- Performance testing (validation speed)
- Internationalization (error messages in multiple languages)
- Real network requests (URL validation is local)
- Actual Bootstrap Modal rendering
- Real page reloads (mocked for testing)
- Network failures and timeout scenarios
- Concurrent deletion attempts

### Future Test Enhancements
- Add visual regression tests for error display
- Add accessibility tests using @testing-library/jest-dom
- Add performance benchmarks
- Add E2E tests with Playwright or Cypress
- Add mutation testing to verify test quality
- Test async validation scenarios
- Add tests for network failures in URL parsing
- Test keyboard navigation and focus management
- Add tests for screen reader announcements
- Test optimistic UI updates
- Test loading states during DELETE requests
- Add tests for undo functionality
- Test batch deletion limits
- Add tests for deletion confirmation timeout

## Continuous Integration

These tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Install Dependencies
  run: npm ci

- name: Run Tests
  run: npm test

- name: Check Coverage
  run: npm run test:coverage -- --coverage.thresholds.lines=80
  
- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    files: ./coverage/coverage-final.json
```

## Debugging Tests

### Running Single Test
```bash
npm test -- emailValidator.test.ts
npm test -- dynamicAddTrackForm.test.ts
npm test -- deletePlaylists.test.ts
npm test -- deletePlaylistTracks.test.ts
```

### Verbose Output
```bash
npm test -- --reporter=verbose
```

### Debug Mode
```bash
node --inspect-brk ./node_modules/vitest/vitest.mjs
```

### Watch Mode for Specific Test
```bash
npm test -- --watch dynamicAddTrackForm.test.ts
npm test -- --watch deletePlaylists.test.ts
```

### Run Only Deletion Tests
```bash
npm test -- delete
# Runs both deletePlaylists.test.ts and deletePlaylistTracks.test.ts
```

## Common Test Patterns

### Testing Button Click Flows
```typescript
const editBtn = document.getElementById('edit-playlists-btn')!;
const deleteBtn = document.getElementById('delete-playlists-btn')!;

editBtn.click(); // Trigger edit mode

expect(editBtn.classList.contains('d-none')).toBe(true);
expect(deleteBtn.classList.contains('d-none')).toBe(false);
```

### Testing Checkbox State
```typescript
const checkbox = cell.querySelector<HTMLInputElement>('input[type="checkbox"]');
checkbox!.checked = true;

// After cancel
expect(checkbox?.checked).toBe(false);
```

### Testing API Calls
```typescript
await vi.waitFor(() => expect(mockFetch).toHaveBeenCalledTimes(1));

const [url, options] = mockFetch.mock.calls[0];
expect(url).toContain('/delete_playlists/');
expect(options.method).toBe('DELETE');
expect(JSON.parse(options.body)).toEqual({ playlist_id: [1] });
```

### Testing Async Flows
```typescript
confirmDeleteBtn.click();

await vi.waitFor(() => expect(reloadMock).toHaveBeenCalledTimes(1));
expect(mockHide).toHaveBeenCalledTimes(1);
```

---

**Testing Framework**: Vitest  
**Last Updated**: March 2026  
**Test Coverage**: ~95% of validation and deletion logic