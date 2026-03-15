# Music Archiving Tool - Frontend TypeScript Modules

## Overview

This directory contains the TypeScript modules for a music archiving tool built with Django and TypeScript. The application provides comprehensive client-side validation for user authentication workflows and music content management, with a focus on user experience and data integrity.

## Architecture

The codebase follows a modular architecture where each validation concern is separated into its own TypeScript module. All modules integrate seamlessly with Django forms through DOM event listeners and provide real-time feedback to users.

## Modules

### Authentication & User Management

#### `musicAppAuth.ts`
Defines TypeScript interfaces for authentication forms used throughout the application:
- `RegistrationForm` - User registration with email, username, and password confirmation
- `LoginForm` - Standard email/password authentication
- `ForgottenPasswordForm` - Password recovery initiation
- `ResetPasswordForm` - Password reset confirmation with dual-entry verification

**Usage**: Import these interfaces in other modules to ensure type safety when working with authentication form data.

#### `validateEmail.ts`
Validates email addresses against standard formatting rules.

**Features**:
- Email pattern validation (must contain '@' and end with '.com')
- Case-insensitive validation with automatic trimming
- Real-time error display on form submission
- Prevents form submission until valid email is provided

**Exported Functions**:
- `checkEmailIsValid(email: string): null | string` - Returns error message or null if valid

#### `validatePassword.ts`
Comprehensive password validation with multiple security requirements.

