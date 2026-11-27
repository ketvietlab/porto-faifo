import { html, signal } from '@ketvietlab/ketjs-view'
import type { IslandFactory } from '@ketvietlab/ketjs-view'
import { orders, orderStatuses } from '../demo-data.ts'
import { selectControl } from '../select-control.ts'

const formatLine = (order: string, total: string, status: string) => `${order.padEnd(10)}${total.padStart(12)}  ${status}`
const report = [
  formatLine('ORDER', 'TOTAL (₫)', 'STATUS'),
  '───────   ────────────  ────────',
  ...orders.map(({ id, total, status }) => formatLine(id, total, orderStatuses[status])),
].join('\n')

const monoDemo: IslandFactory<Record<string, never>> = () => {
  const ready = signal(false)
  const family = signal('mono')

  return {
    mount: () => ready.set(true),
    view: () => html`
      <div class="mono-demo">
        <fieldset class="demo-controls" disabled=${!ready()}>
          <legend class="sr-only">Report typography</legend>
          <label>Typeface
            ${selectControl(html`
              <option value="mono">Porto Faifo Mono</option>
              <option value="sans">Porto Faifo Sans</option>
            `, (value) => family.set(value))}
          </label>
        </fieldset>
        <div class="mono-report">
          <div class="mono-report-heading">
            <h3>Order reconciliation</h3><span class="meta">${orders.length} records</span>
          </div>
          <pre tabindex="0" class=${`mono-report-text report-${family()}`} aria-label="Order reconciliation report">${report}</pre>
        </div>
      </div>
    `,
  }
}

export default monoDemo
