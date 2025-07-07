import axios from 'axios';
import type {
  ApiResponse,
  HistoricalDataResponse,
  PredictionResponse,
  ExplanationResponse,
  AdjustmentResponse,
  ContextInfo,
  GlobalAdjustment,
  LocalAdjustment,
  ModelMetrics,
  UserData,
  UserExperimentData
} from '../types/index.js';

// API基础配置
const API_BASE_URL = 'http://localhost:8001/api/v1';

// 全局会话ID存储
let currentSessionId: string | null = null;

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 设置会话ID
export const setSessionId = (sessionId: string | null) => {
  currentSessionId = sessionId;
};

// 获取当前会话ID
export const getCurrentSessionId = () => currentSessionId;

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);

    // 自动添加会话ID到请求头
    if (currentSessionId && !config.headers['X-Session-Id']) {
      config.headers['X-Session-Id'] = currentSessionId;
    }

    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error);
    if (error.response) {
      // 服务器响应错误
      console.error('Error Data:', error.response.data);
      console.error('Error Status:', error.response.status);
    } else if (error.request) {
      // 请求发送失败
      console.error('Request Error:', error.request);
    } else {
      // 其他错误
      console.error('Error Message:', error.message);
    }
    return Promise.reject(error);
  }
);

// API服务类
export class ApiService {
  // 获取历史数据
  static async getHistoricalData(startDate?: string, endDate?: string): Promise<any> {
    const params: any = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;

    const response = await api.get('/data/historical', { params });
    return response.data;
  }

  // 获取情景信息
  static async getContextInfo(): Promise<ContextInfo[]> {
    const response = await api.get<ApiResponse<{ context_data: ContextInfo[] }>>('/data/context');
    return response.data.data.context_data;
  }

  // 获取数据摘要
  static async getDataSummary(): Promise<any> {
    const response = await api.get<ApiResponse<any>>('/data/summary');
    return response.data.data;
  }

  // 训练模型
  static async trainModel(
    targetDate: string = '2022-06-30',
    weeksBefore: number = 3,
    validationSplit: number = 0.2,
    forceRetrain: boolean = false
  ): Promise<any> {
    const response = await api.post<ApiResponse<any>>('/prediction/train', {
      target_date: targetDate,
      weeks_before: weeksBefore,
      validation_split: validationSplit,
      force_retrain: forceRetrain,
    });
    return response.data.data;
  }

  // 获取预测结果
  static async getPrediction(targetDate: string = '2022-06-30'): Promise<PredictionResponse> {
    const response = await api.get<ApiResponse<PredictionResponse>>('/prediction/predict', {
      params: {
        target_date: targetDate,
      },
    });
    return response.data.data;
  }

  // 获取单小时预测
  static async getHourlyPrediction(
    targetDatetime: string,
    temperature: number
  ): Promise<{ predicted_usage: number; confidence_interval: [number, number] }> {
    const response = await api.get<ApiResponse<any>>('/prediction/hourly', {
      params: {
        target_datetime: targetDatetime,
        temperature: temperature,
      },
    });
    return response.data.data;
  }

  // 获取模型指标
  static async getModelMetrics(): Promise<ModelMetrics> {
    const response = await api.get<ApiResponse<{ training_metrics: ModelMetrics }>>('/prediction/metrics');
    return response.data.data.training_metrics;
  }

  // 获取可解释性分析
  static async getExplanation(
    targetDate: string = '2022-06-30',
    hour: number = 14
  ): Promise<ExplanationResponse> {
    const response = await api.get<ApiResponse<ExplanationResponse>>('/explanation/analyze', {
      params: {
        target_date: targetDate,
        hour: hour,
      },
    });
    return response.data.data;
  }

  // 获取特征重要性
  static async getFeatureImportance(): Promise<any> {
    const response = await api.get<ApiResponse<any>>('/explanation/feature-importance');
    return response.data.data;
  }

  // 应用全局调整
  static async applyGlobalAdjustment(
    predictions: any[],
    adjustment: GlobalAdjustment
  ): Promise<AdjustmentResponse> {
    const response = await api.post<ApiResponse<AdjustmentResponse>>('/adjustment/global', {
      predictions: predictions,
      adjustment: adjustment,
    });
    return response.data.data;
  }

  // 应用局部调整
  static async applyLocalAdjustment(
    predictions: any[],
    adjustments: LocalAdjustment[]
  ): Promise<AdjustmentResponse> {
    const response = await api.post<ApiResponse<AdjustmentResponse>>('/adjustment/local', {
      predictions: predictions,
      adjustments: adjustments,
    });
    return response.data.data;
  }

  // 获取调整历史
  static async getAdjustmentHistory(): Promise<any> {
    const response = await api.get<ApiResponse<any>>('/adjustment/history');
    return response.data.data;
  }