**Features**:
- Validates against four security rules:
  - Minimum 8 characters
  - At least one number
  - At least one special character (!@#$%^&*)
  - At least one uppercase letter
- Supports multiple password fields in a single form (e.g., password + confirm password)
- De-duplicates error messages across fields
- Prevents form submission until all requirements are met

**Exported Functions**:
- `passwordHasNumberValidator(password: string): null | string`
- `passwordHasSpecialCharacterValidator(password: string): null | string`
- `passwordHasUpperCaseValidator(password: string): null | string`
- `passwordminimumLengthValidator(password: string): null | string`
- `orchestratePasswordValidator(password: string): string[] | null` - Runs all validators

#### `showPassword.ts`
Provides toggle functionality for password field visibility.

**Features**:
- Checkbox-based toggle between password/text input types
- Supports multiple password fields per form
- Caches password field references for performance
- Works with any form containing `.show-password-toggle` checkboxes

**Implementation**: Add a checkbox with class `show-password-toggle` to any form with password fields.

#### `dynamicAddTrackForm.ts`
Dynamically changes the addTrack form based on what the user selects for 'track type'

**Features**:
- If the user sets track type to 'track':
    - 'Mix page' field of the form is hidden
- If the user sets track type to 'mix':
    - The following fields are hidden:
        - album_name
        - record_label
        - purchase_link
    - The 'Track name' field is changed to 'Mix Name'


### Music Content Management

#### `musicAppPlaylist.ts`
Defines TypeScript interfaces for playlist and track data structures.

**Interfaces**:
- `userPlaylist` - Playlist metadata including name, owner, type (tracks/mixes/samples), privacy settings, and timestamps
- `playlistTrack` - Individual track information including position, metadata, streaming link, and audit fields

**Usage**: Import these interfaces to ensure type safety when working with playlist data.

#### `validateStreamingLink.ts`
Validates streaming platform URLs and ensures platform compatibility.

**Features**:
- URL parsing and hostname extraction
- Support for multiple streaming platforms:
  - YouTube (youtube.com, youtu.be, music.youtube.com, m.youtube.com)
  - Bandcamp (bandcamp.com and all artist subdomains)
- Dropdown validation for platform selection
- Normalized domain matching (handles www. prefix)

**Exported Functions**:
- `getHostname(streamingLink: string): string | null` - Extracts hostname from URL
- `checkStreamingLinkIsValid(hostName: string | null): null | string` - Validates against supported platforms
- `orchestrateCheckStreamingLinkIsValid(streamingLink: string | null): string | null` - Main validation orchestrator
- `supportedStreamingPlatformIsSelected(formDropDown: string): string[]` - Validates platform dropdown selection
- `initValidateAddTrackForm(): void` - Initializes the track form validation

**Extensibility**: Additional platforms can be added by updating `exactDomains` or `domainPatterns` arrays.

#### `deletePlaylists.ts` 
Handles client-side deletion workflow for multiple playlists with user confirmation.

**Features**:
- Edit mode toggle that reveals deletion controls
- Checkbox-based multi-selection of playlists
- Bootstrap modal confirmation dialog before deletion
- CSRF token handling for secure DELETE requests
- Automatic page refresh after successful deletion
- Cancel functionality to exit edit mode without changes
- Graceful error handling with console logging

**Workflow**:
1. User clicks "Edit" button → Delete/Cancel buttons and checkboxes appear
2. User selects playlists via checkboxes
3. User clicks "Delete" → Confirmation modal appears
4. User confirms → DELETE request sent to Django backend
5. On success → Page refreshes, deleted playlists removed from view

**Backend Integration**:
- Sends DELETE request to URL specified in `data-delete-url` attribute
- Payload format: `{ "playlist_id": [1, 2, 3] }`
- Expects JSON response: `{ "success": true, "deleted_count": 3 }`

**HTML Requirements**:
```html
<button id="edit-playlists-btn">Edit</button>
<button id="delete-playlists-btn" class="d-none">Delete</button>
<button id="cancel-edit-btn" class="d-none">Cancel</button>

<table>
  <thead>
    <th class="checkbox-header d-none">Select</th>
  </thead>
  <tbody>
    <tr data-playlist-id="1">
      <td class="playlist-checkbox-cell d-none">
        <input type="checkbox">
      </td>
    </tr>
  </tbody>
</table>

<div id="confirmDeleteModal" class="modal">
  <button id="confirm-delete-btn" data-delete-url="/user/delete_playlists/">
    Confirm Delete
  </button>
</div>
```

**Exported Functions**:
- `init(): void` - Initializes the deletion workflow (auto-called on DOMContentLoaded)

#### `deletePlaylistTracks.ts` 
Handles client-side deletion workflow for tracks within a playlist with user confirmation.

**Features**:
- Edit mode toggle for track deletion controls
- Checkbox-based multi-selection of tracks
- Bootstrap modal confirmation dialog
- CSRF-protected DELETE requests
- Automatic page refresh on successful deletion
- Cancel functionality to revert changes
- Uses UUID-based track identifiers
- Comprehensive error handling

**Workflow**:
1. User clicks "Edit" button → Delete/Cancel buttons and checkboxes appear
2. User selects tracks via checkboxes
3. User clicks "Delete" → Confirmation modal appears
4. User confirms → DELETE request sent to Django backend
5. On success → Page refreshes, deleted tracks removed from playlist view

**Backend Integration**:
- Sends DELETE request to URL specified in `data-delete-url` attribute
- Payload format: `{ "playlist_track_id": ["uuid-1", "uuid-2"] }`
- Expects JSON response: `{ "success": true, "deleted_count": 2 }`
- Uses UUIDs instead of integer IDs (different from playlist deletion)

**HTML Requirements**:
```html
<button id="edit-playlist-tracks-btn">Edit</button>
<button id="delete-playlist-tracks-btn" class="d-none">Delete</button>
<button id="cancel-edit-btn" class="d-none">Cancel</button>

<table>
  <thead>
    <th class="checkbox-header d-none">Select</th>
  </thead>
  <tbody>
    <tr data-playlist-track-id="a1b2c3d4-e5f6-7890-abcd-ef1234567890">
      <td class="playlist-track-checkbox-cell d-none">
        <input type="checkbox">
      </td>
    </tr>
  </tbody>
</table>

<div id="confirmDeleteModal" class="modal">
  <button id="confirm-delete-btn" data-delete-url="/user/playlist/delete_tracks/">
    Confirm Delete
  </button>
</div>
```

**Exported Functions**:
- `init(): void` - Initializes the track deletion workflow (auto-called on DOMContentLoaded)

**Key Differences from deletePlaylists.ts**:
- Uses `data-playlist-track-id` instead of `data-playlist-id`
- Uses UUID strings instead of integers
- Different CSS classes for checkbox cells
- Different button IDs to avoid conflicts when both modules are loaded

## Common Patterns

### Form Integration
All validation modules follow a consistent pattern:

```typescript
document.addEventListener("DOMContentLoaded", (): void => {
    // 1. Get form and input elements
    const form = document.getElementById("auth-form") as HTMLFormElement;
    const input = document.getElementById("input-id") as HTMLInputElement;
    const errorDiv = document.getElementById("error-id") as HTMLDivElement;

    // 2. Check elements exist
    if (!form || !input || !errorDiv) {
        console.warn('Required elements not found');
        return;
    }

    // 3. Add submit event listener
    form.addEventListener("submit", (event: SubmitEvent) => {
        const error = validationFunction(input.value);
        
        if (error) {
            event.preventDefault(); // Prevent Django submission
            errorDiv.textContent = error;
        } else {
            errorDiv.textContent = "";
        }
    });
});
```

### Error Handling
- All validation functions return `null` for valid input or a user-friendly error message string
- Form submissions are prevented using `event.preventDefault()` when validation fails
- Error messages are displayed in designated error divs with IDs like `{field}-error`
- Deletion modules log errors to console for debugging

### Type Safety
- All form elements are properly typed using TypeScript generics
- Interfaces define clear contracts for data structures
- Functions have explicit return types
- Set collections used for tracking selected items (prevents duplicates)

### CSRF Protection
Deletion modules handle Django's CSRF protection:

```typescript
const csrfToken = document.cookie
    .split('; ')
    .find(row => row.startsWith('csrftoken='))
    ?.split('=')[1] ?? '';

fetch(url, {
    headers: {
        'X-CSRFToken': csrfToken
    }
});
```

## HTML Requirements

For these modules to work correctly, your Django templates must include:

1. **Form Structure** (for validation modules):
   - Form must have `id="auth-form"`
   - Input fields must have Django-standard IDs (e.g., `id_email`, `id_streaming_link`)
   - Error display divs must have IDs matching pattern `{field}-error`

2. **Password Toggle**:
   - Checkbox with class `show-password-toggle`
   - Password input fields with `type="password"`

3. **Deletion UI** (for deletePlaylists.ts):
   - Edit, Delete, and Cancel buttons with specific IDs
   - Table rows with `data-playlist-id` attributes
   - Checkbox cells with `.playlist-checkbox-cell` class
   - Bootstrap modal with `id="confirmDeleteModal"`
   - Confirm button with `data-delete-url` attribute

4. **Track Deletion UI** (for deletePlaylistTracks.ts):
   - Edit, Delete, and Cancel buttons with track-specific IDs
   - Table rows with `data-playlist-track-id` attributes (UUIDs)
   - Checkbox cells with `.playlist-track-checkbox-cell` class
   - Bootstrap modal with `id="confirmDeleteModal"`
   - Confirm button with `data-delete-url` attribute

5. **Example Structure**:
```html
<!-- Authentication Form -->
<form id="auth-form">
    <input type="email" id="id_email">
    <div id="email-error"></div>
    
    <input type="password" id="id_password">
    <div id="password-error"></div>
    
    <input type="checkbox" class="show-password-toggle">
    <button type="submit">Submit</button>
</form>

<!-- Playlist Deletion UI -->
<button id="edit-playlists-btn">Edit Playlists</button>
<button id="delete-playlists-btn" class="d-none">Delete Selected</button>
<button id="cancel-edit-btn" class="d-none">Cancel</button>

<table>
  <thead>
    <tr>
      <th class="checkbox-header d-none"></th>
      <th>Playlist Name</th>
    </tr>
  </thead>
  <tbody>
    <tr data-playlist-id="1">
      <td class="playlist-checkbox-cell d-none">
        <input type="checkbox">
      </td>
      <td>Summer Vibes</td>
    </tr>
  </tbody>
</table>

<!-- Confirmation Modal (Bootstrap) -->
<div class="modal fade" id="confirmDeleteModal">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <h5>Confirm Deletion</h5>
      </div>
      <div class="modal-body">
        Are you sure you want to delete the selected items?
      </div>
      <div class="modal-footer">
        <button type="button" data-bs-dismiss="modal">Cancel</button>
        <button type="button" id="confirm-delete-btn" 
                data-delete-url="/username/delete_playlists/">
          Delete
        </button>
      </div>
    </div>
  </div>
</div>
```

## Development Notes

### Learning Focus
This codebase emphasizes:
- TypeScript fundamentals (types, interfaces, generics)
- DOM manipulation and event handling
- Form validation patterns
- Modular code organization
- Integration with Django backend
- RESTful API interaction (DELETE requests)
- CSRF token handling
- Bootstrap modal integration
- Set collections for state management

### Future Enhancements
- Add SoundCloud and Nina Protocol support to streaming link validation
- Implement real-time validation (on blur/input events)
- Add client-side password strength meter
- Create unit tests for validation functions
- Add internationalization support for error messages
- Add loading states during DELETE requests
- Implement optimistic UI updates (remove items before server confirmation)
- Add undo functionality for deletions
- Batch operation progress indicators
- Keyboard shortcuts for deletion workflow (e.g., Ctrl+E for edit mode)

## Build & Deployment

These TypeScript files should be compiled to JavaScript and included in your Django static files. Ensure your build process:
1. Compiles TypeScript to ES6+ JavaScript
2. Bundles if necessary (or loads as ES modules)
3. Places compiled files in Django's static directory
4. Updates templates to reference compiled JavaScript files
5. Includes Bootstrap JavaScript for modal functionality (deletion modules)

### TypeScript Compilation
```bash
# Compile single file
tsc deletePlaylists.ts --target ES6

# Watch mode for development
tsc --watch

# Compile entire project
tsc --project tsconfig.json
```

## Dependencies

### Runtime Dependencies
- TypeScript 4.x or higher
- Modern browser with ES6+ support
- Django backend for form handling
- Bootstrap 5.x (for modal functionality in deletion modules)

### Development Dependencies
- TypeScript compiler
- ES6+ compatible bundler (optional)
- Type definitions: `@types/bootstrap` (if using TypeScript strict mode)

## Module Loading

### ES Module Pattern
```html
<!-- In your Django template -->
<script type="module" src="{% static 'js/deletePlaylists.js' %}"></script>
<script type="module" src="{% static 'js/deletePlaylistTracks.js' %}"></script>
```

### Conditional Loading
Load deletion modules only on pages that need them:

```html
<!-- Playlist list page -->
{% if playlists %}
  <script type="module" src="{% static 'js/deletePlaylists.js' %}"></script>
{% endif %}

<!-- Playlist detail page -->
{% if playlist_tracks %}
  <script type="module" src="{% static 'js/deletePlaylistTracks.js' %}"></script>
{% endif %}
```

## Security Considerations

### CSRF Protection
- All DELETE requests include Django CSRF token
- Token extracted from cookies and sent in `X-CSRFToken` header
- Django validates token server-side

### Input Validation
- Client-side validation is supplemented by server-side validation
- All form data sanitized before submission
- URL validation prevents malicious links

### User Confirmation
- Deletion actions require explicit confirmation via modal
- Prevents accidental data loss
- Clear visual feedback during deletion workflow

### Error Exposure
- Error details logged to console (development)
- User-friendly error messages only
- Sensitive error details not exposed to frontend

## Testing Checklist

When implementing these modules, verify:

### Validation Modules
- ✅ Form submission prevented on validation failure
- ✅ Error messages display correctly
- ✅ Valid input allows form submission
- ✅ Multiple validation errors shown simultaneously
- ✅ Error messages clear on successful validation

### Deletion Modules
- ✅ Edit mode toggles correctly
- ✅ Checkboxes appear/disappear as expected
- ✅ Modal appears on delete button click
- ✅ Cancel button resets UI state
- ✅ Selected items tracked correctly
- ✅ DELETE request sent with correct payload
- ✅ Page refreshes on successful deletion
- ✅ CSRF token included in requests
- ✅ Error handling works (network failures, etc.)
- ✅ Works with both empty and populated lists

---

**Author**: Full-stack developer focusing on TypeScript and Django integration  
**Last Updated**: March 2026