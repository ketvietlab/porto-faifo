export const dashboardIcons = {
  workspace: 'table',
  orders: 'file-text',
  customers: 'users',
  quotes: 'receipt',
  inventory: 'package',
  receivables: 'wallet',
  reports: 'chart-bar',
  filter: 'filter',
  paid: 'check',
  due: 'clock',
  overdue: 'warning',
  draft: 'file-text',
} as const

export const orderStatuses = {
  due: 'Due soon',
  paid: 'Paid',
  overdue: 'Overdue',
  draft: 'Draft',
} as const

type OrderStatus = keyof typeof orderStatuses

type Order = {
  id: string
  customer: string
  date: string
  total: string
  received: string
  status: OrderStatus
}

// Sales data adapted from the Dashboard in specimen/index.html.
export const orders: readonly Order[] = [
  { id: 'HD-2045', customer: 'Công ty TNHH Phú Quý', date: '2026-10-03', total: '12.100.000', received: '1.200.000', status: 'due' },
  { id: 'HD-2044', customer: 'Việt Ánh Group', date: '2026-10-02', total: '2.010.000', received: '2.010.000', status: 'paid' },
  { id: 'HD-2043', customer: 'Nhà sách Gia Khánh', date: '2026-10-01', total: '748.500', received: '0', status: 'overdue' },
  { id: 'HD-2042', customer: 'Cửa hàng Ngọc Yến', date: '2026-09-30', total: '21.000.200', received: '10.000.000', status: 'draft' },
  { id: 'HD-2041', customer: 'Bếp Ấm Đà Lạt', date: '2026-09-29', total: '3.456.789', received: '3.456.789', status: 'paid' },
  { id: 'HD-2040', customer: 'Quỹ Xã hội Hướng Dương', date: '2026-09-28', total: '200.200.000', received: '20.000.000', status: 'due' },
]
