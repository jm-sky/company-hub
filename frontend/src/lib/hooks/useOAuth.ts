import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api';
import { ApiResponse, AuthResponse } from '@/types/api';

interface OAuthUrlResponse {
  auth_url: string;
  state: string;
}

export const useOAuthAuthUrl = () => {
  return useMutation<ApiResponse<OAuthUrlResponse>, Error, string>({
    mutationFn: async (provider: string) => {
      return await apiClient.getOAuthAuthUrl(provider);
    },
    onSuccess: (data) => {
      // Store state for CSRF protection
      if (typeof window !== 'undefined') {
        localStorage.setItem('oauth_state', data.data.state);
        // Redirect to OAuth provider
        window.location.href = data.data.auth_url;
      }
    },
    onError: (error) => {
      console.error('OAuth URL generation failed:', error);
    },
  });
};

export const useOAuthCallback = () => {
  const queryClient = useQueryClient();
  const router = useRouter();

  return useMutation<
    ApiResponse<AuthResponse>,
    Error,
    { provider: string; code: string; state: string; recaptchaToken?: string | null }
  >({
    mutationFn: async ({ provider, code, state, recaptchaToken }) => {
      // Verify state parameter for CSRF protection
      if (typeof window !== 'undefined') {
        const storedState = localStorage.getItem('oauth_state');
        
        if (!storedState || storedState !== state) {
          throw new Error('Invalid state parameter - possible CSRF attack');
        }
        
        localStorage.removeItem('oauth_state');
      }

      return await apiClient.oauthCallback(provider, code, state, recaptchaToken);
    },
    onSuccess: (data) => {
      if (data.success && data.data) {
        // Set authentication token
        apiClient.setAuth(data.data.token);
        
        // Update user data in cache
        queryClient.setQueryData(['user'], data.data.user);
        
        // Redirect to dashboard
        router.push('/dashboard');
      } else {
        router.push('/login?error=oauth-failed');
      }
    },
    onError: (error) => {
      console.error('OAuth callback failed:', error);
      // Redirect to login with error
      router.push('/login?error=oauth-failed');
    },
  });
};

export const useGitHubLogin = () => {
  const getAuthUrl = useOAuthAuthUrl();
  
  return {
    login: () => getAuthUrl.mutate('github'),
    isPending: getAuthUrl.isPending,
    error: getAuthUrl.error,
  };
};

export const useGoogleLogin = () => {
  const getAuthUrl = useOAuthAuthUrl();
  
  return {
    login: () => getAuthUrl.mutate('google'),
    isPending: getAuthUrl.isPending,
    error: getAuthUrl.error,
  };
};