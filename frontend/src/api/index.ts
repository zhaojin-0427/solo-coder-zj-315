import axios from 'axios'
import type { Theme, Utensil, TeaPlan, BorrowList, ActivityReview, StatisticsResponse, SelectedItem, Reservation, ConflictCheckResponse } from '@/types'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

const formatDate = (d: Date): string => {
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const normalizeDates = (data: any): any => {
  if (data instanceof Date) {
    return formatDate(data)
  }
  if (typeof data === 'string' && /^\d{4}-\d{2}-\d{2}T/.test(data)) {
    return formatDate(new Date(data))
  }
  if (Array.isArray(data)) {
    return data.map(normalizeDates)
  }
  if (data && typeof data === 'object') {
    const result: Record<string, any> = {}
    for (const [key, value] of Object.entries(data)) {
      result[key] = normalizeDates(value)
    }
    return result
  }
  return data
}

api.interceptors.request.use((config) => {
  if (config.data !== undefined && config.data !== null) {
    config.data = normalizeDates(config.data)
  }
  if (config.params !== undefined && config.params !== null) {
    config.params = normalizeDates(config.params)
  }
  return config
})

export const themeApi = {
  getAll: () => api.get<Theme[]>('/themes'),
  getOne: (id: number) => api.get<Theme>(`/themes/${id}`),
  create: (data: Omit<Theme, 'id'>) => api.post<Theme>('/themes', data)
}

export const utensilApi = {
  getAll: (category?: string) => api.get<Utensil[]>('/utensils', { params: { category } }),
  getOne: (id: number) => api.get<Utensil>(`/utensils/${id}`),
  create: (data: Omit<Utensil, 'id'>) => api.post<Utensil>('/utensils', data),
  update: (id: number, data: Partial<Utensil>) => api.put<Utensil>(`/utensils/${id}`, data)
}

export const teaPlanApi = {
  getAll: (status?: string) => api.get<TeaPlan[]>('/tea-plans', { params: { status } }),
  getOne: (id: number) => api.get<TeaPlan>(`/tea-plans/${id}`),
  create: (data: any) => api.post<TeaPlan>('/tea-plans', data),
  update: (id: number, data: Partial<TeaPlan>) => api.put<TeaPlan>(`/tea-plans/${id}`, data),
  regenerate: (id: number) => api.post<TeaPlan>(`/tea-plans/${id}/regenerate`)
}

export const borrowListApi = {
  getAll: (status?: string) => api.get<BorrowList[]>('/borrow-lists', { params: { status } }),
  getOne: (id: number) => api.get<BorrowList>(`/borrow-lists/${id}`),
  create: (data: any) => api.post<BorrowList>('/borrow-lists', data),
  update: (id: number, data: any) => api.put<BorrowList>(`/borrow-lists/${id}`, data),
  updateItem: (itemId: number, data: any) => api.put(`/borrow-items/${itemId}`, data)
}

export const reviewApi = {
  getAll: () => api.get<ActivityReview[]>('/activity-reviews'),
  getOne: (id: number) => api.get<ActivityReview>(`/activity-reviews/${id}`),
  create: (data: any) => api.post<ActivityReview>('/activity-reviews', data),
  update: (id: number, data: any) => api.put<ActivityReview>(`/activity-reviews/${id}`, data),
  updateItem: (itemId: number, data: any) => api.put(`/review-items/${itemId}`, data)
}

export const statsApi = {
  getStatistics: () => api.get<StatisticsResponse>('/statistics')
}

export const recommendApi = {
  getRecommendation: (data: { theme_color: string; tea_category: string; people_count: number; budget: number; photo_style: string }) =>
    api.post('/recommend', data)
}

export const reservationApi = {
  getAll: (params?: {
    status?: string; start_date?: string; end_date?: string; tea_category?: string; theme_color?: string }) =>
    api.get<Reservation[]>('/reservations', { params }),
  getOne: (id: number) => api.get<Reservation>(`/reservations/${id}`),
  checkConflict: (params: { check_date: string; time_slot: string; exclude_reservation_id?: number; exclude_plan_id?: number }) =>
    api.get<ConflictCheckResponse>('/reservations/check-conflict', { params }),
  create: (data: Omit<Reservation, 'id' | 'plans'>) => api.post<Reservation>('/reservations', data),
  update: (id: number, data: Partial<Omit<Reservation, 'id' | 'plans'>>) => api.put<Reservation>(`/reservations/${id}`, data),
  confirm: (id: number) => api.post<Reservation>(`/reservations/${id}/confirm`),
  cancel: (id: number) => api.post<Reservation>(`/reservations/${id}/cancel`),
  convert: (id: number, data: { theme_id: number; name: string }) =>
    api.post<TeaPlan>(`/reservations/${id}/convert`, data)
}

export default api
