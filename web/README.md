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

# Start dev server (default port 3000)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

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

The web UI communicates with the Rulate REST API running on port 8000. The Vite dev server includes a proxy configuration to forward `/api` requests to `http://localhost:8000`.

Ensure the API server is running:

```bash
# From project root
uv run uvicorn api.main:app --reload --port 8000
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
