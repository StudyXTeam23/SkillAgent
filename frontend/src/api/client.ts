/**
 * API 客户端
 * 
 * 统一的 HTTP 请求封装
 */
import axios, { AxiosError } from 'axios';
import type { AxiosInstance } from 'axios';
import type { AgentChatRequest, AgentChatResponse, APIError } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000, // 30 seconds
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // 请求拦截器
    this.client.interceptors.request.use(
      (config) => {
        console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('❌ Request Error:', error);
        return Promise.reject(error);
      }
    );

    // 响应拦截器
    this.client.interceptors.response.use(
      (response) => {
        console.log(`✅ API Response: ${response.status} ${response.config.url}`);
        return response;
      },
      (error: AxiosError<APIError>) => {
        console.error('❌ Response Error:', error.response?.data || error.message);
        return Promise.reject(this.handleError(error));
      }
    );
  }

  private handleError(error: AxiosError<APIError>): Error {
    if (error.response) {
      // 服务器返回错误
      const message = error.response.data?.detail || error.message;
      return new Error(`API Error: ${message}`);
    } else if (error.request) {
      // 请求发送但没有响应
      return new Error('No response from server. Please check your connection.');
    } else {
      // 其他错误
      return new Error(`Request failed: ${error.message}`);
    }
  }

  /**
   * 健康检查
   */
  async healthCheck(): Promise<{ status: string; message: string }> {
    const response = await this.client.get('/health');
    return response.data;
  }

  /**
   * 发送聊天消息
   */
  async sendMessage(request: AgentChatRequest): Promise<AgentChatResponse> {
    const response = await this.client.post<AgentChatResponse>('/api/agent/chat', request);
    return response.data;
  }
}

// 导出单例
export const apiClient = new APIClient();

// 导出便捷的 API 方法
export const agentApi = {
  chat: (request: AgentChatRequest) => apiClient.sendMessage(request),
  health: () => apiClient.healthCheck(),
};

