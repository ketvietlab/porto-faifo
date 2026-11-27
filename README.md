# Porto Faifo

Typefaces and symbols by [Két Việt](https://ketviet.vn) for user interfaces, with full Vietnamese support.

**[Download the latest release](https://github.com/ketvietlab/porto-faifo/releases/latest)**

![Porto Faifo Sans and Porto Faifo Mono](docs/fonts.svg)

| Family | Contents | Download |
| --- | --- | --- |
| **Porto Faifo Sans** | Light 300, Regular 400, Medium 500, SemiBold 600, Bold 700, ExtraBold 800, Black 900; an optical-size (`opsz`) font per weight; a variable font (`wght` 300–900, `opsz` 8–72) | `PFSans-<version>.zip` |
| **Porto Faifo Mono** | Regular 400, Medium 500; every glyph 0.576 em wide | `PFMono-<version>.zip` |
| **Porto Faifo Symbols** | 322 SVG symbols (449 drawings with the filled variants), 14, 16, 20 and 24 px, four weights | `PFSymbols-<version>.zip` |

Both type families cover Google Fonts Latin Core, Latin Plus, Vietnamese and ₫.

## Installing the fonts

Unzip, then install the files in `OTF/` (macOS) or `TTF/` (Windows and Linux, hinted).
`Variable/` holds one font covering all weights. Install either the static or the variable fonts.

## On the web

```css
@font-face {
  font-family: "Porto Faifo Sans";
  src: url("PortoFaifoSans[opsz,wght].woff2") format("woff2");
  font-weight: 300 900;
  font-display: swap;
}
body { font-family: "Porto Faifo Sans", system-ui, sans-serif; font-optical-sizing: auto; }
```

SemiBold 600 is interpolated between Medium and Bold. ExtraBold 800 is interpolated between Bold and Black. Both weights are available as static faces and variable font instances.

## Interactive specimen

Generate the outline data from the built fonts, then serve the repository locally.

```sh
.venv/bin/python scripts/specimen_data.py
python3 -m http.server 8000 --bind 127.0.0.1
```

Open `http://127.0.0.1:8000/specimen/` to inspect outlines and compare all seven weights.

## Google Fonts export

Build Sans and Mono with `sh sources/build.sh`, then run `.venv/bin/python scripts/export_google_fonts.py`.
The export stages `fonts/variable/PortoFaifoSans[opsz,wght].ttf` and the two
`PortoFaifoMono-*.ttf` files from `fonts/mono/ttf/` under
`build/googlefonts/ofl/`. Run `fontspector -p googlefonts` with the TTF files and
`OFL.txt` from each family directory.

For catalog QA, run `gftools add-font` on each staged family and include the
generated `METADATA.pb` in the Fontspector inputs. The Sans metadata needs an
`opsz` registry default override of `16` to match the binary. Classify Mono
as `MONOSPACE`. The catalog entry should reference the upstream commit that
contains the staged files.

The Sans default figures are proportional. Enable `font-variant-numeric: tabular-nums`
for equal-width figures in tables.

## Symbols

![A selection of Porto Faifo Symbols](docs/symbols.svg)

- Single files: `svg/<size>/<weight>/<name>.svg`; filled variants end in `-fill`.
- Sprites: `sprites/pf-symbols-<size>-<weight>.svg`, ids `pf-<name>`.
- `manifest.json`: names, aliases, groups, meanings, matching Lucide and freedesktop names.
- `preview.html`: every symbol on one page.

Each size is drawn with its own stroke, so use the matching size instead of scaling. Symbols follow
`currentColor` when the SVG is part of the page:

```html
<svg width="20" height="20" aria-hidden="true">
  <use href="pf-symbols-20-regular.svg#pf-search"></use>
</svg>
```

Lucide and freedesktop names are cross-references only; no Lucide geometry is used.

## Building from source

Python 3.11 is required. Library versions are pinned in `requirements.txt`.

```sh
python3.11 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/release.py
```

The last command builds the fonts and symbols, runs the checks and writes the packages to `build/dist/`.

| Path | Contents |
| --- | --- |
| `design-system.json` | Parameters of both type families |
| `symbols/symbol-system.json` | Parameters of the symbols; strokes come from the fonts |
| `scripts/pfsans/`, `scripts/pfsymbols/` | Glyph and symbol drawing code |
| `sources/` | UFO3, generated from the parameters and the drawing code (do not edit by hand) |
| `fonts/`, `symbols/svg/`, `symbols/sprites/` | Build output |

## Releasing

1. Set `VERSION`, `meta.version` and `mono.version` in `design-system.json`
   (1.2.0 is written `1.200`), and `meta.version` in `symbols/symbol-system.json`.
2. Add a `## <version>` section to `CHANGELOG.md`.
3. Run `scripts/release.py`, commit the build output and push `main`.
4. Run `scripts/release.py --publish`: it rebuilds, checks, tags `v<version>` and creates the
   GitHub release with the packages and `SHA256SUMS.txt`.

## Licence

[SIL Open Font License 1.1](OFL.txt), for the fonts, the symbols and the source code in this repository.
