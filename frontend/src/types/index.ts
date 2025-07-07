// 历史数据类型
export interface HistoricalData {
  timestamp: string;
  temperature: number;
  usage: number;
  hour: number;
  day_of_week: number;
  week_of_month: number;
}

// 预测结果类型
export interface PredictionResult {
  hour: number;
  predicted_usage: number;
  confidence_interval: [number, number];
  original_prediction?: number;
}

// 天气信息类型
export interface WeatherInfo {
  date: string;
  day_of_week: string;
  max_temperature: string;
  special_note?: string;
}

// 特殊事件信息类型
export interface SpecialEventInfo {
  date: string;
  event_summary: string;
}

// 情景信息类型 (保持向后兼容)
export interface ContextInfo {
  date: string;
  day_of_week: string;
  temperature: number;
  demand_estimate: string;
  increase_percentage: string;
  reserve_rate: string | null;
  special_notes: string;
}

// 特征重要性类型
export interface FeatureImportance {
  feature: string;
  importance: number;
  description: string;
}

// SHAP值类型
export interface ShapValue {
  feature: string;
  value: number;
  base_value: number;
}

// 模型指标类型
export interface ModelMetrics {
  mae: number;
  rmse: number;
  r2_score: number;
  mape: number;
}

// 全局调整类型
export interface GlobalAdjustment {
  start_hour: number;
  end_hour: number;
  direction: 'increase' | 'decrease';
  percentage: number;
}

// 局部调整类型
export interface LocalAdjustment {
  hour: number;
  new_value: number;
}

// API响应类型
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message: string;
  timestamp: string;
}

// 数据质量类型
export interface DataQuality {
  quality_score: number;
  missing_values: number;
  outliers: number;
  completeness: number;
}

// 历史数据响应类型
export interface HistoricalDataResponse {
  historical_data: HistoricalData[];
  total_count: number;
  date_range: [string, string];
  data_quality: DataQuality;
}

// 预测响应类型
export interface PredictionResponse {
  predictions: PredictionResult[];
  model_metrics: ModelMetrics;
  target_date: string;
  confidence_level: number;
}

// 可解释性响应类型
export interface ExplanationResponse {
  feature_importance: FeatureImportance[];
  shap_values: ShapValue[];
  lime_explanation: any;
  prediction_value: number;
  base_value: number;
}

// 调整响应类型
export interface AdjustmentResponse {
  adjusted_predictions: PredictionResult[];
  adjustment_type: 'global' | 'local';
  adjustment_summary: {
    total_adjustments: number;
    average_change: number;
    affected_hours: number[];
  };
}

// 图表数据类型
export interface ChartDataPoint {
  x: number | string;
  y: number;
  label?: string;
  color?: string;
}

// 应用状态类型
export interface AppState {
  loading: boolean;
  error: string | null;
  historicalData: HistoricalData[];
  predictions: PredictionResult[];
  contextInfo: ContextInfo[];
  featureImportance: FeatureImportance[];
  shapValues: ShapValue[];
  modelMetrics: ModelMetrics | null;
  adjustmentHistory: AdjustmentResponse[];
}

// 组件Props类型
export interface ComponentProps {
  className?: string;
  children?: React.ReactNode;
}
