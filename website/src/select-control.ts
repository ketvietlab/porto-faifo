import { html } from '@ketvietlab/ketjs-view'
import type { TemplateResult } from '@ketvietlab/ketjs-view'

export function selectControl(options: TemplateResult, onChange: (value: string) => void, disabled = false) {
  return html`<span class="select-control">
    <select disabled=${disabled} on:change=${(event: Event) => onChange((event.currentTarget as HTMLSelectElement).value)}>
      ${options}
    </select>
  </span>`
}
