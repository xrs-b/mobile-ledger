// 金额格式化工具

export function formatAmount(amount, options = {}) {
  const { showSymbol = true, decimals = 2 } = options
  
  if (amount === null || amount === undefined) return '-'
  
  const num = Number(amount)
  if (isNaN(num)) return '-'
  
  const formatted = num.toLocaleString('zh-CN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  })
  
  return showSymbol ? `¥${formatted}` : formatted
}

export function formatAmountSimple(amount) {
  if (amount === null || amount === undefined) return '0'
  
  const num = Math.abs(Number(amount))
  if (num >= 10000) {
    return `${(num / 10000).toFixed(1)}万`
  } else if (num >= 1000) {
    return `${(num / 1000).toFixed(1)}k`
  }
  return num.toFixed(0)
}

export function formatPercent(value, total, decimals = 1) {
  if (!total || total === 0) return '0%'
  return `${((value / total) * 100).toFixed(decimals)}%`
}

export function getAmountColor(type) {
  return type === 'income' ? '#07c160' : '#ee0a24'
}

export function getTypeLabel(type) {
  return type === 'income' ? '收入' : '支出'
}
