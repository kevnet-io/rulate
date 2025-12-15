# Rulate Web UI

Modern web interface for the Rulate compatibility engine, built with SvelteKit and Tailwind CSS.

## Features

- **Dashboard**: Overview of all schemas, rulesets, and catalogs with quick stats
- **Schema Manager**: View and manage dimension definitions
- **RuleSet Manager**: View compatibility rules with detailed conditions
- **Catalog Manager**: Browse items and their attributes
- **Compatibility Matrix**: Visual grid showing all pairwise compatibility evaluations

## Tech Stack

- **SvelteKit 2.0**: Modern Svelte framework with SSR and routing
- **Tailwind CSS**: Utility-first CSS framework
- **TypeScript**: Type-safe development
- **Shadcn-style Components**: Beautiful, accessible UI components

## Development

```bash
# Install dependencies
npm install

# Start dev server (port 5173)
npm run dev
```

## Production Build

```bash
npm run build  # Builds to web/build/ directory
```

The production build is served by the FastAPI backend at the project root.
Run `make serve-production` from the project root to test locally.

## Testing

```bash
# Run all unit tests
npm test

# Run tests with coverage report
npm run test:coverage

# Run E2E tests
npm run test:e2e

# Run E2E tests with UI
npm run test:e2e:ui

# Run E2E tests in debug mode
npm run test:e2e:debug
```

**Test Coverage**: 671 tests with 100% coverage on production TypeScript code

- **Unit Tests**: 22 test files covering API client, components, pages, and form logic
- **E2E Tests**: 72 tests across 3 browsers validating critical user workflows
- **Test Infrastructure**: Vitest 4.0, Playwright for E2E, happy-dom environment for Svelte 5

## Project Structure

```
web/
├── src/
│   ├── routes/               # SvelteKit routes
│   │   ├── +layout.svelte    # Main layout with navigation
│   │   ├── +page.svelte      # Dashboard
│   │   ├── schemas/          # Schema pages
│   │   ├── rulesets/         # RuleSet pages
│   │   ├── catalogs/         # Catalog and item pages
│   │   └── matrix/           # Compatibility matrix
│   ├── lib/
│   │   ├── api/
│   │   │   └── client.ts     # API client with TypeScript types
│   │   ├── components/
│   │   │   ├── Navigation.svelte
│   │   │   └── ui/           # Reusable UI components
│   │   └── utils.ts          # Utility functions
│   ├── app.html              # HTML template
│   └── app.css               # Global styles and Tailwind
├── static/                   # Static assets
├── package.json
├── tailwind.config.js
├── vite.config.ts
└── svelte.config.js
```

## API Integration

**Development**: Vite proxy forwards `/api/*` requests to `http://localhost:8000`

**Production**: API client uses relative URLs (`/api/v1`) for same-origin requests

The API base URL is automatically selected based on environment:
- `import.meta.env.DEV` → absolute URL for proxy
- Production build → relative URL for same-origin

Ensure the API server is running during development:
```bash
# From project root
make dev-backend
```

## Features by Page

### Dashboard (/)

- Overview cards for schemas, rulesets, and catalogs
- Quick stats and recent items
- Quick action links

### Schemas (/schemas)

- List all schemas with dimension counts
- View schema details with full dimension specifications
- Delete schemas

### RuleSets (/rulesets)

- List all rulesets with rule counts
- View ruleset details with formatted conditions
- See exclusion vs requirement rules
- Delete rulesets

### Catalogs (/catalogs)

- List all catalogs
- View catalog items with attributes
- Browse item details
- Delete catalogs and items

### Matrix (/matrix)

- Select catalog and ruleset
- Generate compatibility matrix
- Visual grid with color coding (green=compatible, red=incompatible)
- Click cells to see detailed rule evaluations
- View pass/fail reasons for each rule

## Styling

The UI uses a custom color system based on CSS variables defined in `app.css`:

- Primary: Blue accent color
- Secondary: Gray accent
- Destructive: Red for errors/warnings
- Muted: Subtle backgrounds and text

All components support dark mode (though not yet implemented in the UI).

## Browser Support

- Modern browsers with ES6+ support
- Chrome, Firefox, Safari, Edge (latest versions)

## Contributing

When adding new pages:

1. Create route in `src/routes/`
2. Add navigation link in `Navigation.svelte`
3. Use existing UI components from `src/lib/components/ui/`
4. Follow TypeScript types from `src/lib/api/client.ts`
