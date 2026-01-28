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

### Type Safety
- All form elements are properly typed using TypeScript generics
- Interfaces define clear contracts for data structures
- Functions have explicit return types

## HTML Requirements

For these modules to work correctly, your Django templates must include:

1. **Form Structure**:
   - Form must have `id="auth-form"`
   - Input fields must have Django-standard IDs (e.g., `id_email`, `id_streaming_link`)
   - Error display divs must have IDs matching pattern `{field}-error`

2. **Password Toggle**:
   - Checkbox with class `show-password-toggle`
   - Password input fields with `type="password"`

3. **Example Structure**:
```html
<form id="auth-form">
    <input type="email" id="id_email">
    <div id="email-error"></div>
    
    <input type="password" id="id_password">
    <div id="password-error"></div>
    
    <input type="checkbox" class="show-password-toggle">
    <button type="submit">Submit</button>
</form>
```

## Development Notes

### Learning Focus
This codebase emphasizes:
- TypeScript fundamentals (types, interfaces, generics)
- DOM manipulation and event handling
- Form validation patterns
- Modular code organization
- Integration with Django backend

### Future Enhancements
- Add SoundCloud and Nina Protocol support to streaming link validation
- Implement real-time validation (on blur/input events)
- Add client-side password strength meter
- Create unit tests for validation functions
- Add internationalization support for error messages

## Build & Deployment

These TypeScript files should be compiled to JavaScript and included in your Django static files. Ensure your build process:
1. Compiles TypeScript to ES6+ JavaScript
2. Bundles if necessary (or loads as ES modules)
3. Places compiled files in Django's static directory
4. Updates templates to reference compiled JavaScript files

## Dependencies

- TypeScript 4.x or higher
- Modern browser with ES6+ support
- Django backend for form handling

---

**Author**: Full-stack developer focusing on TypeScript and Django integration  
**Last Updated**: January 2026