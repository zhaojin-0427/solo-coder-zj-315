export interface Theme {
  id: number
  name: string
  description?: string
  color: string
  tea_category: string
  style: string
  min_people: number
  max_people: number
  min_budget: number
  max_budget: number
}

export interface Utensil {
  id: number
  name: string
  category: string
  material: string
  color: string
  style: string
  price: number
  quantity: number
  available: number
  description?: string
  image_url?: string
}

export interface RecommendedItem {
  id: number
  utensil_id: number
  quantity: number
  selected: boolean
  utensil: Utensil
}

export interface TeaPlan {
  id: number
  theme_id: number
  name: string
  date: string
  time_slot: string
  people_count: number
  budget: number
  photo_style: string
  theme_color: string
  tea_category: string
  status: string
  customer_name: string
  customer_phone: string
  total_price: number
  reservation_id?: number
  theme?: Theme
  recommended_items: RecommendedItem[]
}

export interface BorrowItem {
  id: number
  utensil_id: number
  quantity: number
  borrowed: boolean
  returned: boolean
  utensil: Utensil
}

export interface BorrowList {
  id: number
  plan_id: number
  borrow_date: string
  return_date: string
  status: string
  items: BorrowItem[]
}

export interface ReviewItem {
  id: number
  utensil_id: number
  damaged: boolean
  damage_description?: string
  cleaned: boolean
  utensil: Utensil
}

export interface ActivityReview {
  id: number
  plan_id: number
  review_date: string
  customer_feedback?: string
  rating: number
  is_repeat_customer: boolean
  items: ReviewItem[]
  plan: TeaPlan
}

export interface ThemeStats {
  theme_name: string
  count: number
}

export interface UtensilUsageStats {
  utensil_name: string
  category: string
  usage_count: number
}

export interface DamageStats {
  utensil_name: string
  category: string
  damage_count: number
  damage_rate: number
}

export interface PriceRangeStats {
  range: string
  count: number
}

export interface RepeatTypeStats {
  tea_type: string
  count: number
}

export interface StatisticsResponse {
  theme_stats: ThemeStats[]
  utensil_usage_stats: UtensilUsageStats[]
  damage_stats: DamageStats[]
  price_range_stats: PriceRangeStats[]
  repeat_type_stats: RepeatTypeStats[]
  color_reservation_stats: ColorReservationStats[]
  tea_category_reservation_stats: TeaCategoryReservationStats[]
  total_orders: number
  total_revenue: number
  avg_rating: number
  reservation_stats: ReservationStatsResponse
}

export interface ColorReservationStats {
  theme_color: string
  count: number
}

export interface TeaCategoryReservationStats {
  tea_category: string
  count: number
}

export interface RecommendationItem {
  utensil: Utensil
  quantity: number
  score: number
  category: string
}

export interface SelectedItem {
  utensil_id: number
  quantity: number
  selected: boolean
}

export interface Reservation {
  id: number
  customer_name: string
  customer_phone: string
  expected_date: string
  time_slot: string
  people_count: number
  budget: number
  preferred_color?: string
  preferred_tea?: string
  photo_style?: string
  remark?: string
  status: string
  plans: TeaPlan[]
}

export interface ConflictInfo {
  date: string
  time_slot: string
  type: string
  id: number
  name: string
  customer_name: string
}

export interface ConflictCheckResponse {
  has_conflict: boolean
  conflicts: ConflictInfo[]
}

export interface TimeSlotStats {
  time_slot: string
  count: number
}

export interface ReservationStatsResponse {
  conversion_rate: number
  total_reservations: number
  confirmed_reservations: number
  converted_plans: number
  cancelled_reservations: number
  time_slot_stats: TimeSlotStats[]
  popular_tea_stats: TeaCategoryReservationStats[]
  popular_color_stats: ColorReservationStats[]
}

export interface ScheduleOccupancyItem {
  id: string
  date: string
  time_slot: string
  source_type: string
  source_name: string
  customer_name: string
  business_type: string
  status: string
  related_id?: number
}

export interface ScheduleOccupancyDay {
  date: string
  has_conflict: boolean
  morning: ScheduleOccupancyItem[]
  afternoon: ScheduleOccupancyItem[]
  evening: ScheduleOccupancyItem[]
  full_day: ScheduleOccupancyItem[]
}

export interface ScheduleOccupancyResponse {
  start_date: string
  end_date: string
  total_occupied: number
  total_conflicts: number
  days: ScheduleOccupancyDay[]
}

export const TEA_CATEGORIES = ['绿茶', '红茶', '乌龙茶', '普洱茶', '白茶', '黄茶']
export const PHOTO_STYLES = ['宋韵古风', '禅意极简', '文人雅集', '现代新中式', '自然山野']
export const UTENSIL_CATEGORIES = ['盖碗', '茶海', '杯盏', '席布', '花器']
export const MATERIALS = ['青瓷', '白瓷', '紫砂', '朱泥', '玻璃', '粗陶', '棉麻', '竹编', '织锦', '铜器']
export const COLORS = ['朱红', '赭石', '胭脂', '琥珀', '金黄', '橙黄', '青色', '湖蓝', '黛绿', '松石', '月白', '藏青', '米白', '象牙', '玄黑', '紫砂', '灰墨', '素白']
export const PLAN_STATUS = ['draft', 'confirmed', 'borrowing', 'completed']
export const TIME_SLOTS = ['上午', '下午', '晚上', '全天']
export const RESERVATION_STATUS = ['pending', 'confirmed', 'cancelled', 'converted']
