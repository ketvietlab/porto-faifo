import { each, html } from '@ketvietlab/ketjs-view'
import { version } from './asset-data.ts'
import { symbol } from './symbol.ts'

export const repository = 'https://github.com/ketvietlab/porto-faifo'
export const release = `${repository}/releases/tag/v${version}`
export const archive = (name: string) => `${repository}/releases/download/v${version}/${name}-${version}.zip`

const navigation = [
  { label: 'Sans', path: 'sans' },
  { label: 'Mono', path: 'mono' },
  { label: 'Symbols', path: 'symbols' },
] as const

export type CollectionPart = (typeof navigation)[number]['path']

export function pageHead(title: string, description: string, current?: CollectionPart) {
  const base = current ? '../' : './'
  return {
    title,
    description,
    lang: 'en',
    meta: [{ name: 'theme-color', content: '#f7f2e9' }],
    links: [
      { rel: 'canonical', href: `https://portofaifo.com/${current ? `${current}/` : ''}` },
      { rel: 'icon', href: `${base}favicon.svg`, type: 'image/svg+xml' },
      { rel: 'stylesheet', href: `${base}assets/fonts.css` },
    ],
  }
}

function brand(base: string) {
  return html`<a class="brand" href=${base}>
    <span class="brand-mark" aria-hidden="true">pf</span>
    <span>Porto Faifo</span>
  </a>`
}

export function header(current?: CollectionPart) {
  const base = current ? '../' : './'
  return html`
    <link rel="preload" href=${`${base}assets/PortoFaifoSans%5Bopsz%2Cwght%5D.woff2`} as="font" type="font/woff2" crossorigin="anonymous" fetchpriority="high">
    <link rel="preload" href=${`${base}assets/PortoFaifoMono-Medium.woff2`} as="font" type="font/woff2" crossorigin="anonymous">
    <a class="skip-link" href="#content">Skip to content</a>
    <header class="site-header">
      <div class="wrap header-inner">
        ${brand(base)}
        <nav class="primary-nav" aria-label="Main navigation">
          ${each(navigation, ({ path }) => path, ({ path, label }) =>
            html`<a href=${`${base}${path}/`} aria-current=${current === path ? 'page' : null}>${label}</a>`)}
        </nav>
        <a class="button button-compact button-outline header-download" href=${current ? '../#download' : '#download'}>
          Download ${symbol('download', base)}
        </a>
      </div>
    </header>`
}

export function footer(base = './') {
  return html`
    <footer class="site-footer">
      <div class="wrap footer-inner">
        ${brand(base)}
        <p>A type project by <a href="https://ketviet.vn">Két Việt</a>.</p>
        <nav aria-label="Footer navigation">
          <a href=${`${base}assets/OFL.txt`}>Licence</a>
          <a href=${repository}>GitHub ${symbol('arrow-up-right', base)}</a>
        </nav>
      </div>
    </footer>`
}
