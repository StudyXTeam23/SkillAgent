/**
 * useAgent - 与 Agent API 交互的自定义 Hook
 */
import { useState, useCallback } from 'react'
import { useChatDispatch, createMessage } from '../contexts/ChatContext'
import { agentApi } from '../api/client'

interface UseAgentReturn {
  sendMessage: (message: string) => Promise<void>
  isLoading: boolean
  error: string | null
}

export function useAgent(userId: string = 'demo-user', sessionId: string = 'demo-session'): UseAgentReturn {
  const dispatch = useChatDispatch()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const sendMessage = useCallback(async (messageText: string) => {
    if (!messageText.trim()) {
      return
    }

    try {
      // 1. 添加用户消息
      const userMessage = createMessage('user', messageText)
      dispatch({ type: 'ADD_MESSAGE', payload: userMessage })

      // 2. 设置加载状态
      setIsLoading(true)
      dispatch({ type: 'SET_LOADING', payload: true })
      setError(null)

      // 3. 调用 Agent API
      const response = await agentApi.chat({
        user_id: userId,
        session_id: sessionId,
        message: messageText,
      })

      // 4. 添加 Agent 响应消息
      const agentMessage = createMessage(
        'agent',
        response.content_type === 'error' 
          ? (response.response_content as any).message || '抱歉，发生了错误'
          : '已生成结果',
        {
          type: response.content_type as any,
          data: response.response_content,
        }
      )
      dispatch({ type: 'ADD_MESSAGE', payload: agentMessage })

    } catch (err: any) {
      console.error('Error sending message:', err)
      const errorMessage = err.message || '发送消息失败，请稍后再试'
      setError(errorMessage)
      dispatch({ type: 'SET_ERROR', payload: errorMessage })

      // 添加错误消息到聊天
      const errorMsg = createMessage('agent', errorMessage, {
        type: 'error',
        data: { message: errorMessage },
      })
      dispatch({ type: 'ADD_MESSAGE', payload: errorMsg })
    } finally {
      setIsLoading(false)
      dispatch({ type: 'SET_LOADING', payload: false })
    }
  }, [userId, sessionId, dispatch])

  return {
    sendMessage,
    isLoading,
    error,
  }
}

