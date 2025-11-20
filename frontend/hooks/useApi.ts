import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  authApi,
  usersApi,
  botsApi,
  chatApi,
  leadsApi,
  knowledgeApi,
  dashboardApi,
  organizationsApi,
} from '@/lib/api-client';
import toast from 'react-hot-toast';

// Auth hooks
export const useLogin = () => {
  return useMutation({
    mutationFn: authApi.login,
    onSuccess: (data) => {
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      localStorage.setItem('user', JSON.stringify(data.user));
    },
  });
};

export const useSignup = () => {
  return useMutation({
    mutationFn: authApi.signup,
    onSuccess: (data) => {
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      localStorage.setItem('user', JSON.stringify(data.user));
    },
  });
};

// User hooks
export const useCurrentUser = () => {
  return useQuery({
    queryKey: ['currentUser'],
    queryFn: usersApi.getMe,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useUpdateUser = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: usersApi.updateMe,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['currentUser'] });
      toast.success('Profile updated successfully');
    },
    onError: () => {
      toast.error('Failed to update profile');
    },
  });
};

// Bot hooks
export const useBots = () => {
  return useQuery({
    queryKey: ['bots'],
    queryFn: botsApi.list,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
};

export const useBot = (botId: string) => {
  return useQuery({
    queryKey: ['bot', botId],
    queryFn: () => botsApi.get(botId),
    enabled: !!botId,
    staleTime: 2 * 60 * 1000,
  });
};

export const useUpdateBot = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ botId, data }: { botId: string; data: any }) =>
      botsApi.update(botId, data),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['bots'] });
      queryClient.invalidateQueries({ queryKey: ['bot', variables.botId] });
      toast.success('Bot updated successfully');
    },
    onError: () => {
      toast.error('Failed to update bot');
    },
  });
};

// Chat hooks
export const useSessions = (params?: any) => {
  return useQuery({
    queryKey: ['sessions', params],
    queryFn: () => chatApi.listSessions(params),
    staleTime: 30 * 1000, // 30 seconds
  });
};

export const useSession = (sessionId: string) => {
  return useQuery({
    queryKey: ['session', sessionId],
    queryFn: () => chatApi.getSession(sessionId),
    enabled: !!sessionId,
  });
};

// Lead hooks
export const useLeads = (params?: any) => {
  return useQuery({
    queryKey: ['leads', params],
    queryFn: () => leadsApi.list(params),
    staleTime: 60 * 1000, // 1 minute
  });
};

export const useUpdateLead = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ leadId, data }: { leadId: number; data: any }) =>
      leadsApi.update(leadId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leads'] });
      toast.success('Lead updated successfully');
    },
    onError: () => {
      toast.error('Failed to update lead');
    },
  });
};

export const useExportLeads = () => {
  return useMutation({
    mutationFn: leadsApi.exportCSV,
    onSuccess: (data) => {
      const url = window.URL.createObjectURL(new Blob([data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `leads_${new Date().toISOString().split('T')[0]}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('Leads exported successfully');
    },
    onError: () => {
      toast.error('Failed to export leads');
    },
  });
};

// Knowledge hooks
export const useKnowledgeSources = (botId: number) => {
  return useQuery({
    queryKey: ['knowledge', botId],
    queryFn: () => knowledgeApi.listByBot(botId),
    enabled: !!botId,
    staleTime: 2 * 60 * 1000,
  });
};

export const useCreateKnowledgeSource = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: knowledgeApi.create,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['knowledge', data.bot_id] });
      toast.success('Knowledge source added successfully');
    },
    onError: () => {
      toast.error('Failed to add knowledge source');
    },
  });
};

export const useDeleteKnowledgeSource = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: knowledgeApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['knowledge'] });
      toast.success('Knowledge source deleted');
    },
    onError: () => {
      toast.error('Failed to delete knowledge source');
    },
  });
};

// Dashboard hooks
export const useDashboardStats = (params?: any) => {
  return useQuery({
    queryKey: ['dashboard', params],
    queryFn: () => dashboardApi.getStats(params),
    staleTime: 60 * 1000, // 1 minute
    refetchInterval: 5 * 60 * 1000, // Auto-refresh every 5 minutes
  });
};

// Onboarding hook
export const useCompleteOnboarding = () => {
  return useMutation({
    mutationFn: organizationsApi.completeOnboarding,
    onError: () => {
      toast.error('Failed to complete onboarding');
    },
  });
};
