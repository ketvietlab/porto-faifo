import { each, html, signal } from '@ketvietlab/ketjs-view'
import type { IslandFactory } from '@ketvietlab/ketjs-view'
import { sansWeights, sizes, symbolWeights } from '../asset-data.ts'
import { dashboardIcons, orders, orderStatuses } from '../demo-data.ts'
import { selectControl } from '../select-control.ts'

type SidebarEntry = {
  label: string
  icon: string
  count?: string
  selected?: boolean
}

const sidebar: readonly { label: string; entries: readonly SidebarEntry[] }[] = [
  { label: 'Sales', entries: [
    { label: 'Orders', icon: dashboardIcons.orders, count: '1.248', selected: true },
    { label: 'Customers', icon: dashboardIcons.customers, count: '312' },
    { label: 'Quotes', icon: dashboardIcons.quotes, count: '27' },
    { label: 'Inventory', icon: dashboardIcons.inventory, count: '48' },
  ] },
  { label: 'Accounting', entries: [
    { label: 'Receivables', icon: dashboardIcons.receivables },
    { label: 'Tax reports', icon: dashboardIcons.reports },
  ] },
]

const metrics = [
  { label: 'Revenue', value: '12.480.500.000 ₫', change: '+8.4%', tone: 'positive' },
  { label: 'Orders', value: '1.248', change: '+3.1%', tone: 'positive' },
  { label: 'Receivables', value: '1.012.300.000 ₫', change: '−2.2%', tone: 'negative' },
  { label: 'Overdue', value: '17', change: 'Need follow-up', tone: 'warning' },
]

const dateFormat = new Intl.DateTimeFormat('en-GB', { dateStyle: 'medium', timeZone: 'UTC' })

type DashboardProps = {
  mode: 'sans' | 'symbols'
  base: string
}

const dashboard: IslandFactory<DashboardProps> = ({ mode, base }) => {
  const ready = signal(false)
  const weight = signal(400)
  const figures = signal('tabular')
  const iconSize = signal(20)
  const stroke = signal('Regular')
  const status = signal('all')
  const showIcons = mode === 'symbols'

  function icon(name: string) {
    if (!showIcons) return null
    const size = iconSize()
    const href = `${base}assets/porto-faifo-dashboard-symbols.svg#pf-${name}-${size}-${stroke().toLowerCase()}`
    return html`<span class="dashboard-icon" aria-hidden="true"><svg class="symbol" width=${size} height=${size}
      focusable="false"><use href=${href}></use></svg></span>`
  }

  return {
    mount: () => ready.set(true),
    view: () => {
      const rows = status() === 'all' ? orders : orders.filter((order) => order.status === status())
      return html`
        <div class="dashboard-demo">
          <fieldset class="demo-controls" disabled=${!ready()}>
            <legend class="sr-only">${showIcons ? 'Icon preview settings' : 'Typography preview settings'}</legend>
            ${showIcons ? html`
              <label>Icon size
                ${selectControl(html`
                  ${each(sizes, (size) => size, (size) => html`<option value=${size} selected=${size === 20}>${size} px</option>`)}
                `, (value) => iconSize.set(Number(value)))}
              </label>
              <label>Stroke weight
                ${selectControl(html`
                  ${each(symbolWeights, (name) => name, (name) => html`<option value=${name} selected=${name === 'Regular'}>${name}</option>`)}
                `, (value) => stroke.set(value))}
              </label>
            ` : html`
              <label>Text weight
                ${selectControl(html`
                  ${each(sansWeights, ({ value }) => value, ({ name, value }) =>
                    html`<option value=${value} selected=${value === 400}>${name} ${value}</option>`)}
                `, (value) => weight.set(Number(value)))}
              </label>
              <label>Figures
                ${selectControl(html`
                  <option value="tabular">Tabular</option>
                  <option value="proportional">Proportional</option>
                `, (value) => figures.set(value))}
              </label>
            `}
          </fieldset>
          <div class="dashboard" style=${`--dashboard-weight:${weight()};--dashboard-figures:${figures()}-nums`}>
            <aside class="dashboard-sidebar" aria-label="Sample workspace">
              <p class="dashboard-brand">${icon(dashboardIcons.workspace)} Sales workspace</p>
              ${each(sidebar, ({ label }) => label, ({ label, entries }) => html`<div class="dashboard-nav-group">
                <p>${label}</p>
                <ul>
                  ${each(entries, (entry) => entry.label, (entry) => html`<li class=${entry.selected ? 'dashboard-selected' : null}>
                    ${icon(entry.icon)}<span>${entry.label}</span>
                    ${entry.count ? html`<span class="dashboard-count">${entry.count}</span>` : null}
                  </li>`)}
                </ul>
              </div>`)}
            </aside>
            <div class="dashboard-body">
              <div class="dashboard-heading">
                <h3>Orders in October</h3>
                <label class="dashboard-filter">
                  ${icon(dashboardIcons.filter)}
                  <span class="sr-only">Filter orders by status</span>
                  ${selectControl(html`
                    <option value="all">All statuses</option>
                    ${each(Object.entries(orderStatuses), ([key]) => key, ([key, label]) => html`<option value=${key}>${label}</option>`)}
                  `, (value) => status.set(value), !ready())}
                </label>
              </div>
              <dl class="dashboard-metrics">
                ${each(metrics, ({ label }) => label, ({ label, value, change, tone }) => html`<div>
                  <dt>${label}</dt><dd>${value}</dd><dd class=${`dashboard-change ${tone}`}>${change}</dd>
                </div>`)}
              </dl>
              <div class="dashboard-orders">
                <div class="dashboard-orders-heading">
                  <h4>Recent orders</h4>
                  <span class="dashboard-order-count" role="status">${`${rows.length} ${rows.length === 1 ? 'order' : 'orders'}`}</span>
                </div>
                <div class="dashboard-table-region" tabindex="0" role="region" aria-label="Recent orders table">
                  <table class="dashboard-table">
                    <thead><tr>
                      <th scope="col">Order</th><th scope="col">Customer</th><th scope="col">Date</th>
                      <th scope="col" class="dashboard-amount">Total (₫)</th>
                      <th scope="col" class="dashboard-amount">Received (₫)</th><th scope="col">Status</th>
                    </tr></thead>
                    <tbody>${each(rows, ({ id }) => id, (order) => html`<tr>
                      <th scope="row">${order.id}</th><td lang="vi">${order.customer}</td>
                      <td><time datetime=${order.date}>${dateFormat.format(new Date(order.date))}</time></td>
                      <td class="dashboard-amount">${order.total}</td><td class="dashboard-amount">${order.received}</td>
                      <td><span class=${`dashboard-status ${order.status}`}>${icon(dashboardIcons[order.status])}${orderStatuses[order.status]}</span></td>
                    </tr>`)}</tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      `
    },
  }
}

export default dashboard
