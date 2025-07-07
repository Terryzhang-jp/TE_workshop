import React from 'react';
import { 
  Thermometer, 
  Clock, 
  Calendar, 
  BarChart3, 
  Info,
  AlertCircle,
  Target,
  TrendingUp,
  TrendingDown
} from 'lucide-react';
import type { 
  BusinessImpact, 
  ImpactStrength, 
  Suggestion, 
  PatternInsight,
  TimeSeriesItem,
  ContributionItem,
  FeatureExplanation
} from '../types/explanation';

// 特征解释映射
const FEATURE_EXPLANATIONS: Record<string, FeatureExplanation> = {
  'Temperature': {
    feature: 'Temperature',
    positive: '高温增加了制冷需求，推高用电量',
    negative: '低温减少了制冷需求，降低用电量',
    icon: React.createElement(Thermometer, { className: "w-4 h-4" }),
    businessContext: '温度是影响电力需求的关键因素，特别是在夏季和冬季'
  },
  'Hour': {
    feature: 'Hour',
    positive: '当前时段为用电高峰期，需求较大',
    negative: '当前时段为用电低谷期，需求较小',
    icon: React.createElement(Clock, { className: "w-4 h-4" }),
    businessContext: '一天中不同时段的用电模式反映了人们的生活和工作规律'
  },
  'Day_of_Week': {
    feature: 'Day_of_Week',
    positive: '工作日用电需求通常高于周末',
    negative: '周末用电需求通常低于工作日',
    icon: React.createElement(Calendar, { className: "w-4 h-4" }),
    businessContext: '工作日与周末的用电模式差异反映了商业活动的影响'
  },
  'Week_of_Month': {
    feature: 'Week_of_Month',
    positive: '月中时段商业活动活跃，用电需求较高',
    negative: '月初/月末商业活动相对较少，用电需求较低',
    icon: React.createElement(BarChart3, { className: "w-4 h-4" }),
    businessContext: '月内不同周次的用电差异可能与商业周期相关'
  }
};

/**
 * 获取特征的业务影响描述
 */
export const getBusinessImpact = (feature: string, shapValue: number): BusinessImpact => {
  const explanation = FEATURE_EXPLANATIONS[feature];
  
  if (!explanation) {
    return { 
      text: '影响因素', 
      icon: React.createElement(Info, { className: "w-4 h-4" })
    };
  }

  return {
    text: shapValue > 0 ? explanation.positive : explanation.negative,
    icon: explanation.icon
  };
};

/**
 * 获取影响强度描述
 */
export const getImpactStrength = (shapValue: number): ImpactStrength => {
  const absValue = Math.abs(shapValue);
  if (absValue > 200) return '强';
  if (absValue > 100) return '中';
  return '弱';
};

/**
 * 获取影响颜色样式
 */
export const getImpactColor = (shapValue: number): string => {
  if (shapValue > 0) return 'text-red-600 bg-red-50 border-red-200';
  return 'text-blue-600 bg-blue-50 border-blue-200';
};

/**
 * 生成智能建议
 */
export const generateSuggestions = (
  hourData: TimeSeriesItem, 
  contributions: ContributionItem[],
  selectedHour: number
): Suggestion[] => {
  const suggestions: Suggestion[] = [];
  
  // 基于总体影响的建议
  if (hourData.total_shap > 100) {
    suggestions.push({
      type: 'warning',
      text: `当前时段(${selectedHour}:00)用电需求较高，建议提前准备充足的电力供应。`,
      icon: React.createElement(AlertCircle, { className: "w-4 h-4 text-orange-500" })
    });
  } else if (hourData.total_shap < -100) {
    suggestions.push({
      type: 'info',
      text: `当前时段(${selectedHour}:00)用电需求较低，可考虑调整发电计划以提高效率。`,
      icon: React.createElement(Info, { className: "w-4 h-4 text-blue-500" })
    });
  }
  
  // 基于主要影响因素的建议
  const topFactor = contributions[0];
  if (topFactor) {
    if (topFactor.feature === 'Temperature' && Math.abs(topFactor.shap_value) > 50) {
      suggestions.push({
        type: 'tip',
        text: '温度是当前主要影响因素，建议密切关注天气变化对用电需求的影响。',
        icon: React.createElement(Thermometer, { className: "w-4 h-4 text-red-500" })
      });
    }
    
    if (topFactor.feature === 'Hour' && Math.abs(topFactor.shap_value) > 100) {
      const isHighDemand = topFactor.shap_value > 0;
      suggestions.push({
        type: isHighDemand ? 'warning' : 'info',
        text: isHighDemand 
          ? '当前处于用电高峰时段，建议加强电网监控和负荷管理。'
          : '当前处于用电低谷时段，可考虑安排设备维护或储能充电。',
        icon: React.createElement(Clock, { className: `w-4 h-4 ${isHighDemand ? 'text-orange-500' : 'text-blue-500'}` })
      });
    }
  }
  
  // 如果没有特殊建议，提供默认建议
  if (suggestions.length === 0) {
    suggestions.push({
      type: 'normal',
      text: '当前时段各影响因素相对平衡，预测结果较为稳定。',
      icon: React.createElement(Target, { className: "w-4 h-4 text-green-500" })
    });
  }
  
  return suggestions;
};

