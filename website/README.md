# Porto Faifo website

An English-language type specimen and marketing site built with [KetJS View](https://ketjs.dev/docs/view-static-sites/). The home, Sans, Mono and Symbols pages render to HTML at build time. The demos, type tester and symbol catalogue hydrate as islands.

From this directory with Node 24.22.3+ (24.x) or 26.13.1+:

```sh
npm ci
npm run dev
npm run check
npm run build
npm run preview
```

The development server listens on `127.0.0.1:5173`. Preview serves the current build on `127.0.0.1:4173`. Publish the contents of `dist/` to a static host.

The build copies the repository's WOFF2 files, symbol sprite and `OFL.txt`. It reads the release version from `VERSION`, named Sans weights from `design-system.json` and symbol names from `symbols/manifest.json`. Download links point to the matching versioned GitHub release.

The dashboard demos adapt the sample orders in `specimen/index.html`. The build extracts the dashboard's icon variants from the original symbol sprites.

Canonical URLs, sharing metadata, structured data, `robots.txt` and `sitemap.xml` target `https://portofaifo.com/`. The build writes the sitemap and robots file to the root of `dist/`.

## Cloudflare Workers Builds

In **Workers & Pages → Create application**, connect `ketvietlab/porto-faifo` to a Worker with the following build settings.

| Field | Value |
| --- | --- |
| Project name | `porto-faifo` |
| Production branch | `main` |
| Root directory | `website` |
| Build command | `npm ci --ignore-scripts && npm run check && npm run build` |
| Deploy command | `npx --yes wrangler@4.168.0 deploy` |
| Enable Preview builds | Off |
| Protect with Cloudflare Access | Off |

Under **Build variables and secrets**, set `NODE_VERSION` to `26.13.1` and
`SKIP_DEPENDENCY_INSTALL` to `true`. Keep the repository-wide build watch default
so pushes that update fonts, symbols or release data also build the site.

[The Wrangler configuration](wrangler.jsonc) serves `website/dist/` as static
assets with canonical directory URLs and a `404` response for unknown paths.
After the first deployment, add `portofaifo.com` under **Settings → Domains & Routes**
as a custom domain. [Cloudflare Workers Builds configuration](https://developers.cloudflare.com/workers/ci-cd/builds/configuration/)
