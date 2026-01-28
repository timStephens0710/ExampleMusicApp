# Music App Frontend

## Overview

This is the frontend TypeScript workspace for a music archiving tool built with Django and TypeScript. The project provides comprehensive client-side validation, form handling, and user interface interactions for managing music playlists, tracks, and user authentication.

## Project Structure

```
music_app_frontend/
├── node_modules/          # NPM dependencies (git-ignored)
├── src/                   # TypeScript source files
│   ├── validateEmail.ts
│   ├── validatePassword.ts
│   ├── validateStreamingLink.ts
│   ├── validateAddTrackForm.ts
│   ├── showPassword.ts
│   ├── musicAppAuth.ts
│   └── musicAppPlaylist.ts
├── tests/                 # Vitest test suite
│   ├── emailValidator.test.ts
│   ├── validatePassword.test.ts
│   ├── validateStreamingLink.test.ts
│   └── validateAddTrackForm.test.ts
├── package.json           # NPM dependencies and scripts
├── package-lock.json      # Locked dependency versions
├── tsconfig.json          # TypeScript compiler configuration
├── vite.config.ts         # Vite bundler configuration
└── vitest.config.ts       # Vitest test configuration
```

## Technology Stack

### Core Technologies
- **TypeScript** - Strongly-typed JavaScript for better developer experience
- **Django** - Python web framework (backend integration)
- **Vite** - Next-generation frontend build tool
- **Vitest** - Fast unit testing framework

### Development Tools
- **Node.js** - JavaScript runtime
- **NPM** - Package manager
- **ESLint** (recommended) - Code linting
- **Prettier** (recommended) - Code formatting

## Getting Started

### Prerequisites
- Node.js 16+ 
- NPM 8+
- Python 3.8+ (for Django backend)

### Installation

1. **Install dependencies**:
```bash
npm install
```

2. **Verify installation**:
```bash
npm run test
```

### Development Workflow

1. **Start development mode** (with hot-reload):
```bash
npm run dev
```

2. **Run tests in watch mode**:
```bash
npm run test:watch
```

3. **Build for production**:
```bash
npm run build
```

4. **Type-check TypeScript**:
```bash
npm run type-check
```

## NPM Scripts

```json
{
  "dev": "vite",                    // Start dev server with HMR
  "build": "vite build",            // Build for production
  "preview": "vite preview",        // Preview production build
  "test": "vitest",                 // Run tests once
  "test:watch": "vitest --watch",   // Run tests in watch mode
  "test:coverage": "vitest --coverage", // Generate coverage report
  "type-check": "tsc --noEmit"      // Check TypeScript types
}
```

## Configuration Files

### `tsconfig.json`
TypeScript compiler configuration:
- Target: ES6+
- Module: ESNext
- Strict mode enabled
- DOM lib included for browser APIs
- Source maps enabled for debugging

### `vite.config.ts`
Vite bundler configuration:
- Build output directory
- Public path configuration
- Asset handling
- Development server settings
- Integration with Django static files

### `vitest.config.ts`
Test framework configuration:
- Test environment (jsdom for DOM testing)
- Coverage settings
- Test file patterns
- Setup files
- Mock configurations

### `package.json`
Project metadata and dependencies:
- Project name and version
- NPM scripts
- Dependencies and devDependencies
- Node engine requirements

## Source Code (`src/`)

The source directory contains all TypeScript modules for client-side validation and user interactions. Each module is focused on a specific concern:

### Validation Modules
- **validateEmail.ts** - Email format validation
- **validatePassword.ts** - Password strength validation (8+ chars, numbers, special chars, uppercase)
- **validateStreamingLink.ts** - URL validation for YouTube and Bandcamp
- **validateAddTrackForm.ts** - Form text validation (null checks, length limits)

### UI Modules
- **showPassword.ts** - Toggle password visibility
- **dynamicAddTrackForm.ts** - Dynamically change addTrack form depending on track type

### Type Definitions
- **musicAppAuth.ts** - Authentication form interfaces
- **musicAppPlaylist.ts** - Playlist and track interfaces

**For detailed documentation**, see `src/README.md`

## Tests (`tests/`)

Comprehensive test suite using Vitest covering:
- Unit tests for all validation functions
- DOM integration tests for form handling
- Edge case testing
- ~95% code coverage

**For detailed documentation**, see `tests/README.md`

## Integration with Django

### Build Process
1. TypeScript files are compiled to JavaScript
2. Vite bundles and optimizes the output
3. Built files are placed in Django's `static/` directory
4. Django serves the compiled JavaScript to the frontend

### Django Template Integration

