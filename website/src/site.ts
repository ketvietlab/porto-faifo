export const siteOrigin = 'https://portofaifo.com'
export const repository = 'https://github.com/ketvietlab/porto-faifo'

export const routes = {
  home: '/',
  sans: '/sans/',
  mono: '/mono/',
  symbols: '/symbols/',
} as const

export type SitePage = keyof typeof routes
export type CollectionPart = Exclude<SitePage, 'home'>

export const canonicalUrl = (page: SitePage) => `${siteOrigin}${routes[page]}`
