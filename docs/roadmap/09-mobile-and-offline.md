# Mobile & Offline

> Use Rulate anywhere

## Status

- **Phase**: Planning
- **Priority**: Lower
- **Last Updated**: December 2025

## Context

While the Web UI is responsive and works on mobile browsers, some users may want an installable app experience with offline capabilities. This epic explores progressive enhancement for mobile and offline use cases.

## Success Criteria

- [ ] App can be installed to home screen on mobile
- [ ] Basic functionality works offline
- [ ] Service worker caches essential resources

## Deliverables

### Progressive Web App (PWA)

**Current State**: Standard web app, requires connection.

**Goal**: Installable app with offline support.

**Tasks**:
- [ ] Create PWA manifest (`manifest.json`)
  - App name, icons, theme color
  - Display mode (standalone)
- [ ] Implement service worker
  - Cache static assets (HTML, CSS, JS)
  - Cache API responses for offline viewing
- [ ] Add install prompt handling
- [ ] Implement offline fallback page
- [ ] Add background sync for queued operations
- [ ] Test on iOS Safari and Android Chrome

**Offline capabilities**:
- View cached catalogs and rulesets
- Queue evaluation requests for when online
- Clear indication of offline status

### Mobile Companion App (Conditional)

**Current State**: No native app.

**Goal**: Native experience if PWA proves insufficient.

**Condition**: Only pursue if PWA doesn't meet user needs.

**Tasks** (if needed):
- [ ] Evaluate React Native vs Flutter
- [ ] Design mobile-optimized UI
- [ ] Implement core features (view, evaluate)
- [ ] Consider camera integration for item photos
- [ ] App store submission

**Note**: PWA approach is strongly preferred. Native app development is expensive and should only be considered if clear user demand exists.

## Dependencies

- Production Ready epic (complete) - API stability available

## Open Questions

- What data should be available offline?
- How to handle conflicts when offline edits sync?
- Is push notification support needed?

## Technical Notes

**PWA checklist**:
- HTTPS required (production deployment with reverse proxy)
- Valid manifest.json
- Service worker registered
- Lighthouse PWA audit passing

**Recommended service worker strategy**: Network-first with cache fallback for API calls, cache-first for static assets.