  // 重置调整
  static async resetAdjustments(): Promise<any> {
    const response = await api.post<ApiResponse<any>>('/adjustment/reset');
    return response.data.data;
  }

  // 导出结果
  static async exportResults(format: string = 'csv'): Promise<Blob> {
    const response = await api.get('/export/results', {
      params: { format },
      responseType: 'blob',
    });
    return response.data;
  }

  // 健康检查
  static async healthCheck(): Promise<any> {
    const response = await api.get('http://localhost:8001/health');
    return response.data;
  }

  // ===== 用户管理相关API =====

  // 用户登录
  static async loginUser(username: string): Promise<any> {
    const response = await api.post<ApiResponse<any>>('/users/login', {
      username: username
    });

    // 自动设置会话ID
    if (response.data.data?.user_data?.session_id) {
      setSessionId(response.data.data.user_data.session_id);
    }

    // 转换字段名称从下划线到驼峰命名
    if (response.data.data?.user_data) {
      const userData = response.data.data.user_data;
      response.data.data.user_data = {
        userId: userData.user_id,
        username: userData.username,
        sessionId: userData.session_id,
        loginTime: userData.login_time
      };
    }

    return response.data.data;
  }

  // 获取会话信息
  static async getSessionInfo(): Promise<any> {
    const response = await api.get<ApiResponse<any>>('/users/session');
    return response.data.data;
  }

  // 更新会话活动
  static async updateSessionActivity(): Promise<any> {
    const response = await api.post<ApiResponse<any>>('/users/session/activity');
    return response.data.data;
  }

  // 用户登出
  static async logoutUser(): Promise<any> {
    const response = await api.post<ApiResponse<any>>('/users/logout');
    setSessionId(null); // 清除会话ID
    return response.data.data;
  }

  // 开始实验
  static async startExperiment(): Promise<UserExperimentData> {
    const response = await api.post<ApiResponse<UserExperimentData>>('/users/experiment/start');
    return response.data.data;
  }

  // 保存实验数据
  static async saveExperimentData(experimentData: UserExperimentData): Promise<any> {
    const response = await api.post<ApiResponse<any>>('/users/experiment/save', experimentData);
    return response.data.data;
  }

  // 完成实验
  static async completeExperiment(experimentData: UserExperimentData): Promise<any> {
    // 转换字段名称从驼峰命名到下划线
    const backendExperimentData = {
      user_id: experimentData.userId,
      username: experimentData.username,
      session_id: experimentData.sessionId,
      start_time: experimentData.startTime,
      decisions: experimentData.decisions.map(decision => ({
        id: decision.id,
        label: decision.label,
        reason: decision.reason,
        status: decision.status,
        adjustments: decision.adjustments.map(adj => ({
          id: adj.id,
          hour: adj.hour,
          original_value: adj.originalValue,
          adjusted_value: adj.adjustedValue,
          timestamp: adj.timestamp,
          decision_id: adj.decisionId
        })),
        created_at: decision.createdAt,
        completed_at: decision.completedAt
      })),
      adjustments: experimentData.adjustments.map(adj => ({
        id: adj.id,
        hour: adj.hour,
        original_value: adj.originalValue,
        adjusted_value: adj.adjustedValue,
        timestamp: adj.timestamp,
        decision_id: adj.decisionId
      })),
      interactions: experimentData.interactions.map(interaction => ({
        id: interaction.id,
        type: interaction.type,
        component: interaction.component,
        action: interaction.action,
        timestamp: interaction.timestamp,
        duration: interaction.duration,
        metadata: interaction.metadata
      })),
      completion_time: experimentData.completionTime,
      status: experimentData.status
    };

    const response = await api.post<ApiResponse<any>>('/users/experiment/complete', {
      experiment_data: backendExperimentData
    });
    return response.data.data;
  }

  // 获取实验数据
  static async getExperimentData(): Promise<UserExperimentData | null> {
    const response = await api.get<ApiResponse<UserExperimentData | null>>('/users/experiment/data');
    return response.data.data;
  }

  // 获取模型拟合历史
  static async getModelFittingHistory(startDate?: string, endDate?: string): Promise<any> {
    const params: any = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;

    const response = await api.get('/prediction/model-fitting-history', { params });
    return response.data;
  }

  // 滑动窗口训练模型
  static async trainSlidingWindowModels(
    startDate: string,
    endDate: string,
    weekseBefore: number = 3,
    forceRetrain: boolean = false
  ): Promise<any> {
    const response = await api.post('/prediction/train-sliding-window', {
      start_date: startDate,
      end_date: endDate,
      weeks_before: weekseBefore,
      force_retrain: forceRetrain
    });
    return response.data;
  }

  // 获取预训练模型数据
  static async getPretrainedModels(startDate?: string, endDate?: string): Promise<any> {
    const params: any = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;

    const response = await api.get('/prediction/pretrained-models', { params });
    return response.data;
  }
}

export default ApiService;
