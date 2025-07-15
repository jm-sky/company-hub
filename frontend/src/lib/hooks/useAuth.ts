import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../api';
import { User } from '@/types/api';

export const useAuth = () => {
  const queryClient = useQueryClient();

  const loginMutation = useMutation({
    mutationFn: ({ email, password }: { email: string; password: string }) =>
      apiClient.login(email, password),
    onSuccess: (data) => {
      apiClient.setAuth(data.data.token);
      queryClient.setQueryData(['user'], data.data.user);
    },
  });

  const registerMutation = useMutation({
    mutationFn: ({ email, password, name }: { email: string; password: string; name: string }) =>
      apiClient.register(email, password, name),
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
    enabled: !!localStorage.getItem('auth_token'),
  });
};