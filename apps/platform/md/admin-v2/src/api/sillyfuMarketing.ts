import apiClient from './client';
import type { ApiResponse } from '@/types';

// ============================================================
// Config types for category='sillyfu'
// ============================================================

// ---- Product (name='product') ----

export interface GalleryImage {
  src: string;
  alt: string;
}

export interface ShowcaseSection {
  title: string;
  desc: string;
  image: string;
  features: string[];
}

export interface AgentConfig {
  name: string;
  color: string;
  color_hex: string;
  version: string;
  tech_stack: string;
  strength: string;
  good_at: string;
}

export interface ModeItem {
  name: string;
  desc: string;
  icon: string;
  color: string;
}

export interface CollabIssue {
  icon: string;
  issue: string;
  desc: string;
}

export interface QualityDimension {
  icon: string;
  title: string;
  desc: string;
  effect: string;
}

export interface SecurityDimension {
  icon: string;
  title: string;
  desc: string;
  effect: string;
}

export interface SecurityItem {
  type: string;
  desc: string;
  action: string;
}

export interface ColorSystemItem {
  mode: string;
  color: string;
  border: string;
  indicator: string;
}

export interface UseCase {
  scene: string;
  mode: string;
  mode_icon: string;
  desc: string;
}

export interface TechSpec {
  label: string;
  value: string;
}

export interface ProductPhoto {
  src: string;
  alt: string;
  caption: string;
}

export interface SillyFuProductData {
  name?: string;
  subtitle?: string;
  description?: string;
  ai_system?: string;
  capacity_range?: string;
  speed?: string;
  interface?: string;
  dimensions?: string;
  material?: string;
  colors?: string;
  warranty?: string;
  compatible?: string;
  serial?: string;
  production_count?: string;
  images?: GalleryImage[];
  showcase?: ShowcaseSection;
  agents?: { openclaw?: AgentConfig; hermes?: AgentConfig };
  modes?: ModeItem[];
  why_collab?: CollabIssue[];
  quality_dimensions?: QualityDimension[];
  security_dimensions?: SecurityDimension[];
  security_items?: SecurityItem[];
  color_system?: ColorSystemItem[];
  use_cases?: UseCase[];
  tech_specs?: TechSpec[];
  photos?: ProductPhoto[];
  [key: string]: unknown;
}

// ---- Variants (name='variants') ----

export interface VariantItem {
  capacity: string;
  color: string;
  price: string;
  badge?: string;
  tags?: string[];
}

// ---- OpenClaw (name='openclaw') ----

export interface AIFeature {
  icon: string;
  title: string;
  desc: string;
}

export interface SillyFuOpenClawData {
  store_name?: string;
  subtitle?: string;
  hero_video?: string;
  hero_poster?: string;
  ai_features?: AIFeature[];
  [key: string]: unknown;
}

// ============================================================
// API helpers – unwrap config_data nested data
// ============================================================

interface ConfigDataWrapper {
  category?: string;
  name?: string;
  data?: unknown;
}

async function getConfigData<T>(name: string): Promise<T> {
  const response = await apiClient.get<
    ApiResponse<ConfigDataWrapper> | ConfigDataWrapper
  >(`/config-data/item/sillyfu/${name}`);
  const wrapper = response.data;
  // Response interceptor normalizes to {success, data}, so actual data is at .data
  // But the config item itself wraps content in `.data`, so it's .data.data
  const raw: unknown =
    (wrapper && (wrapper as ApiResponse<ConfigDataWrapper>).data !== undefined)
      ? (wrapper as ApiResponse<ConfigDataWrapper>).data
      : wrapper;
  const inner: unknown =
    raw && typeof raw === 'object' && (raw as ConfigDataWrapper).data !== undefined
      ? (raw as ConfigDataWrapper).data
      : raw;
  return inner as T;
}

async function putConfigData(name: string, data: unknown): Promise<void> {
  await apiClient.put(`/config-data/sillyfu/${name}`, { data });
}

// ============================================================
// Product
// ============================================================

export const getSillyFuProduct = async (): Promise<SillyFuProductData> => {
  return getConfigData<SillyFuProductData>('product');
};

export const saveSillyFuProduct = async (
  data: SillyFuProductData
): Promise<void> => {
  return putConfigData('product', data);
};

// ============================================================
// Variants
// ============================================================

export const getSillyFuVariants = async (): Promise<VariantItem[]> => {
  return getConfigData<VariantItem[]>('variants');
};

export const saveSillyFuVariants = async (
  data: VariantItem[]
): Promise<void> => {
  return putConfigData('variants', data);
};

// ============================================================
// OpenClaw config
// ============================================================

export const getSillyFuOpenClaw = async (): Promise<SillyFuOpenClawData> => {
  return getConfigData<SillyFuOpenClawData>('openclaw');
};

export const saveSillyFuOpenClaw = async (
  data: SillyFuOpenClawData
): Promise<void> => {
  return putConfigData('openclaw', data);
};
