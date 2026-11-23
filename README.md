AWEFonts static multi-page worldwide typography library and local font studio.

Pages: home, fonts.html, font.html?id=family-id, packs.html, studio.html, sources.html, compare.html, developers.html.

Catalog: 2243 indexed families: 1,960 Google Fonts, 145 Fontsource-only packages, 63 SIL families, 67 additional Fontshare families and 8 Google Material icon families. Bunny Fonts is an alternative privacy-focused CDN for Google families.ng Google Fonts / Fontsource / SIL families plus 67 additional Fontshare families (100 total Fontshare records; 33 were already represented). Fontshare licensing is preserved: SIL OFL entries can be packaged locally; ITF FFL entries are preview/embed-only and link to the official foundry page. SIL entries include OFL/license metadata and direct font file references.

Language packs fetch provider stylesheets and font binaries in the browser and create ZIP files locally. SIL packs include TTF/WOFF2 files where available. No Workers, Functions, backend, database, login or API keys. The studio imports images and exports TTF locally. Check original licenses before commercial use. Android does not universally install fonts system-wide from ZIP files.

Cloudflare Pages build command is empty. Automatic deployments are disabled in the connected Pages projects (production disabled; preview setting `none`). Do not trigger manual deployments for this preview branch.


## Static API routes
Deploy `api-site/` as a second Cloudflare Pages project (root directory `api-site`, no build command, output directory `.`) and attach `fonts.api.aweconnect.dpdns.org`. Keep the main UI Pages project rooted at repository root for `fonts.aweconnect.dpdns.org`. API documentation and embed example are in `api-site/README.md`.

The main Pages project serves both the website and `/v1/*` static API routes. The `fonts.api.aweconnect.dpdns.org` custom domain is attached to the same Pages project so one deployment updates both UI and API. Build command remains empty; no Workers or Functions are required.


## Global source directory and multilingual studio
The source directory indexes every platform supplied in the project brief. Only fonts with redistribution rights are mirrored in the downloadable catalogue; commercial and mixed archives remain linked and are not scraped or republished without permission. The library preview uses script-specific specimen strings and explicit font loading. The local studio offers glyph grids for 30+ writing systems and generates self-contained CSS `@font-face` embeds using a data URL from a locally exported TTF. Complex-script shaping (ligatures, contextual forms and mark positioning) requires a full OpenType shaping editor; this pixel-grid tool is a local glyph prototyping studio.

Fontshare source integration adds 67 additional families with source-native CSS delivery, designer/style metadata, and license-aware download controls.

API v5 options: `data-font`, `data-weights`, `data-selector`, `data-apply`, `data-size`, `data-line-height`, `data-letter-spacing`.
