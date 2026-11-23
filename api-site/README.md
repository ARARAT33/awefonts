# AWEFonts static API

The API is served by the same Cloudflare Pages project as the AWEFonts UI. Static API assets are mirrored under the repository root at `/v1/` so one deployment updates the interface and catalog together. The legacy `api-site/` directory is retained as a source mirror and rollback reference, not as a separate required deployment.

Endpoints: `/v1/catalog.json`, `/v1/sources.json`, `/v1/health.json`, `/v1/embed.v5.js`, `/v1/openapi.json`.

Embed:
```html
<script src="https://fonts.api.aweconnect.dpdns.org/v1/embed.v5.js" data-font="Inter" data-weights="400;700"></script>
```

For Google families, `data-provider="bunny"` selects the Bunny Fonts privacy CDN when the family is available there. Fontshare ITF FFL records remain preview/embed-only; downloadable packages are restricted by the recorded licence.
