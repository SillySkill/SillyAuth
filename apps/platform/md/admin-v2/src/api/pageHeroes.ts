import apiClient from './client';
import type { ApiResponse } from '@/types';

// ============================================================
// Types for page hero config (category='page_heroes')
// ============================================================

/** A single hero slide within a page carousel */
export interface PageHeroSlide {
  title?: string;
  subtitle?: string;
  description?: string;
  badge?: string;
  background_image?: string;
  type?: 'image' | 'video';
  src?: string;
}

/** Full page hero data – supports both single mode and slides mode */
export interface PageHeroData {
  title?: string;
  subtitle?: string;
  badge?: string;
  background_image?: string;
  description?: string;
  /** Array of slides for carousel mode */
  slides?: PageHeroSlide[];
  [key: string]: unknown;
}

// All page names that can have heroes
export const PAGE_HERO_NAMES = [
  'index',
  'downloads',
  'tutorials',
  'marketplace',
  'about',
  'community',
  'contact',
  'help',
  'pricing',
  'docs',
  'creation',
  'policy',
  'vendor_apply',
] as const;

export type PageHeroName = (typeof PAGE_HERO_NAMES)[number];

// Page labels for display in the UI
export const PAGE_HERO_LABELS: Record<PageHeroName, string> = {
  index: '首页',
  downloads: '下载中心',
  tutorials: '教程中心',
  marketplace: '供应商市场',
  about: '关于我们',
  community: '社区论坛',
  contact: '联系我们',
  help: '帮助中心',
  pricing: '定价方案',
  docs: '文档中心',
  creation: '创作中心',
  policy: '政策声明',
  vendor_apply: '供应商申请',
};

// ============================================================
// API helpers – unwrap config_data nested data
// ============================================================

interface ConfigDataWrapper {
  category?: string;
  name?: string;
  data?: unknown;
}

async function getPageHero<T = PageHeroData>(name: string): Promise<T> {
  try {
    const response = await apiClient.get<
      ApiResponse<ConfigDataWrapper> | ConfigDataWrapper
    >(`/config-data/item/page_heroes/${name}`);
    const wrapper = response.data;
    const raw: unknown =
      wrapper && (wrapper as ApiResponse<ConfigDataWrapper>).data !== undefined
        ? (wrapper as ApiResponse<ConfigDataWrapper>).data
        : wrapper;
    const inner: unknown =
      raw && typeof raw === 'object' && (raw as ConfigDataWrapper).data !== undefined
        ? (raw as ConfigDataWrapper).data
        : raw;
    return (inner as T) || ({} as T);
  } catch {
    // 404 means no record yet — return empty object so form shows defaults
    return {} as T;
  }
}

async function savePageHero(name: string, data: PageHeroData): Promise<void> {
  await apiClient.put(`/config-data/page_heroes/${name}`, { data });
}

// ============================================================
// Per-page getter/setter exports
// ============================================================

export const getDownloadsHero = () => getPageHero('downloads');
export const saveDownloadsHero = (data: PageHeroData) => savePageHero('downloads', data);

export const getTutorialsHero = () => getPageHero('tutorials');
export const saveTutorialsHero = (data: PageHeroData) => savePageHero('tutorials', data);

export const getMarketplaceHero = () => getPageHero('marketplace');
export const saveMarketplaceHero = (data: PageHeroData) => savePageHero('marketplace', data);

export const getAboutHero = () => getPageHero('about');
export const saveAboutHero = (data: PageHeroData) => savePageHero('about', data);

export const getCommunityHero = () => getPageHero('community');
export const saveCommunityHero = (data: PageHeroData) => savePageHero('community', data);

export const getContactHero = () => getPageHero('contact');
export const saveContactHero = (data: PageHeroData) => savePageHero('contact', data);

export const getHelpHero = () => getPageHero('help');
export const saveHelpHero = (data: PageHeroData) => savePageHero('help', data);

export const getPricingHero = () => getPageHero('pricing');
export const savePricingHero = (data: PageHeroData) => savePageHero('pricing', data);

export const getDocsHero = () => getPageHero('docs');
export const saveDocsHero = (data: PageHeroData) => savePageHero('docs', data);

export const getCreationHero = () => getPageHero('creation');
export const saveCreationHero = (data: PageHeroData) => savePageHero('creation', data);

export const getPolicyHero = () => getPageHero('policy');
export const savePolicyHero = (data: PageHeroData) => savePageHero('policy', data);

export const getVendorApplyHero = () => getPageHero('vendor_apply');
export const saveVendorApplyHero = (data: PageHeroData) => savePageHero('vendor_apply', data);

export const getIndexHero = () => getPageHero('index');
export const saveIndexHero = (data: PageHeroData) => savePageHero('index', data);
