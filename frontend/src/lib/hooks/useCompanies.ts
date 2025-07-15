import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../api';

export const useCompany = (nip: string) => {
  return useQuery({
    queryKey: ['company', nip],
    queryFn: async () => {
      const response = await apiClient.getCompany(nip);
      return response.data;
    },
    enabled: !!nip,
  });
};

export const useCompanyRefresh = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (nip: string) => apiClient.getCompany(nip, true),
    onSuccess: (data, nip) => {
      queryClient.setQueryData(['company', nip], data.data);
    },
  });
};

export const useCompanySearch = (query: string, page: number = 1, limit: number = 20) => {
  return useQuery({
    queryKey: ['companies', 'search', query, page, limit],
    queryFn: async () => {
      const response = await apiClient.searchCompanies(query, page, limit);
      return response.data;
    },
    enabled: !!query && query.length > 2,
  });
};