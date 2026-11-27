import { each, html } from '@ketvietlab/ketjs-view'
import type { PageHead } from '@ketvietlab/ketjs-view-tools'
import { version } from './asset-data.ts'
import { canonicalUrl, repository, routes, siteOrigin } from './site.ts'
import type { CollectionPart } from './site.ts'
import { symbol } from './symbol.ts'

export const release = `${repository}/releases/tag/v${version}`
export const archive = (name: string) => `${repository}/releases/download/v${version}/${name}-${version}.zip`

const navigation = [
  { label: 'Sans', path: 'sans' },
  { label: 'Mono', path: 'mono' },
  { label: 'Symbols', path: 'symbols' },
] as const

const siteName = 'Porto Faifo'
const siteId = `${siteOrigin}/#website`
const publisher = { '@type': 'Organization', name: 'Két Việt', url: 'https://ketviet.vn/' }

export function pageHead(title: string, description: string, current?: CollectionPart): PageHead {
  const base = current ? '../' : './'
  const canonical = canonicalUrl(current ?? 'home')
  const image = `${siteOrigin}/assets/porto-faifo-social.png`
  const variant = navigation.find(({ path }) => path === current)?.label
  const work = {
    '@type': 'CreativeWork',
    name: variant ? `${siteName} ${variant}` : siteName,
    url: canonical,
    isAccessibleForFree: true,
    license: `${siteOrigin}/assets/OFL.txt`,
    creator: publisher,
  }

  return {
    title,
    description,
    lang: 'en',
    meta: [
      { name: 'theme-color', content: '#f7f2e9' },
      { property: 'og:type', content: 'website' },
      { property: 'og:site_name', content: siteName },
      { property: 'og:title', content: title },
      { property: 'og:description', content: description },
      { property: 'og:url', content: canonical },
      { property: 'og:image', content: image },
      { property: 'og:image:type', content: 'image/png' },
      { property: 'og:image:width', content: '1200' },
      { property: 'og:image:height', content: '630' },
      { property: 'og:image:alt', content: 'Porto Faifo wordmark and the Vietnamese letters Ắ and ơ.' },
      { name: 'twitter:card', content: 'summary_large_image' },
    ],
    links: [
      { rel: 'canonical', href: canonical },
      { rel: 'icon', href: `${base}favicon.svg`, type: 'image/svg+xml' },
      { rel: 'stylesheet', href: `${base}assets/fonts.css` },
    ],
    structuredData: [{
      '@context': 'https://schema.org',
      '@type': 'WebPage',
      name: title,
      url: canonical,
      description,
      inLanguage: 'en',
      isPartOf: { '@id': siteId },
      mainEntity: work,
    }, ...(current ? [] : [{
      '@context': 'https://schema.org',
      '@type': 'WebSite',
      '@id': siteId,
      name: siteName,
      url: canonical,
      inLanguage: 'en',
      publisher,
    }])],
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
            html`<a href=${`${base}${routes[path].slice(1)}`} aria-current=${current === path ? 'page' : null}>${label}</a>`)}
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
