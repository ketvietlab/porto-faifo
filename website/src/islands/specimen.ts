import { each, html, signal } from '@ketvietlab/ketjs-view'
import type { IslandFactory } from '@ketvietlab/ketjs-view'
import { sansWeights } from '../asset-data.ts'
import { selectControl } from '../select-control.ts'

const samples = [
  { name: 'Vietnamese', lang: 'vi', text: 'Một chiều Hội An.\nNắng đậu trên mái ngói.' },
  { name: 'English', lang: 'en', text: 'The quiet rhythm\nof everyday letters.' },
  { name: 'Numbers', lang: 'en', text: '0123456789\n₫ 1.250.000  /  09:41' },
]

const monoWeights = sansWeights.filter(({ value }) => value === 400 || value === 500)

const specimen: IslandFactory<{ initialFamily?: 'sans' | 'mono' }> = ({ initialFamily = 'sans' }) => {
  const ready = signal(false)
  const family = signal(initialFamily)
  const weight = signal(500)
  const size = signal(48)
  const language = signal('vi')

  return {
    mount: () => ready.set(true),
    view: () => html`
      <div class="tester">
        <fieldset class="tester-controls" disabled=${!ready()}>
          <legend class="sr-only">Type settings</legend>
          <label>
            <span>Typeface</span>
            ${selectControl(html`
              <option value="sans" selected=${initialFamily === 'sans'}>Porto Faifo Sans</option>
              <option value="mono" selected=${initialFamily === 'mono'}>Porto Faifo Mono</option>
            `, (value) => {
              const next = value === 'mono' ? 'mono' : 'sans'
              family.set(next)
              if (next === 'mono' && !monoWeights.some(({ value: monoWeight }) => monoWeight === weight())) weight.set(500)
            })}
          </label>
          <label>
            <span>Weight</span>
            ${selectControl(html`
              ${each(family() === 'mono' ? monoWeights : sansWeights, ({ value }) => value, ({ name, value }) =>
                html`<option value=${value} selected=${value === weight()}>${name} ${value}</option>`)}
            `, (value) => weight.set(Number(value)))}
          </label>
          <div class="size-control">
            <label for="specimen-size">Size</label>
            <output for="specimen-size">${size()} px</output>
            <input id="specimen-size" type="range" min="16" max="128" value="48"
              on:input=${(event: Event) => size.set((event.currentTarget as HTMLInputElement).valueAsNumber)}>
          </div>
        </fieldset>

        <label class="sr-only" for="specimen-text">Editable specimen text</label>
        <textarea id="specimen-text" class=${`tester-text tester-${family()}`}
          style=${`--specimen-size:${size()}px;--specimen-weight:${weight()}`}
          lang=${language()} spellcheck="false">${samples[0].text}</textarea>

        <div class="tester-footer">
          <span>Sample text</span>
          <div class="sample-actions" role="group" aria-label="Sample text">
            ${each(samples, ({ name }) => name, (sample) =>
              html`<button type="button" disabled=${!ready()} on:click=${(event: Event) => {
                const button = event.currentTarget as HTMLButtonElement
                const preview = button.closest('.tester')?.querySelector<HTMLTextAreaElement>('#specimen-text')
                if (!preview) return
                preview.value = sample.text
                language.set(sample.lang)
                preview.focus()
              }}>${sample.name}</button>`)}
          </div>
        </div>
      </div>
    `,
  }
}

export default specimen
