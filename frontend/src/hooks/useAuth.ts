import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/router';
import { authApi, LoginCredentials, RegisterData } from '@/lib/api';
import { queryKeys } from '@/lib/queryClient';
import toast from 'react-hot-toast';

export function useAuth() {
  const router = useRouter();
  const queryClient = useQueryClient();

  // Get current user
  const { data: user, isLoading } = useQuery({
    queryKey: queryKeys.currentUser,
    queryFn: authApi.getCurrentUser,
    retry: false,
    enabled: typeof window !== 'undefined',
  });

  // Login mutation
  const loginMutation = useMutation({
    mutationFn: (credentials: LoginCredentials) => authApi.login(credentials),
    onSuccess: (data) => {
      queryClient.setQueryData(queryKeys.currentUser, data.user);
      toast.success(`Welcome back, ${data.user.name}!`);
      router.push('/dashboard');
    },
  });

  // Register mutation
  const registerMutation = useMutation({
    mutationFn: (data: RegisterData) => authApi.register(data),
    onSuccess: (data) => {
      queryClient.setQueryData(queryKeys.currentUser, data.user);
      toast.success(`Welcome, ${data.user.name}!`);
      router.push('/dashboard');
    },
  });

  // Logout mutation
  const logoutMutation = useMutation({
    mutationFn: authApi.logout,
    onSuccess: () => {
      queryClient.clear();
      toast.success('Logged out successfully');
    },
  });

  return {
    user,
    isLoading,
    isAuthenticated: !!user,
    login: loginMutation.mutate,
    register: registerMutation.mutate,
    logout: logoutMutation.mutate,
    isLoggingIn: loginMutation.isPending,
    isRegistering: registerMutation.isPending,
    isLoggingOut: logoutMutation.isPending,
  };
}
