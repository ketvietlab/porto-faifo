import { each, html } from '@ketvietlab/ketjs-view'
import { symbol } from './symbol.ts'

const links = [
  {
    href: 'https://ketjs.dev/playground/',
    title: 'Try the KetJS playground',
    description: 'Edit and run KetJS View examples in your browser.',
  },
  {
    href: 'https://ketviet.vn/',
    title: 'Explore Két Việt ERP',
    description: 'See the platform for sales, inventory and accounting.',
  },
]

export function productionLinks(base = './') {
  return html`<ul class="production-links">
    ${each(links, ({ href }) => href, ({ href, title, description }) => html`<li>
      <a href=${href}>
        <span><strong>${title}</strong><small>${description}</small></span>
        ${symbol('arrow-up-right', base)}
      </a>
    </li>`)}
  </ul>`
}
