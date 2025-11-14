/**
 * 全局常量
 */

// 默认用户 ID（Demo）
export const DEFAULT_USER_ID = 'demo_user_001';

// 会话 ID 生成
export const generateSessionId = (): string => {
  return `session_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
};

// 消息 ID 生成
export const generateMessageId = (): string => {
  return `msg_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
};

// Artifact 类型常量
export const ARTIFACT_TYPES = {
  QUIZ_SET: 'quiz_set',
  EXPLANATION: 'explanation',
  LOADING: 'loading',
  ERROR: 'error',
} as const;

// Intent 类型常量
export const INTENT_TYPES = {
  QUIZ: 'quiz',
  EXPLAIN: 'explain',
  OTHER: 'other',
} as const;

// 时间格式化
export const formatTime = (date: Date): string => {
  return new Intl.DateTimeFormat('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
};

// 置信度等级
export const getConfidenceLevel = (confidence: number): 'high' | 'medium' | 'low' => {
  if (confidence >= 0.8) return 'high';
  if (confidence >= 0.5) return 'medium';
  return 'low';
};

// 置信度颜色
export const getConfidenceColor = (confidence: number): string => {
  const level = getConfidenceLevel(confidence);
  switch (level) {
    case 'high':
      return 'text-green-600';
    case 'medium':
      return 'text-yellow-600';
    case 'low':
      return 'text-red-600';
    default:
      return 'text-gray-600';
  }
};

