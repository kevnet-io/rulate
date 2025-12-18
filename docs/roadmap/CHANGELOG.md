# Changelog

All notable completed work for Rulate.

## December 2025

### Comprehensive Test Suite

**Impact**: High confidence in system reliability

- 480 backend tests (94% coverage) across all core modules
- 671 frontend tests (100% production code coverage)
- 72 E2E tests with Playwright across 3 browsers (Chromium, Firefox, WebKit)
- **Total: 1,151+ tests** ensuring system reliability

### Import/Export Functionality

**Impact**: Bulk data backup and migration

- 14 API endpoints for data import/export
- Web UI page for bulk operations
- JSON format support with validation
- Automatic dependency handling for imports

### UX Polish

**Impact**: Replaced all browser dialogs with accessible custom components

- **Toast notifications** - Custom system with 4 types (success, error, warning, info), auto-dismiss, stacking
- **Modal dialogs** - Accessible modals with focus trap, keyboard nav, contextual confirmations
- **Loading states** - Spinner component and skeleton loaders on all list pages
- **Empty states** - Helpful empty states with icons and CTAs on all list pages
- **Tooltips** - Reusable tooltip component for inline help
- **Form validation** - FormField component and comprehensive validation utilities
- **Unsaved changes** - Warning before navigation with unsaved form data
- **Enhanced rule editor** - Operator documentation sidebar, search, templates (18 presets)
- **Operator registry** - 17 operators fully documented with examples and parameters

Zero browser `alert()` or `confirm()` calls remaining. WCAG 2.1 AA compliant.

See [UX_POLISH_SUMMARY.md](../UX_POLISH_SUMMARY.md) for full details.

### Developer Experience Infrastructure

**Impact**: Automated quality gates and contributor onboarding

- **GitHub Actions CI/CD** - Automated testing with Python 3.14, frontend unit tests, E2E tests (9 parallel jobs)
- **Pre-commit hooks** - Black, Ruff, Mypy, Prettier, ESLint with auto-fix
- **GitHub templates** - Bug reports, feature requests, and PR templates
- **CONTRIBUTING.md** - Comprehensive contributor guide with setup, workflow, and coding standards
- **Dependabot** - Automated weekly dependency updates for Python, npm, and GitHub Actions
- **VS Code integration** - Shared settings and 15+ recommended extensions
- **EditorConfig** - Consistent formatting across all editors
- **Code of Conduct** - Contributor Covenant 2.0 for open source collaboration
- **Build badges** - Test status and version badges in README
