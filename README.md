# AWEFonts

AWEFonts is a static font discovery and local font-authoring experience.

## Pages
- /fonts/ — searchable catalog. It merges the bundled catalog with the public Fontsource registry/API in the visitor's browser. Google Fonts and Fontsource assets are requested directly from their providers.
- /fontsstudio/ — local glyph designer. Draw glyphs, import raster/SVG images or AWE glyph projects, and export TTF, OTF, WOFF and WOFF2 in-browser.
- /api/v1/fonts.json — bundled curated catalog.
- /api/v1/providers.json — provider registry.
- /api/v1/openapi.json — static API description.
- /api/css/{family}.css — pre-generated static CSS for bundled families.

## Architecture constraints
- Static HTML, CSS, JavaScript and JSON only.
- No Cloudflare Workers, Pages Functions, server, database, authentication, scheduled jobs or upload endpoints.
- No server-side processing. FontStudio drawing, tracing, project save and font compilation run on the visitor's device.
- Catalog discovery uses public upstream sources directly from the browser. If an upstream provider is unavailable or blocks CORS, the bundled catalog remains available.
- The full font binaries are not mirrored by this project. Google Fonts and Fontsource deliver their own files. Each font's license must be checked individually.

## Deploy
Cloudflare Pages: no build command; output directory /. The API subdomain can point to the same Pages project. Do not add Workers or Functions.

## FontStudio formats
The studio uses the browser build of fontsketch to generate TTF, OTF, WOFF and WOFF2 locally. The AWE glyph project is portable JSON with the .awfglyph extension. Imported images are rasterized and threshold-traced locally; for accurate results, use a clean high-contrast glyph scan.

## Important
The public catalog is broad but depends on upstream provider registries; it does not imply every font on the internet is included. Provider catalogs can change, and each family may have its own redistribution and commercial-use terms.