/**
 * 分析时间模式
 */
export const analyzePattern = (timeseries: TimeSeriesItem[]): PatternInsight => {
  const peakHour = timeseries.reduce((max, hour) => 
    hour.total_shap > max.total_shap ? hour : max
  );
  
  const lowHour = timeseries.reduce((min, hour) => 
    hour.total_shap < min.total_shap ? hour : min
  );
  
  const totalImpacts = timeseries.map(h => h.total_shap);
  const averageImpact = totalImpacts.reduce((sum, impact) => sum + impact, 0) / totalImpacts.length;
  
  // 计算波动性（标准差）
  const variance = totalImpacts.reduce((sum, impact) => 
    sum + Math.pow(impact - averageImpact, 2), 0
  ) / totalImpacts.length;
  const volatility = Math.sqrt(variance);
  
  // 生成趋势描述
  let trendDescription = '';
  if (volatility > 150) {
    trendDescription = '全天用电需求波动较大，需要灵活的调度策略';
  } else if (volatility > 75) {
    trendDescription = '全天用电需求有一定波动，属于正常范围';
  } else {
    trendDescription = '全天用电需求相对稳定，便于预测和调度';
  }
  
  return {
    peakHour,
    lowHour,
    averageImpact,
    volatility,
    trendDescription
  };
};

/**
 * 格式化SHAP值显示
 */
export const formatShapValue = (value: number): string => {
  const sign = value > 0 ? '+' : '';
  return `${sign}${value.toFixed(0)} MW`;
};

/**
 * 获取时段描述
 */
export const getHourDescription = (hour: number): string => {
  if (hour >= 6 && hour < 9) return '早高峰';
  if (hour >= 9 && hour < 12) return '上午';
  if (hour >= 12 && hour < 14) return '午间';
  if (hour >= 14 && hour < 18) return '下午';
  if (hour >= 18 && hour < 21) return '晚高峰';
  if (hour >= 21 && hour < 24) return '夜间';
  return '深夜';
};

/**
 * 获取影响因素的重要性等级
 */
export const getImportanceLevel = (rank: number, totalFeatures: number): string => {
  const ratio = rank / totalFeatures;
  if (ratio <= 0.25) return '核心';
  if (ratio <= 0.5) return '重要';
  if (ratio <= 0.75) return '一般';
  return '次要';
};

/**
 * 计算置信度指示器
 */
export const calculateConfidence = (shapValues: ContributionItem[]): {
  level: 'high' | 'medium' | 'low';
  score: number;
  description: string;
} => {
  // 基于SHAP值的分布计算置信度
  const totalAbsImpact = shapValues.reduce((sum, item) => sum + Math.abs(item.shap_value), 0);
  const maxImpact = Math.max(...shapValues.map(item => Math.abs(item.shap_value)));
  
  // 如果主要因素占主导地位，置信度较高
  const dominanceRatio = maxImpact / totalAbsImpact;
  
  let level: 'high' | 'medium' | 'low';
  let description: string;
  
  if (dominanceRatio > 0.6) {
    level = 'high';
    description = '主要影响因素明确，预测置信度高';
  } else if (dominanceRatio > 0.4) {
    level = 'medium';
    description = '影响因素相对均衡，预测置信度中等';
  } else {
    level = 'low';
    description = '多因素共同影响，预测不确定性较高';
  }
  
  const score = Math.round(dominanceRatio * 100);
  
  return { level, score, description };
};
