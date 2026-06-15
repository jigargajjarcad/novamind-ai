import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import chatService from '../services/chatService'

export function useChatSessions() {
  return useQuery({
    queryKey: ['chat-sessions'],
    queryFn: chatService.listSessions,
  })
}

export function useChatSession(sessionId) {
  return useQuery({
    queryKey: ['chat-session', sessionId],
    queryFn: () => chatService.getSession(sessionId),
    enabled: !!sessionId,
  })
}

export function useCreateSession() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data) => chatService.createSession(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chat-sessions'] })
    },
  })
}

export function useDeleteSession() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (sessionId) => chatService.deleteSession(sessionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chat-sessions'] })
    },
  })
}
