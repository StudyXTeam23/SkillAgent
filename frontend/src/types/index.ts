/**
 * TypeScript 类型定义
 * 
 * 与后端 Pydantic 模型对应
 */

// ============= Intent Types =============

export interface MemorySummary {
  topic_hint?: string | null;
  user_mastery_hint?: string | null;
  recent_behavior: string;
}

export interface IntentResult {
  intent: string | string[];
  topic?: string | null;
  target_artifact?: string | null;
  confidence: number;
  raw_text: string;
}

// ============= Memory Types =============

export interface UserLearningProfile {
  user_id: string;
  mastery: Record<string, string>; // { topic: "weak" | "medium" | "strong" }
  preferences: Record<string, string>;
  history: {
    quiz_sessions: number;
    homework_help_count: number;
    topics_visited: string[];
  };
  updated_at: string;
}

export interface SessionContext {
  session_id: string;
  current_topic?: string | null;
  recent_intents: string[];
  last_artifact?: string | null;
  last_user_message: string;
  updated_at: string;
}

// ============= Skill Types =============

export interface SkillDefinition {
  id: string;
  display_name: string;
  version: string;
  intent_tags: string[];
  input_schema: Record<string, any>;
  output_schema: Record<string, any>;
  models: {
    primary: string;
    fallback?: string;
  };
  context: Record<string, any>;
  cost: Record<string, any>;
  composable: boolean;
  dependencies: string[];
}

// ============= Artifact Types =============

export interface Artifact {
  type: string;
  payload: Record<string, any>;
  meta: Record<string, any>;
}

export interface Question {
  id: string;
  stem: string;
  options: string[];
  answer: string;
  explanation: string;
}

export interface QuizSetArtifact {
  type: 'quiz_set';
  title: string;
  questions: Question[];
  meta: Record<string, any>;
}

export interface Example {
  problem: string;
  solution: string;
  steps: string[];
}

export interface ExplanationArtifact {
  type: 'explanation';
  title: string;
  content: string;
  formula?: string | null;
  examples: Example[];
  meta: Record<string, any>;
}

// ============= API Types =============

export interface AgentChatRequest {
  user_id: string;
  session_id: string;
  message: string;
}

export interface AgentChatResponse {
  user_id: string;
  session_id: string;
  response_content: Record<string, any>;
  content_type: string; // 'quiz_set' | 'explanation' | 'error' 等
  intent: string;
  skill_id: string;
  processing_time_ms: number;
}

// ============= UI State Types =============

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  artifact?: Artifact;
  intent?: IntentResult;
  timestamp: Date;
  isLoading?: boolean;
  error?: string;
}

export interface ChatState {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  sessionId: string;
  userId: string;
}

export type ChatAction =
  | { type: 'ADD_USER_MESSAGE'; payload: string }
  | { type: 'ADD_ASSISTANT_MESSAGE'; payload: { artifact: Artifact; intent: IntentResult } }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'UPDATE_LAST_MESSAGE'; payload: Partial<Message> }
  | { type: 'RESET_CHAT' };

// ============= API Error Types =============

export interface APIError {
  detail: string;
  status: number;
}

