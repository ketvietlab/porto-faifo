import { each, html } from '@ketvietlab/ketjs-view'
import { definePage, island } from '@ketvietlab/ketjs-view-tools'
import { sansWeights, sizes, symbolData, symbolWeights } from './asset-data.ts'
import dashboard from './islands/dashboard.ts'
import monoDemo from './islands/mono-demo.ts'
import specimen from './islands/specimen.ts'
import symbols from './islands/symbols.ts'
import { archive, footer, header, pageHead } from './layout.ts'
import { productionLinks } from './production-links.ts'
import { routes } from './site.ts'
import type { CollectionPart } from './site.ts'
import { symbol } from './symbol.ts'

const base = '../'
const monoGlyphs = [...'il1O0WHội An']
const products = {
  sans: {
    name: 'Sans',
    label: 'Proportional typeface',
    archive: 'PFSans',
    title: 'Porto Faifo Sans | Vietnamese Variable Font',
    metaDescription: 'Try Porto Faifo Sans, a free Vietnamese variable font for digital interfaces and reading. Compare seven weights, optical sizes and tabular figures.',
    description: `A variable typeface for digital interfaces and longer reading, with ${sansWeights.length} named weights, full Vietnamese support and optical sizes for small text and display.`,
    demoTitle: 'Sans at work.',
    demoDescription: 'Change the text weight or switch between tabular and proportional figures in the same sales dashboard.',
    facts: [
      ['Weight', '300–900'],
      ['Optical size', '8–72'],
      ['Coverage', 'Latin + Vietnamese'],
    ],
    preview: html`<span class="detail-glyph" lang="vi">Aa<span>Ắ</span></span>`,
  },
  mono: {
    name: 'Mono',
    label: 'Fixed-width typeface',
    archive: 'PFMono',
    title: 'Porto Faifo Mono | Vietnamese Monospace Font',
    metaDescription: 'Try Porto Faifo Mono, a free Vietnamese monospace font for code, logs and tables. Compare fixed-width letters and figures in a live order report.',
    description: 'A fixed-width companion for code and tabular data. Vietnamese letters, digits and spaces sit on the same grid.',
    demoTitle: 'Columns that line up.',
    demoDescription: 'Switch this plain-text order report between Mono and Sans to see what fixed-width characters do for columns.',
    facts: [
      ['Weights', '400 & 500'],
      ['Advance', '0.576 em'],
      ['Coverage', 'Latin + Vietnamese'],
    ],
    preview: html`
      <figure class="mono-proof">
        <figcaption class="mono-proof-header meta">
          <span>Porto Faifo Mono</span><span>0.576 em per cell</span>
        </figcaption>
        <div class="mono-proof-grid" aria-hidden="true">
          ${each(monoGlyphs, (_, index) => index, (glyph) => html`<span>${glyph}</span>`)}
        </div>
        <p class="mono-proof-caption">From <span>i</span> to <span>W</span>, every letter takes one column.</p>
      </figure>`,
  },
  symbols: {
    name: 'Symbols',
    label: 'Interface icon set',
    archive: 'PFSymbols',
    title: 'Porto Faifo Symbols | Open-Source Interface Icons',
    metaDescription: `Browse ${symbolData.length} free SVG interface icons for navigation, controls and status. Preview four sizes and stroke weights in the Porto Faifo Symbols dashboard.`,
    description: 'Interface icons drawn to match the strokes of Porto Faifo. Each size has its own drawing to keep the details clear at the scale you use.',
    demoTitle: 'Icons in context.',
    demoDescription: 'Change the size and stroke weight of the original Porto Faifo icons in navigation, filters and order statuses.',
    facts: [
      ['Catalogue', `${symbolData.length} symbols`],
      ['Sizes', `${sizes.join(', ')} px`],
      ['Styles', `${symbolWeights.length} weights`],
    ],
    preview: html`<span class="card-symbol-sample">
      ${each(['sparkles', 'command', 'map-pin', 'layers'], (name) => name, (name) => symbol(name, base))}
    </span>`,
  },
}

export function collectionPage(part: CollectionPart) {
  const product = products[part]
  const isSymbols = part === 'symbols'
  const isMono = part === 'mono'
  const workLabel = isSymbols ? 'Browse the symbols' : 'Try the type'

  return definePage({
    path: routes[part],
    head: pageHead(product.title, product.metaDescription, part),
    view: () => html`
      ${header(part)}
      <main id="content">
        <section class=${`wrap detail-hero detail-hero-${part}`} aria-labelledby="detail-title">
          <div class="detail-copy">
            <p class="meta section-label">${product.label}</p>
            <h1 id="detail-title">Porto Faifo<br><span>${product.name}</span></h1>
            <p class="detail-description">${product.description}</p>
            <div class="hero-actions">
              <a class="button button-primary" href=${archive(product.archive)}>Download ${product.name} ${symbol('download', base)}</a>
              <a class="button button-text" href="#demo">${isMono ? 'See the report' : 'See the dashboard'} ${symbol('arrow-down', base)}</a>
            </div>
          </div>
          <div class=${`detail-plate card-${part}`} aria-hidden=${isMono ? null : 'true'}>${product.preview}</div>
        </section>

        <div class="facts">
          <dl class="wrap facts-inner detail-facts">
            ${each(product.facts, ([key]) => key, ([key, value]) => html`
              <div><dt>${key}</dt><dd>${value}</dd></div>
            `)}
          </dl>
        </div>

        <section id="demo" class="wrap section demo-section" aria-labelledby="demo-title">
          <div class="section-heading">
            <h2 id="demo-title">${product.demoTitle}</h2>
            <p>${product.demoDescription}</p>
          </div>
          ${isMono ? island('mono-demo', monoDemo, {}) : island('dashboard', dashboard, { mode: part, base })}
          <section class="live-examples" aria-labelledby="live-examples-title">
            <h3 id="live-examples-title">Explore live websites</h3>
            ${productionLinks(base)}
          </section>
          <div class="demo-next">
            <a class="inline-link" href="#preview">${workLabel} ${symbol('arrow-down', base)}</a>
          </div>
        </section>

        <section id="preview" class=${isSymbols ? 'wrap section' : 'specimen-section'} aria-labelledby="preview-title">
          <div class=${isSymbols ? null : 'wrap section'}>
            <div class="section-heading">
              <h2 id="preview-title">${workLabel}.</h2>
              <p>${isSymbols
                ? 'Preview the 24 px Regular drawings and search by name, alias or category.'
                : 'Edit the sample directly and change the typeface, weight or size.'}</p>
            </div>
            ${isSymbols ? island('symbols', symbols, { base }) : island('specimen', specimen, { initialFamily: part })}
            <noscript><p class="fallback-note">${isSymbols
              ? 'Enable JavaScript to search and expand the catalogue.'
              : 'The sample text is editable. Typeface, weight and size controls require JavaScript.'}</p></noscript>
          </div>
        </section>
      </main>
      ${footer(base)}
    `,
  })
}
