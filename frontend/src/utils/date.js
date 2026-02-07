// 日期格式化工具

export function formatDate(date, format = 'YYYY-MM-DD') {
  if (!date) return ''
  
  const d = new Date(date)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hour = String(d.getHours()).padStart(2, '0')
  const minute = String(d.getMinutes()).padStart(2, '0')
  const second = String(d.getSeconds()).padStart(2, '0')
  
  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hour)
    .replace('mm', minute)
    .replace('ss', second)
}

export function formatMonth(date) {
  return formatDate(date, 'YYYY-MM')
}

export function getToday() {
  return formatDate(new Date())
}

export function getCurrentMonth() {
  return formatMonth(new Date())
}

export function getMonthStartEnd(month) {
  const [year, monthNum] = month.split('-').map(Number)
  const start = `${year}-${String(monthNum).padStart(2, '0')}-01`
  const lastDay = new Date(year, monthNum, 0).getDate()
  const end = `${year}-${String(monthNum).padStart(2, '0')}-${lastDay}`
  return { start, end }
}

export function getDaysBetween(start, end) {
  const startDate = new Date(start)
  const endDate = new Date(end)
  const diffTime = Math.abs(endDate - startDate)
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1
}
