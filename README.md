# AWEFonts

AWEFonts is a static, worldwide typography library and local-first font studio.

## Included

- Light-first responsive interface with optional dark mode.
- A static catalog snapshot containing 2,105 families: 1,960 Google Fonts entries and 145 Fontsource-only entries.
- Real provider-loaded previews, family specimen routes, weight controls, language/script metadata, favorites and search.
- A directory of global, independent, commercial, regional and specialist font sources.
- Local pixel glyph editor with browser-only image import, local drafts and TTF export.
- Static JSON catalog and per-family CSS endpoints.

## Static architecture

No Workers, Functions, database, login, server-side API or API keys. Catalog and CSS files are static assets. Google Fonts and Fontsource deliver their upstream font binaries. Font creation and image processing happen locally in the browser; no image or font draft is uploaded.

The catalog is a metadata index, not a mirror of every third-party archive. The external source directory links to provider collections; their catalogs, downloads and licenses remain controlled by those providers. Check each license before commercial use.

## Data snapshot

- Google Fonts public metadata snapshot: 2026-06-30
- Fontsource package registry snapshot: 2026-10-21
- Catalog file: `/api/v1/catalog.json`

## Deployment

Deploy on Cloudflare Pages with no build command and output directory `/`. Add `fonts.aweconnect.dpdns.org` and `fonts.api.aweconnect.dpdns.org` as custom domains on the same Pages project. The API hostname serves static catalog and CSS files.

## Notes

Static hosting cannot accept font uploads or publish user-created fonts. The local studio exports files directly to the user's device.
