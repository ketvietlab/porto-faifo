import { copyFile, mkdir, readFile, writeFile } from 'node:fs/promises'

const repository = new URL('../../', import.meta.url)
const assets = new URL('../public/assets/', import.meta.url)

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

await writeFile(
  new URL('../src/asset-data.ts', import.meta.url),
  '// Generated from VERSION, design-system.json and symbols/manifest.json.\n' +
    `export const version = ${JSON.stringify(version)}\n` +
    `export const sansWeights = ${JSON.stringify(sansWeights)}\n` +
    `export const sizes = ${JSON.stringify(sizes)}\n` +
    `export const symbolWeights = ${JSON.stringify(weights)}\n` +
    `export const symbolData = ${JSON.stringify(symbolData, null, 2)}\n`,
)
