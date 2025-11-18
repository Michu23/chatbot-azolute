export interface User {
  id: number;
  email: string;
  full_name?: string;
  is_active: boolean;
  is_verified: boolean;
  is_superuser: boolean;
  created_at: string;
  last_login?: string;
}

export interface Organization {
  id: number;
  name: string;
  slug: string;
  owner_id: number;
  website_domain?: string;
  primary_color: string;
  logo_url?: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface Bot {
  id: number;
  bot_id: string;
  organization_id: number;
  name: string;
  personality: 'friendly' | 'professional' | 'sales_focused' | 'custom';
  custom_persona?: string;
  welcome_message: string;
  offline_message: string;
  primary_color: string;
  button_color: string;
  chat_bubble_color: string;
  theme_mode: string;
  profile_image_url?: string;
  position: 'left' | 'right';
  visibility: 'both' | 'mobile' | 'desktop';
  model_name: string;
  temperature: number;
  max_tokens: number;
  system_prompt?: string;
  lead_capture_enabled: boolean;
  quick_suggestions_enabled: boolean;
  quick_suggestions?: string;
  n8n_webhook_url?: string;
  send_lead_webhook: boolean;
  is_active: boolean;
  is_online: boolean;
  created_at: string;
  updated_at?: string;
}

export interface ChatSession {
  id: number;
  session_id: string;
  bot_id: number;
  visitor_id?: string;
  visitor_name?: string;
  visitor_email?: string;
  visitor_phone?: string;
  source_url?: string;
  source_page_title?: string;
  user_agent?: string;
  ip_address?: string;
  country?: string;
  city?: string;
  status: 'active' | 'resolved' | 'archived';
  is_lead: boolean;
  created_at: string;
  updated_at?: string;
  last_message_at?: string;
  messages?: ChatMessage[];
}

export interface ChatMessage {
  id: number;
  session_id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  token_count?: number;
  model_used?: string;
  response_time_ms?: number;
  used_rag: boolean;
  source_documents?: string;
  created_at: string;
}

export interface Lead {
  id: number;
  session_id: number;
  name?: string;
  email?: string;
  phone?: string;
  company?: string;
  message?: string;
  tags?: string;
  custom_fields?: string;
  source_url?: string;
  source_page?: string;
  utm_source?: string;
  utm_medium?: string;
  utm_campaign?: string;
  is_qualified: boolean;
  is_contacted: boolean;
  webhook_sent: boolean;
  created_at: string;
  updated_at?: string;
}

export interface KnowledgeSource {
  id: number;
  bot_id: number;
  source_type: 'url' | 'pdf' | 'text' | 'faq';
  name: string;
  url?: string;
  file_path?: string;
  content?: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  error_message?: string;
  total_chunks: number;
  last_crawled_at?: string;
  created_at: string;
  updated_at?: string;
}

export interface DashboardStats {
  total_conversations: number;
  total_users: number;
  total_messages: number;
  leads_collected: number;
  avg_response_time_ms: number;
  model_usage: Record<string, number>;
}

export interface DashboardAnalytics {
  stats: DashboardStats;
  conversation_trends: Array<{
    date: string;
    count: number;
  }>;
  top_pages: Array<{
    url: string;
    count: number;
  }>;
  recent_leads: number;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}
