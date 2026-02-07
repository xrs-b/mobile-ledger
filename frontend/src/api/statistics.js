import request from './request'

export function getStatisticsOverview(params = {}) {
  return request.get('/statistics/overview', { params })
}

export function getStatisticsDaily(params = {}) {
  return request.get('/statistics/daily', { params })
}

export function getStatisticsMonthly(params = {}) {
  return request.get('/statistics/monthly', { params })
}

export function getStatisticsCategory(params = {}) {
  return request.get('/statistics/category', { params })
}

export function getStatisticsTrend(params = {}) {
  return request.get('/statistics/trend', { params })
}

export function getStatisticsDashboard(params = {}) {
  return request.get('/statistics/dashboard', { params })
}

export function getStatisticsYearly(params = {}) {
  return request.get('/statistics/yearly', { params })
}

export function getStatisticsCompareMonths(params = {}) {
  return request.get('/statistics/compare/months', { params })
}

export function getStatisticsCompareCategories(params = {}) {
  return request.get('/statistics/compare/categories', { params })
}
