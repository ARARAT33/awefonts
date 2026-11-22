# AWEFonts API-only static site

This directory is deployed as a **separate Cloudflare Pages project** for `https://fonts.api.aweconnect.dpdns.org`. It contains no website UI.

## Cloudflare Pages setup
- Create a second Pages project connected to this same GitHub repository.
- Production branch: `feat/full-font-library-static-multipage-packs`.
- Root directory: `api-site`.
- Build command: leave empty.
- Build output directory: `.`.
- Attach custom domain: `fonts.api.aweconnect.dpdns.org`.
- Keep the main AWEFonts Pages project rooted at repository root and attach `fonts.aweconnect.dpdns.org`.

The API hostname must point to this separate Pages project, not the main UI project.

## Embed a font
```html
<script src="https://fonts.api.aweconnect.dpdns.org/v1/embed.v3.js" data-font="Inter" data-weights="400;700"></script>
<style>body { font-family: "Inter", sans-serif; }</style>
```

Multiple fonts are supported with comma-separated family names:
```html
<script src="https://fonts.api.aweconnect.dpdns.org/v1/embed.v3.js" data-font="Inter, Noto Sans Armenian"></script>
```

To apply the first font automatically:
```html
<script src="https://fonts.api.aweconnect.dpdns.org/v1/embed.v3.js" data-font="Inter" data-apply="true" data-selector=".article"></script>
```

`data-font` accepts a catalog family name or family id. Google Fonts are loaded from Google Fonts, Fontsource families from Fontsource, and SIL families from their published WOFF2 files. Font binaries are not proxied or mirrored by AWEFonts.

## Endpoints
- `/v1/catalog.json` — full catalog metadata
- `/v1/embed.v3.js` — browser-side embed loader
- `/v1/health.json` — static API build/version information

All API files are static. There are no Workers, Functions, server-side code, database, login or API keys. The loader fetches the catalog in the visitor's browser and adds the upstream font stylesheet.