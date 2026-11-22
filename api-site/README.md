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
<script src="https://fonts.api.aweconnect.dpdns.org/v1/embed.v6.js" data-font="Inter" data-weights="400;700"></script>
<style>body { font-family: "Inter", sans-serif; }</style>
```

Multiple fonts are supported with comma-separated family names:
```html
<script src="https://fonts.api.aweconnect.dpdns.org/v1/embed.v6.js" data-font="Inter, Noto Sans Armenian"></script>
```

To apply the first font automatically:
```html
<script src="https://fonts.api.aweconnect.dpdns.org/v1/embed.v6.js" data-font="Inter" data-apply="true" data-selector=".article"></script>
```

`data-font` accepts a catalog family name or family id. Every catalog family has a static CSS endpoint under `/v1/css/{font_id}.css` on the API hostname. The CSS endpoint is served by AWEFonts; licensed font binaries are still fetched from their upstream provider (Google Fonts, Fontsource or SIL). This keeps embed code and stylesheet URLs on the API hostname, but is not yet a binary mirror.

## Endpoints
- `/v1/catalog.json` — full catalog metadata
- `/v1/embed.v6.js` — browser-side embed loader
- `/v1/health.json` — static API build/version information

All API files are static. There are no Workers, Functions, server-side code, database, login or API keys. The loader fetches the catalog and API-hosted CSS endpoints in the visitor's browser. CSS then fetches font binaries from the licensed upstream provider.