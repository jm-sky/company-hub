import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../api';

export const useAuth = () => {
  const queryClient = useQueryClient();

  const loginMutation = useMutation({
    mutationFn: ({ email, password, recaptchaToken }: { email: string; password: string; recaptchaToken?: string | null }) =>
      apiClient.login(email, password, recaptchaToken),
    onSuccess: (data) => {
      apiClient.setAuth(data.data.token);
      queryClient.setQueryData(['user'], data.data.user);
    },
  });

  const registerMutation = useMutation({
    mutationFn: ({ email, password, name, recaptchaToken }: { email: string; password: string; name: string; recaptchaToken?: string | null }) =>
      apiClient.register(email, password, name, recaptchaToken),
    onSuccess: (data) => {
      apiClient.setAuth(data.data.token);
      queryClient.setQueryData(['user'], data.data.user);
    },
  });

  const forgotPasswordMutation = useMutation({
    mutationFn: (email: string) => apiClient.forgotPassword(email),
  });

  const resetPasswordMutation = useMutation({
    mutationFn: ({ token, password }: { token: string; password: string }) =>
      apiClient.resetPassword(token, password),
  });

  const changePasswordMutation = useMutation({
    mutationFn: ({ currentPassword, newPassword }: { currentPassword: string; newPassword: string }) =>
      apiClient.changePassword(currentPassword, newPassword),
  });

  const logout = () => {
    apiClient.clearAuth();
    queryClient.clear();
  };

  return {
    login: loginMutation,
    register: registerMutation,
    forgotPassword: forgotPasswordMutation,
    resetPassword: resetPasswordMutation,
    changePassword: changePasswordMutation,
    logout,
  };
};

export const useUser = () => {
  return useQuery({
    queryKey: ['user'],
    queryFn: async () => {
      const response = await apiClient.getProfile();
      return response.data;
    },
    enabled: typeof window !== 'undefined' && !!localStorage.getItem('auth_token'),
    staleTime: 15 * 60 * 1000, // 15 minutes - consider data fresh for 15 minutes
    gcTime: 30 * 60 * 1000, // 30 minutes - keep in cache for 30 minutes
    refetchOnWindowFocus: false, // Don't refetch when window gains focus
    refetchOnMount: false, // Don't refetch on component mount if data exists and is fresh
    refetchOnReconnect: false, // Don't refetch when network reconnects
  });
};
