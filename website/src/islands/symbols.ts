import { each, html, signal } from '@ketvietlab/ketjs-view'
import type { IslandFactory } from '@ketvietlab/ketjs-view'
import { symbolData } from '../asset-data.ts'
import { symbol } from '../symbol.ts'

const featuredCount = 18
const featured = [
  'search', 'arrow-up-right', 'map-pin', 'sparkles', 'layers', 'sun',
  'terminal', 'command', 'settings', 'wifi', 'bell', 'star',
  'cloud', 'book-open', 'calendar', 'file-text', 'folder', 'camera',
]
const featuredNames = new Set(featured)
const byName = new Map(symbolData.map((entry) => [entry.name, entry]))
const catalogue = [
  ...featured.flatMap((name) => byName.get(name) ?? []),
  ...symbolData.filter(({ name }) => !featuredNames.has(name)),
]

const symbols: IslandFactory<{ base?: string }> = ({ base = './' }) => {
  const ready = signal(false)
  const query = signal('')
  const expanded = signal(false)

  return {
    mount: () => ready.set(true),
    view: () => {
      const terms = query().trim().toLowerCase().split(/[\s-]+/).filter(Boolean)
      const matching = terms.length ? catalogue.filter(({ name, aliases, group, lucide }) => {
        const keywords = [name, group, lucide, ...aliases].join(' ').toLowerCase()
        return terms.every((term) => keywords.includes(term))
      }) : catalogue
      const visible = expanded() ? matching : matching.slice(0, featuredCount)

      return html`
        <div class="symbol-browser">
          <div class="symbol-toolbar">
            <label class="symbol-search">
              ${symbol('search', base)}
              <span class="sr-only">Search symbols</span>
              <input type="search" placeholder="Search symbols" disabled=${!ready()}
                on:input=${(event: Event) => {
                  query.set((event.currentTarget as HTMLInputElement).value)
                  expanded.set(false)
                }}>
            </label>
            <div class="symbol-toolbar-actions">
              <p class="symbol-count meta" role="status">${`Showing ${visible.length} of ${matching.length}`}</p>
              ${matching.length > featuredCount ? html`
                <button type="button" class="button button-outline" aria-controls="symbol-results"
                  disabled=${!ready()} aria-expanded=${String(expanded())} on:click=${() => expanded.set(!expanded())}>
                  ${expanded() ? 'Show fewer symbols' : `Show all ${matching.length} symbols`}
                </button>
              ` : null}
            </div>
          </div>
          ${matching.length ? html`
            <ul class="symbol-grid" id="symbol-results" aria-label="Matching symbols">
              ${each(visible, ({ name }) => name, ({ name }) =>
                html`<li>${symbol(name, base)}<span>${name}</span></li>`)}
            </ul>
          ` : html`<p class="symbol-empty">No symbols found. Try a different name or category.</p>`}
        </div>
      `
    },
  }
}

export default symbols
