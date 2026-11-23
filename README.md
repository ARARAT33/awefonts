# AWEFonts

AWEFonts is a static-first worldwide typography library and local font studio. Browse real font families, preview scripts, compare typefaces, download permitted font files, and create custom fonts locally in the browser.

## Library

**2,235 indexed families** across five catalog sources:

| Source | Families |
|---|---:|
| Google Fonts | 1,960 |
| Fontsource-only packages | 137 |
| SIL International | 63 |
| Additional Fontshare families | 67 |
| Google Material Icons / Symbols | 8 |

The 67 additional Fontshare records are deduplicated against the existing catalog. Fontshare licensing is preserved: 64 ITF Free Font License records are preview/embed-only; 3 additional SIL OFL records can be packaged locally. Always check the upstream licence before redistribution or commercial use.

Bunny Fonts is offered as a privacy-focused, Google Fonts-compatible alternative delivery provider for the 1,960 Google families. It does not add duplicate family records.

## Features

- Search across family names, designers, tags, categories, scripts and licences.
- Filter by source, writing system, category and variable-font availability.
- Sort by name, recent update, popularity metadata or variable-font status.
- Real font previews, script-aware specimens and local saved favourites.
- Compare up to four families side by side.
- Material Symbols variable axes: optical size, weight, fill and grade.
- Language packs and browser-local ZIP assembly for files permitted by their licences.
- Font Studio: local drawing/import workflow and local exports. User artwork is not uploaded.
- Static API and embed loader; no account, API key, database, Worker or Functions.

## Pages

- `/` — home
- `/fonts.html` — font discovery
- `/font.html?id=family-id` — specimen and family details
- `/compare.html` — side-by-side comparison
- `/packs.html` — language packs
- `/studio.html` — local font studio
- `/sources.html` — source directory
- `/developers.html` — API and embed documentation

## Static API

The root Pages project serves the API from `/v1/` so the UI and catalog are updated together in one deployment:

- `/v1/catalog.json`
- `/v1/sources.json`
- `/v1/health.json`
- `/v1/embed.v5.js`
- `/v1/openapi.json`

The API custom hostname is `fonts.api.aweconnect.dpdns.org`. The same project also serves the main website at `fonts.aweconnect.dpdns.org`. The legacy `api-site/` directory remains as a synchronized source mirror and rollback reference.

Example:

```html
<script src="https://fonts.api.aweconnect.dpdns.org/v1/embed.v5.js" data-font="Inter" data-weights="400;700"></script>
```

For supported Google families, add `data-provider="bunny"` to use the Bunny Fonts privacy CDN.

## Cloudflare Pages

- Root directory: `/`
- Build command: empty (static assets only)
- Build output directory: `/`
- No Workers or Functions.
- Automatic Git deployments remain disabled; the release is initiated manually once.
