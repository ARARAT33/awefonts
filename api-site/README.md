# AWEFonts static API deployment

This directory is the **Cloudflare Pages deployment root** for the API project
`awefonts-api`. Keep every public API asset needed at runtime inside this tree.

## Endpoints

- `/v1/catalog.json` — font family catalog.
- `/v1/languages.json` — language and script profiles.
- `/v1/css-index.json` — the curated list of committed CSS presets.
- `/api/css/{font-id}.css` — AWEFonts-origin CSS preset files.
- `/v1/embed.v6.js` — API-origin embed loader.

The canonical CSS preset sources live in the repository at `api/css/`. The
matching files under `api-site/api/css/` are deployment copies. The offline
validator checks that every indexed preset exists in both locations and that
the contents match exactly.

The preset index is curated; it is not the full 2,204-family catalog. Each CSS
preset may import its font binary stylesheet from its upstream provider. The
CSS file itself is served from the AWEFonts API origin.

## Deployment

Cloudflare Pages publishes this directory. Do not rely on files outside
`api-site/` being available to the deployed API. Keep the root redirect
`/` to `/v1/catalog.json`; API routes must resolve to actual files rather
than the fallback HTML page.
