/**
 * ChatContext - 聊天状态管理
 * 
 * 使用 useReducer 管理聊天消息、加载状态和错误
 */
import React, { createContext, useContext, useReducer } from 'react'
import type { ReactNode } from 'react'

// ============= Types =============

export interface Message {
  id: string
  role: 'user' | 'agent'
  content: string
  timestamp: Date
  artifact?: {
    type: 'quiz_set' | 'explanation' | 'error'
    data: any
  }
}

interface ChatState {
  messages: Message[]
  isLoading: boolean
  error: string | null
}

type ChatAction =
  | { type: 'ADD_MESSAGE'; payload: Message }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'CLEAR_MESSAGES' }

// ============= Initial State =============

const initialState: ChatState = {
  messages: [],
  isLoading: false,
  error: null,
}

// ============= Reducer =============

function chatReducer(state: ChatState, action: ChatAction): ChatState {
  switch (action.type) {
    case 'ADD_MESSAGE':
      return {
        ...state,
        messages: [...state.messages, action.payload],
        error: null,
      }
    
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
      }
    
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
        isLoading: false,
      }
    
    case 'CLEAR_MESSAGES':
      return {
        ...state,
        messages: [],
        error: null,
      }
    
    default:
      return state
  }
}

// ============= Context =============

const ChatStateContext = createContext<ChatState | undefined>(undefined)
const ChatDispatchContext = createContext<React.Dispatch<ChatAction> | undefined>(undefined)

// ============= Provider =============

interface ChatProviderProps {
  children: ReactNode
}

export function ChatProvider({ children }: ChatProviderProps) {
  const [state, dispatch] = useReducer(chatReducer, initialState)

  return (
    <ChatStateContext.Provider value={state}>
      <ChatDispatchContext.Provider value={dispatch}>
        {children}
      </ChatDispatchContext.Provider>
    </ChatStateContext.Provider>
  )
}

// ============= Custom Hooks =============

export function useChat(): ChatState {
  const context = useContext(ChatStateContext)
  if (context === undefined) {
    throw new Error('useChat must be used within a ChatProvider')
  }
  return context
}

export function useChatDispatch(): React.Dispatch<ChatAction> {
  const context = useContext(ChatDispatchContext)
  if (context === undefined) {
    throw new Error('useChatDispatch must be used within a ChatProvider')
  }
  return context
}

// ============= Helper Functions =============

export function createMessage(
  role: 'user' | 'agent',
  content: string,
  artifact?: Message['artifact']
): Message {
  return {
    id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    role,
    content,
    timestamp: new Date(),
    artifact,
  }
}

