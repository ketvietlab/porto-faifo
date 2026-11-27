import { html } from '@ketvietlab/ketjs-view'

export function symbol(name: string, base = './') {
  return html`<svg class="symbol" width="24" height="24" aria-hidden="true" focusable="false">
    <use href=${`${base}assets/porto-faifo-symbols.svg#pf-${name}`}></use>
  </svg>`
}
