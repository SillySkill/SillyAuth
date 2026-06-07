import apiClient from './client';
import type { ApiResponse, PaginatedResponse } from '@/types';

// ---- Yicuiyuan Document Types ----

export interface YicuiyuanDocument {
  id: number;
  category: string;
  title: string;
  summary?: string;
  content?: string;
  file_url?: string;
  file_size?: number;
  sort_order: number;
  is_published: boolean;
  created_at: string;
}

export interface YicuiyuanDocumentCreateRequest {
  category: string;
  title: string;
  summary?: string;
  content?: string;
  file_url?: string;
  sort_order?: number;
  is_published?: boolean;
}

export interface YicuiyuanDocumentUpdateRequest {
  category?: string;
  title?: string;
  summary?: string;
  content?: string;
  file_url?: string;
  sort_order?: number;
  is_published?: boolean;
}

// ---- Yicuiyuan Feedback Types ----

export interface YicuiyuanFeedback {
  id: number;
  submitter_name: string;
  contact_info?: string;
  feedback_type: string;
  content: string;
  status: string;
  admin_reply?: string;
  replied_at?: string;
  replied_by_name?: string;
  created_at: string;
}

export interface YicuiyuanFeedbackUpdateRequest {
  status?: string;
  admin_reply?: string;
}

// ---- Yicuiyuan Event Types ----

export interface YicuiyuanEvent {
  id: number;
  title: string;
  description?: string;
  event_date: string;
  event_time?: string;
  location?: string;
  cover_image?: string;
  max_participants: number;
  status: string;
  registration_count?: number;
  sort_order: number;
  created_at: string;
}

export interface YicuiyuanEventCreateRequest {
  title: string;
  description?: string;
  event_date: string;
  event_time?: string;
  location?: string;
  cover_image?: string;
  max_participants?: number;
  status?: string;
  sort_order?: number;
}

export interface YicuiyuanEventUpdateRequest {
  title?: string;
  description?: string;
  event_date?: string;
  event_time?: string;
  location?: string;
  cover_image?: string;
  max_participants?: number;
  status?: string;
  sort_order?: number;
}

export interface YicuiyuanEventRegistration {
  id: number;
  event_id: number;
  registrant_name: string;
  contact_info?: string;
  num_participants: number;
  note?: string;
  status: string;
  created_at: string;
}

// ---- Documents API ----

export const getDocuments = async (params: {
  category?: string;
  search?: string;
  page?: number;
  page_size?: number;
} = {}): Promise<PaginatedResponse<YicuiyuanDocument>> => {
  const response = await apiClient.get<PaginatedResponse<YicuiyuanDocument>>('/community/yicuiyuan/documents', { params });
  return response.data;
};

export const getDocument = async (id: number): Promise<ApiResponse<YicuiyuanDocument>> => {
  const response = await apiClient.get<ApiResponse<YicuiyuanDocument>>(`/community/yicuiyuan/documents/${id}`);
  return response.data;
};

export const createDocument = async (data: YicuiyuanDocumentCreateRequest): Promise<ApiResponse<YicuiyuanDocument>> => {
  const response = await apiClient.post<ApiResponse<YicuiyuanDocument>>('/community/yicuiyuan/documents', data);
  return response.data;
};

export const updateDocument = async (id: number, data: YicuiyuanDocumentUpdateRequest): Promise<ApiResponse<YicuiyuanDocument>> => {
  const response = await apiClient.put<ApiResponse<YicuiyuanDocument>>(`/community/yicuiyuan/documents/${id}`, data);
  return response.data;
};

export const deleteDocument = async (id: number): Promise<ApiResponse<null>> => {
  const response = await apiClient.delete<ApiResponse<null>>(`/community/yicuiyuan/documents/${id}`);
  return response.data;
};

// ---- Feedback API ----

export const getFeedbacks = async (params: {
  status?: string;
  search?: string;
  page?: number;
  page_size?: number;
} = {}): Promise<PaginatedResponse<YicuiyuanFeedback>> => {
  const response = await apiClient.get<PaginatedResponse<YicuiyuanFeedback>>('/community/yicuiyuan/feedback', { params });
  return response.data;
};

export const updateFeedback = async (id: number, data: YicuiyuanFeedbackUpdateRequest): Promise<ApiResponse<YicuiyuanFeedback>> => {
  const response = await apiClient.put<ApiResponse<YicuiyuanFeedback>>(`/community/yicuiyuan/feedback/${id}`, data);
  return response.data;
};

// ---- Events API ----

export const getEvents = async (params: {
  status?: string;
  search?: string;
  page?: number;
  page_size?: number;
} = {}): Promise<PaginatedResponse<YicuiyuanEvent>> => {
  const response = await apiClient.get<PaginatedResponse<YicuiyuanEvent>>('/community/yicuiyuan/events', { params });
  return response.data;
};

export const getEvent = async (id: number): Promise<ApiResponse<YicuiyuanEvent>> => {
  const response = await apiClient.get<ApiResponse<YicuiyuanEvent>>(`/community/yicuiyuan/events/${id}`);
  return response.data;
};

export const createEvent = async (data: YicuiyuanEventCreateRequest): Promise<ApiResponse<YicuiyuanEvent>> => {
  const response = await apiClient.post<ApiResponse<YicuiyuanEvent>>('/community/yicuiyuan/events', data);
  return response.data;
};

export const updateEvent = async (id: number, data: YicuiyuanEventUpdateRequest): Promise<ApiResponse<YicuiyuanEvent>> => {
  const response = await apiClient.put<ApiResponse<YicuiyuanEvent>>(`/community/yicuiyuan/events/${id}`, data);
  return response.data;
};

export const deleteEvent = async (id: number): Promise<ApiResponse<null>> => {
  const response = await apiClient.delete<ApiResponse<null>>(`/community/yicuiyuan/events/${id}`);
  return response.data;
};

export const getEventRegistrations = async (eventId: number): Promise<ApiResponse<YicuiyuanEventRegistration[]>> => {
  const response = await apiClient.get<ApiResponse<YicuiyuanEventRegistration[]>>(`/community/yicuiyuan/events/${eventId}/registrations`);
  return response.data;
};
