# Static API and embed contract

AWEFonts remains static-first: no Workers, Pages Functions, server-side routes, database or build command. Static hosting cannot dynamically proxy arbitrary third-party binaries or generate font files at request time.

API origin: `https://fonts.api.aweconnect.dpdns.org`.

- `/v1/catalog.json` — font family catalog.
- `/v1/languages.json` — language/script profiles.
- `/v1/assets-index.json` and `/v1/assets/*.json` — sharded provider resource index.
- `/v1/sources.json` — source and licence notes.
- `/v1/health.json` — inventory metadata.
- `/v1/css-index.json` — committed AWEFonts CSS presets.
- `/v1/embed.v6.js` — API-origin embed loader.

The CSS preset list is a curated subset, not the entire family catalog. The loader reports unsupported families through `awefonts:missing`; it does not silently load a third-party CSS origin. AWEFonts-hosted CSS may itself import an upstream CDN, which is not the same as a locally mirrored font binary.

Example:
```html
<script src="https://fonts.api.aweconnect.dpdns.org/v1/embed.v6.js"
 data-font="roboto,noto-sans-armenian" data-apply="true"
 data-selector=".article" data-size="18px" data-line-height="1.6"></script>
```

Supported attributes: `data-font`, `data-selector`, `data-apply`, `data-size`, `data-line-height`, `data-letter-spacing`. Events: `awefonts:ready`, `awefonts:missing`, `awefonts:error`.
