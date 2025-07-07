// 模型可解释性相关的类型定义

export interface SHAPMetadata {
  date: string;
  description: string;
  features: string[];
  features_chinese: string[];
  base_prediction: number;
  total_hours: number;
}

export interface FeatureImportanceItem {
  feature: string;
  feature_chinese: string;
  importance: number;
  rank: number;
}

export interface TimeSeriesItem {
  hour: number;
  time: string;
  temperature: number;
  total_shap: number;
  shap_values: Record<string, number>;
}

export interface ContributionItem {
  feature: string;
  feature_chinese: string;
  shap_value: number;
}

export interface WaterfallItem {
  hour: number;
  time: string;
  base_value: number;
  final_prediction: number;
  contributions: ContributionItem[];
}

export interface SHAPData {
  metadata: SHAPMetadata;
  feature_importance: FeatureImportanceItem[];
  timeseries: TimeSeriesItem[];
  waterfall: WaterfallItem[];
}

// 业务影响描述
export interface BusinessImpact {
  text: string;
  icon: React.ReactNode;
}

// 影响强度等级
export type ImpactStrength = '强' | '中' | '弱';

// 影响类型
export type ImpactType = 'positive' | 'negative' | 'neutral';

// 建议类型
export interface Suggestion {
  type: 'warning' | 'info' | 'tip' | 'normal';
  text: string;
  icon: React.ReactNode;
}

// 时段分析结果
export interface HourAnalysis {
  hour: number;
  prediction: number;
  baseValue: number;
  totalAdjustment: number;
  mainFactors: {
    positive: ContributionItem[];
    negative: ContributionItem[];
  };
  suggestions: Suggestion[];
}

// 模式洞察
export interface PatternInsight {
  peakHour: TimeSeriesItem;
  lowHour: TimeSeriesItem;
  averageImpact: number;
  volatility: number;
  trendDescription: string;
}

// 特征解释映射
export interface FeatureExplanation {
  feature: string;
  positive: string;
  negative: string;
  icon: React.ReactNode;
  businessContext: string;
}

// 可解释性配置
export interface ExplanationConfig {
  showTechnicalDetails: boolean;
  selectedHour: number;
  impactThreshold: number;
  maxSuggestions: number;
}

// 导出的工具函数类型
export interface ExplanationUtils {
  getBusinessImpact: (feature: string, shapValue: number) => BusinessImpact;
  getImpactStrength: (shapValue: number) => ImpactStrength;
  getImpactColor: (shapValue: number) => string;
  generateSuggestions: (hourData: TimeSeriesItem, contributions: ContributionItem[]) => Suggestion[];
  analyzePattern: (timeseries: TimeSeriesItem[]) => PatternInsight;
}
