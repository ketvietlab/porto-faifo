import { copyFile, mkdir, readFile, writeFile } from 'node:fs/promises'
import { dashboardIcons } from '../src/demo-data.ts'
import { canonicalUrl, routes, siteOrigin } from '../src/site.ts'

const repository = new URL('../../', import.meta.url)
const publicDir = new URL('../public/', import.meta.url)
const assets = new URL('assets/', publicDir)

await mkdir(assets, { recursive: true })

const files = {
  'fonts/variable/PortoFaifoSans[opsz,wght].woff2': 'PortoFaifoSans[opsz,wght].woff2',
  'fonts/mono/woff2/PortoFaifoMono-Regular.woff2': 'PortoFaifoMono-Regular.woff2',
  'fonts/mono/woff2/PortoFaifoMono-Medium.woff2': 'PortoFaifoMono-Medium.woff2',
  'symbols/sprites/pf-symbols-24-regular.svg': 'porto-faifo-symbols.svg',
  'OFL.txt': 'OFL.txt',
}

await Promise.all(Object.entries(files).map(([source, target]) =>
  copyFile(new URL(source, repository), new URL(target, assets)),
))

const [versionSource, manifestSource, designSystemSource] = await Promise.all([
  readFile(new URL('VERSION', repository), 'utf8'),
  readFile(new URL('symbols/manifest.json', repository), 'utf8'),
  readFile(new URL('design-system.json', repository), 'utf8'),
])
const version = versionSource.trim()
const { symbols, sizes, weights } = JSON.parse(manifestSource)
const symbolData = symbols.map(({ name, aliases, group, lucide }) => ({ name, aliases, group, lucide }))
const { variable: { instances } } = JSON.parse(designSystemSource)
const sansWeights = Object.entries(instances)
  .map(([name, value]) => ({ name, value }))
  .sort((left, right) => left.value - right.value)

const demoIcons = new Set(Object.values(dashboardIcons))
const dashboardSprites = await Promise.all(sizes.flatMap((size) => weights.map(async (weight) => {
  const variant = `${size}-${weight.toLowerCase()}`
  const filename = `symbols/sprites/pf-symbols-${variant}.svg`
  const source = await readFile(new URL(filename, repository), 'utf8')
  const definitions = new Map(Array.from(source.matchAll(/<symbol id="pf-([^"]+)"[^>]*>[\s\S]*?<\/symbol>/g),
    ([definition, name]) => [name, definition]))

  return Array.from(demoIcons, (name) => {
    const definition = definitions.get(name)
    if (!definition) throw new Error(`Missing dashboard symbol ${name} in ${filename}`)
    return definition.replace(`id="pf-${name}"`, `id="pf-${name}-${variant}"`)
  }).join('\n')
})))

await writeFile(
  new URL('porto-faifo-dashboard-symbols.svg', assets),
  '<!-- Porto Faifo Symbols. Copyright (c) 2026 The Porto Faifo Project Authors. SIL Open Font License 1.1. -->\n' +
    `<svg xmlns="http://www.w3.org/2000/svg">\n${dashboardSprites.join('\n')}\n</svg>\n`,
)

await writeFile(
  new URL('../src/asset-data.ts', import.meta.url),
  '// Generated from VERSION, design-system.json and symbols/manifest.json.\n' +
    `export const version = ${JSON.stringify(version)}\n` +
    `export const sansWeights = ${JSON.stringify(sansWeights)}\n` +
    `export const sizes = ${JSON.stringify(sizes)}\n` +
    `export const symbolWeights = ${JSON.stringify(weights)}\n` +
    `export const symbolData = ${JSON.stringify(symbolData, null, 2)}\n`,
)

const entries = Object.keys(routes).map((page) => `  <url><loc>${canonicalUrl(page)}</loc></url>`)
await Promise.all([
  writeFile(new URL('sitemap.xml', publicDir), [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ...entries,
    '</urlset>',
    '',
  ].join('\n')),
  writeFile(new URL('robots.txt', publicDir), `User-agent: *\nAllow: /\n\nSitemap: ${siteOrigin}/sitemap.xml\n`),
])
