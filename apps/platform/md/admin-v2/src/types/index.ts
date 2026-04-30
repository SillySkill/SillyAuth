// ============================================================
// SillyMD Admin v2 - Type Definitions
// ============================================================

// ---- Generic API Response Types ----

export interface PaginatedResponse<T> {
  success: boolean;
  data: {
    items: T[];
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
  };
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
}

// ---- Auth Types ----

export interface User {
  id: number;
  username: string;
  email: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  success: boolean;
  data: {
    token: string;
    user: User;
  };
}

// ---- Query Parameter Types ----

export interface PaginationParams {
  page?: number;
  page_size?: number;
  search?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

// ---- Article / Content Types ----

export interface Article {
  id: number;
  title: string;
  slug: string;
  content: string;
  excerpt?: string;
  category_id?: number;
  category?: Category;
  author_id?: number;
  author?: User;
  tags?: string[];
  cover_image?: string;
  status: 'draft' | 'published' | 'archived';
  view_count: number;
  like_count: number;
  is_featured: boolean;
  created_at: string;
  updated_at: string;
  published_at?: string;
}

export interface ArticleCreateRequest {
  title: string;
  slug?: string;
  content: string;
  excerpt?: string;
  category_id?: number;
  tags?: string[];
  cover_image?: string;
  status?: 'draft' | 'published';
  is_featured?: boolean;
}

export interface ArticleUpdateRequest extends Partial<ArticleCreateRequest> {}

export interface ArticleListParams extends PaginationParams {
  status?: string;
  category_id?: number;
  is_featured?: boolean;
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  description?: string;
  parent_id?: number;
  article_count?: number;
  sort_order: number;
  created_at: string;
}

// ---- Skill Types ----

export interface Skill {
  id: number;
  name: string;
  slug: string;
  description: string;
  icon?: string;
  category?: string;
  difficulty_level: 'beginner' | 'intermediate' | 'advanced';
  sort_order: number;
  is_active: boolean;
  article_count?: number;
  tutorial_count?: number;
  created_at: string;
  updated_at: string;
}

export interface SkillCreateRequest {
  name: string;
  slug?: string;
  description: string;
  icon?: string;
  category?: string;
  difficulty_level?: string;
  sort_order?: number;
  is_active?: boolean;
}

export interface SkillUpdateRequest extends Partial<SkillCreateRequest> {}

export interface SkillListParams extends PaginationParams {
  difficulty_level?: string;
  is_active?: boolean;
}

// ---- Vendor Types ----

export interface Vendor {
  id: number;
  name: string;
  slug: string;
  description: string;
  logo?: string;
  website?: string;
  category?: string;
  contact_email?: string;
  contact_phone?: string;
  is_active: boolean;
  is_verified: boolean;
  sort_order: number;
  created_at: string;
  updated_at: string;
}

export interface VendorCreateRequest {
  name: string;
  slug?: string;
  description: string;
  logo?: string;
  website?: string;
  category?: string;
  contact_email?: string;
  contact_phone?: string;
  is_active?: boolean;
  is_verified?: boolean;
  sort_order?: number;
}

export interface VendorUpdateRequest extends Partial<VendorCreateRequest> {}

export interface VendorListParams extends PaginationParams {
  category?: string;
  is_active?: boolean;
  is_verified?: boolean;
}

// ---- Tutorial Types ----

export interface Tutorial {
  id: number;
  title: string;
  slug: string;
  description: string;
  content: string;
  skill_id?: number;
  skill?: Skill;
  author_id?: number;
  difficulty_level: 'beginner' | 'intermediate' | 'advanced';
  duration_minutes?: number;
  video_url?: string;
  cover_image?: string;
  status: 'draft' | 'published' | 'archived';
  view_count: number;
  sort_order: number;
  created_at: string;
  updated_at: string;
}

export interface TutorialCreateRequest {
  title: string;
  slug?: string;
  description: string;
  content: string;
  skill_id?: number;
  difficulty_level?: string;
  duration_minutes?: number;
  video_url?: string;
  cover_image?: string;
  status?: 'draft' | 'published';
  sort_order?: number;
}

export interface TutorialUpdateRequest extends Partial<TutorialCreateRequest> {}

export interface TutorialListParams extends PaginationParams {
  status?: string;
  skill_id?: number;
  difficulty_level?: string;
}

// ---- Download Types ----

export interface Download {
  id: number;
  title: string;
  slug: string;
  description: string;
  file_url: string;
  file_size?: number;
  file_type?: string;
  version?: string;
  category?: string;
  platform?: string;
  download_count: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface DownloadCreateRequest {
  title: string;
  slug?: string;
  description: string;
  file_url: string;
  file_size?: number;
  file_type?: string;
  version?: string;
  category?: string;
  platform?: string;
  is_active?: boolean;
}

export interface DownloadUpdateRequest extends Partial<DownloadCreateRequest> {}

export interface DownloadListParams extends PaginationParams {
  category?: string;
  platform?: string;
  is_active?: boolean;
}

// ---- Payment Account Types ----

export interface PaymentAccount {
  id: number;
  user_id: number;
  user?: User;
  account_type: 'alipay' | 'wechat' | 'bank' | 'paypal';
  account_name: string;
  account_number: string;
  is_verified: boolean;
  is_default: boolean;
  created_at: string;
  updated_at: string;
}

export interface PaymentAccountCreateRequest {
  user_id: number;
  account_type: string;
  account_name: string;
  account_number: string;
  is_verified?: boolean;
  is_default?: boolean;
}

export interface PaymentAccountUpdateRequest extends Partial<PaymentAccountCreateRequest> {}

// ---- Creator Earning Types ----

export interface CreatorEarning {
  id: number;
  user_id: number;
  user?: User;
  amount: number;
  currency: string;
  earning_type: 'article' | 'tutorial' | 'skill' | 'download' | 'referral';
  reference_id?: number;
  status: 'pending' | 'settled' | 'cancelled';
  settled_at?: string;
  description?: string;
  created_at: string;
}

export interface CreatorEarningListParams extends PaginationParams {
  user_id?: number;
  earning_type?: string;
  status?: string;
  date_from?: string;
  date_to?: string;
}

export interface RevenueStats {
  total_revenue: number;
  total_settled: number;
  total_pending: number;
  period_revenue: { date: string; amount: number }[];
  revenue_by_type: { type: string; amount: number }[];
}

export interface SettleRequest {
  amount: number;
  note?: string;
}

// ---- Commission Types ----

export interface CommissionRecord {
  id: number;
  user_id: number;
  user?: User;
  order_id?: number;
  amount: number;
  rate: number;
  description?: string;
  status: 'pending' | 'approved' | 'rejected';
  created_at: string;
  updated_at: string;
}

export interface CommissionListParams extends PaginationParams {
  user_id?: number;
  status?: string;
  date_from?: string;
  date_to?: string;
}

export interface CommissionStats {
  total_commission: number;
  total_pending: number;
  total_approved: number;
  total_rejected: number;
  average_rate: number;
}

// ---- Points Types ----

export interface PointsProduct {
  id: number;
  name: string;
  description: string;
  image_url?: string;
  points_required: number;
  stock: number;
  category_id?: number;
  category?: PointsCategory;
  exchange_count: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface PointsProductCreateRequest {
  name: string;
  description: string;
  image_url?: string;
  points_required: number;
  stock: number;
  category_id?: number;
  is_active?: boolean;
}

export interface PointsProductUpdateRequest extends Partial<PointsProductCreateRequest> {}

export interface PointsCategory {
  id: number;
  name: string;
  description?: string;
  sort_order: number;
  created_at: string;
}

export interface PointsExchange {
  id: number;
  user_id: number;
  user?: User;
  product_id: number;
  product?: PointsProduct;
  points_spent: number;
  status: 'pending' | 'completed' | 'cancelled';
  ship_to?: string;
  tracking_number?: string;
  created_at: string;
  updated_at: string;
}

export interface ExchangeListParams extends PaginationParams {
  user_id?: number;
  product_id?: number;
  status?: string;
}

// ---- Order Types ----

export interface Order {
  id: number;
  user_id: number;
  user?: User;
  order_number: string;
  total_amount: number;
  currency: string;
  status: 'pending' | 'paid' | 'completed' | 'cancelled' | 'refunded';
  payment_method?: string;
  items?: OrderItem[];
  created_at: string;
  updated_at: string;
  paid_at?: string;
}

export interface OrderItem {
  id: number;
  order_id: number;
  product_id: number;
  product_name: string;
  quantity: number;
  unit_price: number;
  total_price: number;
}

// ---- Navigation Types ----

export interface NavigationItem {
  id: number;
  title: string;
  url: string;
  icon?: string;
  parent_id?: number;
  children?: NavigationItem[];
  sort_order: number;
  is_active: boolean;
  target?: '_self' | '_blank';
}

export interface Navigation {
  items: NavigationItem[];
}

export interface NavigationUpdateRequest {
  items: Omit<NavigationItem, 'id'>[];
}

// ---- SEO Types ----

export interface SEOConfig {
  id: number;
  page: string;
  title: string;
  description: string;
  keywords: string;
  og_title?: string;
  og_description?: string;
  og_image?: string;
  canonical_url?: string;
  updated_at: string;
}

export interface SEOConfigUpdateRequest {
  title?: string;
  description?: string;
  keywords?: string;
  og_title?: string;
  og_description?: string;
  og_image?: string;
  canonical_url?: string;
}

// ---- i18n Types ----

export interface I18nTranslation {
  id: number;
  locale: string;
  namespace: string;
  key: string;
  value: string;
  created_at: string;
  updated_at: string;
}

export interface TranslationCreateRequest {
  locale: string;
  namespace: string;
  key: string;
  value: string;
}

export interface TranslationUpdateRequest {
  value?: string;
  namespace?: string;
  key?: string;
}

export interface TranslationListParams extends PaginationParams {
  locale?: string;
  namespace?: string;
}

// ---- Module Types ----

export interface ModuleInfo {
  id: number;
  name: string;
  key: string;
  description: string;
  is_enabled: boolean;
  version?: string;
  installed_at: string;
}

// ---- Dashboard Types ----

export interface DashboardStats {
  total_users: number;
  total_articles: number;
  total_skills: number;
  total_tutorials: number;
  total_downloads: number;
  total_revenue: number;
  active_users_today: number;
  new_users_today: number;
}

export interface DashboardOverview {
  stats: DashboardStats;
  revenue_trend: { date: string; amount: number }[];
  user_growth: { date: string; count: number }[];
  content_distribution: { type: string; count: number }[];
  top_articles: Article[];
  top_creators: { user: User; earnings: number }[];
}

export interface RecentActivity {
  id: number;
  action: string;
  description: string;
  user_id?: number;
  user?: User;
  target_type?: string;
  target_id?: number;
  created_at: string;
}
