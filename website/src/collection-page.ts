import { each, html } from '@ketvietlab/ketjs-view'
import { definePage, island } from '@ketvietlab/ketjs-view-tools'
import { sansWeights, sizes, symbolData, symbolWeights } from './asset-data.ts'
import specimen from './islands/specimen.ts'
import symbols from './islands/symbols.ts'
import { archive, footer, header, pageHead } from './layout.ts'
import type { CollectionPart } from './layout.ts'
import { symbol } from './symbol.ts'

const base = '../'
const monoGlyphs = [...'il1O0WHội An']
const products = {
  sans: {
    name: 'Sans',
    label: 'Proportional typeface',
    archive: 'PFSans',
    description: `A variable typeface for digital interfaces and longer reading, with ${sansWeights.length} named weights, full Vietnamese support and optical sizes for small text and display.`,
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
    description: 'A fixed-width companion for code and tabular data. Vietnamese letters, digits and spaces sit on the same grid.',
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
    description: 'Interface icons drawn to match the strokes of Porto Faifo. Each size has its own drawing to keep the details clear at the scale you use.',
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
    head: pageHead(`Porto Faifo ${product.name}`, product.description, part),
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
              <a class="button button-text" href="#preview">${workLabel} ${symbol('arrow-down', base)}</a>
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