**HTML Structure Required**:
```html
<!-- Django template -->
<form id="auth-form" method="post">
    {% csrf_token %}
    
    <!-- Email field -->
    {{ form.email }}
    <div id="email-error" class="error-message"></div>
    
    <!-- Password field -->
    {{ form.password }}
    <div id="password-error" class="error-message"></div>
    
    <!-- Show password toggle -->
    <label>
        <input type="checkbox" class="show-password-toggle">
        Show password
    </label>
    
    <button type="submit">Submit</button>
</form>

<!-- Load compiled JavaScript -->
<script type="module" src="{% static 'js/bundle.js' %}"></script>
```

### Form Validation Flow
1. User fills out Django form
2. User clicks submit
3. TypeScript validators run client-side
4. If validation fails:
   - `event.preventDefault()` stops form submission
   - Error messages display in designated divs
5. If validation passes:
   - Form submits to Django backend
   - Django performs server-side validation
   - Database operations proceed

## Development Guidelines

### Adding New Validation

1. **Create validator function** in `src/`:
```typescript
export function validateField(value: string): null | string {
    if (/* validation logic */) {
        return null; // Valid
    }
    return "Error message"; // Invalid
}
```

2. **Add DOM integration**:
```typescript
document.addEventListener("DOMContentLoaded", (): void => {
    const form = document.getElementById("auth-form") as HTMLFormElement;
    const input = document.getElementById("id_field") as HTMLInputElement;
    const errorDiv = document.getElementById("field-error") as HTMLDivElement;

    form.addEventListener("submit", (event: SubmitEvent) => {
        const error = validateField(input.value);
        if (error) {
            event.preventDefault();
            errorDiv.textContent = error;
        } else {
            errorDiv.textContent = "";
        }
    });
});
```

3. **Write tests** in `tests/`:
```typescript
describe('validateField', () => {
    it('returns null for valid input', () => {
        expect(validateField('valid')).toBeNull();
    });

    it('returns error for invalid input', () => {
        expect(validateField('invalid')).toBe('Error message');
    });
});
```

4. **Update documentation** in relevant README files

### Code Style

- Use TypeScript strict mode
- Explicit return types on functions
- Descriptive variable names (balance between clarity and brevity)
- Comment complex logic
- Export functions that may be reused
- Keep functions small and focused (single responsibility)

### Testing Standards

- Write tests before or alongside implementation (TDD)
- Test happy path, sad path, and edge cases
- One assertion focus per test (generally)
- Use descriptive test names
- Mock DOM elements for integration tests
- Aim for >80% code coverage

## Dependencies

### Production Dependencies
Currently no runtime dependencies - vanilla TypeScript with browser APIs

### Development Dependencies
- **typescript** - TypeScript compiler
- **vite** - Build tool and dev server
- **vitest** - Testing framework
- **@vitest/ui** - Visual test runner
- **jsdom** - DOM implementation for testing

## Building for Production

### Development Build
```bash
npm run build
```

### Production Optimization
Vite automatically handles:
- Minification
- Tree-shaking
- Code splitting
- Asset optimization
- Source map generation

### Output
Built files are placed in `dist/` (or Django `static/` directory based on configuration)

## Troubleshooting

### Common Issues

**TypeScript errors in IDE**:
```bash
# Restart TypeScript server
npm run type-check
```

**Tests failing**:
```bash
# Clear cache and re-run
npm test -- --no-cache
```

**Build errors**:
```bash
# Clean install
rm -rf node_modules package-lock.json
npm install
```

**Module not found**:
- Check import paths are correct
- Verify file exists in `src/`
- Ensure no circular dependencies

## Future Enhancements

### Planned Features
- [ ] Add SoundCloud and Nina Protocol support
- [ ] Real-time validation (on blur/input events)
- [ ] Password strength meter visualization
- [ ] Internationalization (i18n) for error messages
- [ ] Accessibility improvements (ARIA labels, screen reader support)

### Technical Improvements
- [ ] Add ESLint and Prettier
- [ ] Set up GitHub Actions CI/CD
- [ ] Add E2E tests with Playwright
- [ ] Implement bundle size analysis
- [ ] Add performance monitoring
- [ ] Create Storybook component documentation

## Contributing

### Development Process
1. Create feature branch from `main`
2. Write tests for new functionality
3. Implement feature
4. Ensure all tests pass: `npm test`
5. Type-check: `npm run type-check`
6. Build successfully: `npm run build`
7. Update relevant documentation
8. Submit pull request

### Commit Message Format
```
type(scope): subject

body (optional)

footer (optional)
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## Project Goals

This frontend workspace serves as a learning project focused on:
1. **TypeScript Fundamentals** - Types, interfaces, generics, strict mode
2. **DOM Manipulation** - Event listeners, form handling, dynamic content
3. **Testing** - Unit tests, integration tests, TDD practices
4. **Build Tools** - Modern bundling with Vite
5. **Django Integration** - Seamless backend/frontend communication

## License

[Your License Here]

## Contact

[Your Contact Information]

---

**Project Type**: Learning project / Portfolio piece  
**Status**: Active development  
**Last Updated**: January 2026  
**Node Version**: 16+  
**TypeScript Version**: 4.x+