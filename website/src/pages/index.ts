import { each, html } from '@ketvietlab/ketjs-view'
import { definePage, island } from '@ketvietlab/ketjs-view-tools'
import { sizes, symbolData, symbolWeights, version } from '../asset-data.ts'
import specimen from '../islands/specimen.ts'
import symbols from '../islands/symbols.ts'
import { archive, footer, header, pageHead, release } from '../layout.ts'
import { productionLinks } from '../production-links.ts'
import { routes } from '../site.ts'
import { symbol } from '../symbol.ts'

const iconCount = symbolData.length.toLocaleString('en')
const description = `Download Porto Faifo, a free collection for digital interfaces. Try Vietnamese Sans and Mono fonts, and browse ${iconCount} open-source SVG icons.`
const cards = [
  {
    name: 'Sans',
    kind: 'sans',
    note: 'Proportional typeface',
    title: 'Porto Faifo Sans',
    description: 'For headings, reading and interface text. A variable font with weight and optical-size axes.',
    details: '300–900 weight · 8–72 optical size',
    preview: html`<span class="card-glyph sans-glyph" aria-hidden="true">Aa</span>`,
  },
  {
    name: 'Mono',
    kind: 'mono',
    note: 'Fixed-width typeface',
    title: 'Porto Faifo Mono',
    description: 'For code, figures and places where every character needs the same amount of room.',
    details: '400 & 500 weights · 0.576 em advance',
    preview: html`<span class="card-glyph mono-glyph" aria-hidden="true"><span>i</span><span>W</span></span>`,
  },
  {
    name: 'Symbols',
    kind: 'symbols',
    note: 'Interface icon set',
    title: 'Porto Faifo Symbols',
    description: 'A set of interface icons with shapes tuned for four sizes and strokes that match the type.',
    details: `${symbolWeights.length} weights · ${sizes.join(', ')} px`,
    preview: html`<span class="card-symbol-sample" aria-hidden="true">
      ${each(['sparkles', 'command', 'map-pin', 'layers'], (name) => name, (name) => symbol(name))}
    </span>`,
  },
]
const downloads = [
  { name: 'Porto Faifo Sans', file: 'PFSans', formats: 'OTF, TTF, WOFF2, variable fonts' },
  { name: 'Porto Faifo Mono', file: 'PFMono', formats: 'OTF, TTF, WOFF2' },
  { name: 'Porto Faifo Symbols', file: 'PFSymbols', formats: 'SVG files, sprites and manifest' },
]

export default definePage({
  path: routes.home,
  head: pageHead('Porto Faifo | Free Vietnamese Fonts and Interface Icons', description),
  view: () => html`
    ${header()}

    <main id="content">
      <section class="hero wrap" aria-labelledby="hero-title">
        <div class="hero-copy">
          <p class="meta hero-kicker"><span></span> An open type collection by Két Việt</p>
          <h1 id="hero-title">Porto<br>Faifo<span>.</span></h1>
          <p class="hero-intro">Free fonts and icons for digital interfaces, with full Vietnamese support.</p>
          <div class="hero-actions">
            <a class="button button-primary" href="#download">Download the collection ${symbol('download')}</a>
            <a class="button button-text" href="#specimen">Try the type ${symbol('arrow-down')}</a>
          </div>
        </div>

        <figure class="hero-plate">
          <figcaption class="plate-header meta">
            <span>Porto Faifo Sans</span>
            <span>Vietnamese specimen</span>
          </figcaption>
          <div class="plate-body" lang="vi" aria-hidden="true">
            <div class="plate-line plate-line-cap"></div>
            <div class="plate-line plate-line-mid"></div>
            <div class="plate-line plate-line-base"></div>
            <span class="plate-letter">Ắ<span>ơ</span></span>
          </div>
          <div class="plate-footer">
            <span class="meta">Vietnamese Latin</span>
            <span class="plate-alphabet" lang="vi">Ă Â Đ Ê Ô Ơ Ư</span>
          </div>
        </figure>
      </section>

      <div class="facts">
        <dl class="wrap facts-inner">
          <div><dt>Typefaces</dt><dd>Sans + Mono</dd></div>
          <div><dt>Language coverage</dt><dd>Latin + Vietnamese</dd></div>
          <div><dt>Interface icons</dt><dd>${iconCount} symbols</dd></div>
          <div><dt>Licence</dt><dd><a href="./assets/OFL.txt">SIL OFL 1.1 ${symbol('arrow-up-right')}</a></dd></div>
        </dl>
      </div>

      <section id="collection" class="wrap section" aria-labelledby="collection-title">
        <div class="section-heading">
          <div>
            <p class="meta section-label">The collection</p>
            <h2 id="collection-title">Three parts.<br class="mobile-break"> One system.</h2>
          </div>
          <p>Two typefaces and a set of icons, drawn to work together across digital interfaces.</p>
        </div>
        <div class="collection-grid">
          ${each(cards, (card) => card.kind, (card) => html`
            <article class="collection-card">
              <div class=${`card-plate card-${card.kind}`}>
                <span class="meta">${card.note}</span>
                ${card.preview}
              </div>
              <div class="card-copy">
                <h3><a href=${`./${card.kind}/`}>${card.title} ${symbol('arrow-right')}</a></h3>
                <p>${card.description}</p>
                <p class="meta card-details">${card.details}</p>
              </div>
            </article>
          `)}
        </div>
      </section>

      <section id="specimen" class="specimen-section" aria-labelledby="specimen-title">
        <div class="wrap section">
          <div class="section-heading">
            <div>
              <p class="meta section-label">Live specimen</p>
              <h2 id="specimen-title">Try the type.</h2>
            </div>
            <p>Edit the text below to see how Porto Faifo looks in a heading, a short line of copy or a string of numbers.</p>
          </div>
          ${island('specimen', specimen, {})}
          <noscript><p class="fallback-note">The sample text is editable. Typeface, weight and size controls require JavaScript.</p></noscript>
        </div>
      </section>

      <section id="symbols" class="wrap section" aria-labelledby="symbols-title">
        <div class="section-heading">
          <div>
            <p class="meta section-label">The icon set</p>
            <h2 id="symbols-title">Drawn to fit.</h2>
          </div>
          <p>Porto Faifo Symbols includes ${iconCount} icons. Preview the 24 px Regular drawings and search by name, alias or category.</p>
        </div>
        ${island('symbols', symbols, {})}
        <noscript><p class="fallback-note">Enable JavaScript to search the catalogue, or <a href="#download">download the full set</a>.</p></noscript>
      </section>

      <section class="wrap live-examples home-live-examples" aria-labelledby="live-examples-title">
        <h2 id="live-examples-title">Explore live websites</h2>
        ${productionLinks()}
      </section>

      <section id="download" class="download-section" aria-labelledby="download-title">
        <div class="wrap section download-inner">
          <div class="download-copy">
            <p class="meta section-label">Version ${version}</p>
            <h2 id="download-title">Make it<br>yours.</h2>
            <p>The entire collection is available under the SIL Open Font License 1.1, for personal and commercial use.</p>
            <a class="inline-link" href=${release}>View release on GitHub ${symbol('arrow-up-right')}</a>
          </div>
          <ul class="download-list">
            ${each(downloads, ({ file }) => file, ({ name, file, formats }) => html`
              <li>
                <a href=${archive(file)} aria-label=${`Download ${name} ZIP`}>
                  <span><strong>${name}</strong><small>${formats}</small></span>
                  <span class="download-format meta">ZIP ${symbol('download')}</span>
                </a>
              </li>
            `)}
          </ul>
        </div>
      </section>
    </main>

    ${footer()}
  `,
})
