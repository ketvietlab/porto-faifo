# Porto Faifo website

An English-language type specimen and marketing site built with [KetJS View](https://ketjs.dev/docs/view-static-sites/). The home, Sans, Mono and Symbols pages render to HTML at build time. The type tester and symbol catalogue hydrate as islands.

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
