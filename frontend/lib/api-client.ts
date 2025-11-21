import api from './api';
import type {
  User,
  Bot,
  ChatSession,
  Lead,
  KnowledgeSource,
  DashboardAnalytics,
  Organization,
  AuthResponse,
} from '@/types';

// Auth API
export const authApi = {
  signup: async (data: { email: string; password: string; full_name?: string }) => {
    const response = await api.post<AuthResponse>('/auth/signup', data);
    return response.data;
  },

  login: async (data: { email: string; password: string }) => {
    const response = await api.post<AuthResponse>('/auth/login', data);
    return response.data;
  },

  refresh: async (refreshToken: string) => {
    const response = await api.post<AuthResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    });
    return response.data;
  },

  requestPasswordReset: async (email: string) => {
    const response = await api.post('/auth/request-password-reset', { email });
    return response.data;
  },

  resetPassword: async (token: string, newPassword: string) => {
    const response = await api.post('/auth/reset-password', {
      token,
      new_password: newPassword,
    });
    return response.data;
  },
};

// Users API
export const usersApi = {
  getMe: async () => {
    const response = await api.get<User>('/users/me');
    return response.data;
  },

  updateMe: async (data: Partial<User>) => {
    const response = await api.patch<User>('/users/me', data);
    return response.data;
  },
};

// Organizations API
export const organizationsApi = {
  list: async () => {
    const response = await api.get<Organization[]>('/organizations/');
    return response.data;
  },

  get: async (id: number) => {
    const response = await api.get<Organization>(`/organizations/${id}`);
    return response.data;
  },

  update: async (id: number, data: Partial<Organization>) => {
    const response = await api.patch<Organization>(`/organizations/${id}`, data);
    return response.data;
  },

  completeOnboarding: async (data: any) => {
    const response = await api.post('/organizations/onboarding', data);
    return response.data;
  },
};

// Bots API
export const botsApi = {
  list: async () => {
    const response = await api.get<{ bots: Bot[]; total: number }>('/bots/');
    return response.data;
  },

  get: async (botId: string) => {
    const response = await api.get<Bot>(`/bots/${botId}`);
    return response.data;
  },

  update: async (botId: string, data: Partial<Bot>) => {
    const response = await api.patch<Bot>(`/bots/${botId}`, data);
    return response.data;
  },

  getWidgetCode: async (botId: string) => {
    const response = await api.get(`/bots/${botId}/widget-code`);
    return response.data;
  },
};

// Chat API
export const chatApi = {
  listSessions: async (params?: { skip?: number; limit?: number; bot_id?: string }) => {
    const response = await api.get<ChatSession[]>('/chat/sessions', { params });
    return response.data;
  },

  getSession: async (sessionId: string) => {
    const response = await api.get<ChatSession>(`/chat/sessions/${sessionId}`);
    return response.data;
  },

  updateSession: async (sessionId: string, data: Partial<ChatSession>) => {
    const response = await api.patch<ChatSession>(`/chat/sessions/${sessionId}`, data);
    return response.data;
  },
};

// Leads API
export const leadsApi = {
  list: async (params?: { skip?: number; limit?: number }) => {
    const response = await api.get<{ leads: Lead[]; total: number }>('/leads/', {
      params,
    });
    return response.data;
  },

  get: async (leadId: number) => {
    const response = await api.get<Lead>(`/leads/${leadId}`);
    return response.data;
  },

  update: async (leadId: number, data: Partial<Lead>) => {
    const response = await api.patch<Lead>(`/leads/${leadId}`, data);
    return response.data;
  },

  exportCSV: async () => {
    const response = await api.get('/leads/export/csv', {
      responseType: 'blob',
    });
    return response.data;
  },
};

// Knowledge API
export const knowledgeApi = {
  listByBot: async (botId: number) => {
    const response = await api.get<{ sources: KnowledgeSource[]; total: number }>(
      `/knowledge/bot/${botId}`
    );
    return response.data;
  },

  create: async (data: {
    bot_id: number;
    source_type: string;
    name: string;
    url?: string;
    content?: string;
  }) => {
    const response = await api.post<KnowledgeSource>('/knowledge/', data);
    return response.data;
  },

  delete: async (sourceId: number) => {
    const response = await api.delete(`/knowledge/${sourceId}`);
    return response.data;
  },

  reindex: async (sourceId: number) => {
    const response = await api.post(`/knowledge/${sourceId}/reindex`);
    return response.data;
  },

  uploadPDF: async (botId: number, file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post<KnowledgeSource>(
      `/knowledge/upload-pdf?bot_id=${botId}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },
};

// Dashboard API
export const dashboardApi = {
  getStats: async (params?: { days?: number; bot_id?: string }) => {
    const response = await api.get<DashboardAnalytics>('/dashboard/stats', {
      params,
    });
    return response.data;
  },
};
