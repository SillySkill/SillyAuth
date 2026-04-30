export interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
  error?: string;
  meta?: {
    page?: number;
    limit?: number;
    total?: number;
    totalPages?: number;
  };
}

export interface PaginationParams {
  page?: number;
  limit?: number;
}

export interface User {
  id: string;
  email: string;
  username: string;
  role: 'ADMIN' | 'EDITOR' | 'VIEWER';
  avatar?: string;
  status: 'ACTIVE' | 'INACTIVE' | 'BANNED';
  createdAt: string;
  updatedAt: string;
}

export interface Content {
  id: string;
  key: string;
  type: string;
  title: string;
  content: string;
  metadata?: any;
  language: string;
  status: 'DRAFT' | 'PUBLISHED' | 'ARCHIVED';
  seo?: any;
  createdAt: string;
  updatedAt: string;
}

export interface Navigation {
  id: string;
  title: string;
  key: string;
  url: string;
  icon?: string;
  parentId?: string | null;
  order: number;
  isActive: boolean;
  isNewWindow: boolean;
  language: string;
  createdAt: string;
  updatedAt: string;
  children?: Navigation[];
}

export interface Carousel {
  id: string;
  title: string;
  description?: string;
  mediaType: 'IMAGE' | 'VIDEO';
  mediaUrl: string;
  linkUrl?: string;
  linkTitle?: string;
  order: number;
  isActive: boolean;
  language: string;
  startDate?: string;
  endDate?: string;
  createdAt: string;
  updatedAt: string;
}

export interface Skill {
  id: string;
  name: string;
  category: string;
  level: number;
  icon?: string;
  description?: string;
  order: number;
  isActive: boolean;
  language: string;
  createdAt: string;
  updatedAt: string;
}

export interface Vendor {
  id: string;
  name: string;
  logo?: string;
  website?: string;
  description?: string;
  order: number;
  isActive: boolean;
  language: string;
  createdAt: string;
  updatedAt: string;
}
