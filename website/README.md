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

## Cloudflare Pages

Create a Direct Upload Pages project with production branch `main`. From a terminal authenticated with Wrangler, run:

```sh
npx --yes wrangler@4.168.0 pages project create porto-faifo --production-branch main
```

Set `CLOUDFLARE_ACCOUNT_ID` as a GitHub Actions repository variable and
`CLOUDFLARE_API_TOKEN` as a repository secret. Scope the token to the target
Cloudflare account with **Account → Cloudflare Pages → Edit**.

[Publish website](../.github/workflows/publish-website.yml) builds and uploads
`website/dist/` on relevant pushes to `main`. It can also be run manually
from the Actions tab on `main`. In the Pages project's **Custom domains**
settings, add `portofaifo.com` to match the site's canonical URLs.
