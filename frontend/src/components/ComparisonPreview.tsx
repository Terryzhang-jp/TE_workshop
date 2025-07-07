import React from 'react';
import PredictionComparison from './PredictionComparison';

// 模拟用户预测数据用于测试
const mockUserPredictions = [
  { hour: 0, predicted_usage: 3600, isAdjusted: false },
  { hour: 1, predicted_usage: 3500, isAdjusted: false },
  { hour: 2, predicted_usage: 3400, isAdjusted: false },
  { hour: 3, predicted_usage: 3500, isAdjusted: true },
  { hour: 4, predicted_usage: 3800, isAdjusted: true },
  { hour: 5, predicted_usage: 4300, isAdjusted: false },
  { hour: 6, predicted_usage: 4700, isAdjusted: false },
  { hour: 7, predicted_usage: 5200, isAdjusted: true },
  { hour: 8, predicted_usage: 5300, isAdjusted: false },
  { hour: 9, predicted_usage: 5100, isAdjusted: false },
  { hour: 10, predicted_usage: 4900, isAdjusted: true },
  { hour: 11, predicted_usage: 4600, isAdjusted: false },
  { hour: 12, predicted_usage: 4500, isAdjusted: false },
  { hour: 13, predicted_usage: 4400, isAdjusted: false },
  { hour: 14, predicted_usage: 4500, isAdjusted: true },
  { hour: 15, predicted_usage: 4800, isAdjusted: false },
  { hour: 16, predicted_usage: 4900, isAdjusted: false },
  { hour: 17, predicted_usage: 4900, isAdjusted: true },
  { hour: 18, predicted_usage: 4800, isAdjusted: false },
  { hour: 19, predicted_usage: 4700, isAdjusted: false },
  { hour: 20, predicted_usage: 4500, isAdjusted: true },
  { hour: 21, predicted_usage: 4200, isAdjusted: false },
  { hour: 22, predicted_usage: 4000, isAdjusted: false },
  { hour: 23, predicted_usage: 3700, isAdjusted: false }
];

const ComparisonPreview: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Enhanced Prediction Comparison Preview
          </h1>
          <p className="text-lg text-gray-600">
            New visualization features for comparing user predictions with real data
          </p>
        </div>
        
        <PredictionComparison 
          userPredictions={mockUserPredictions}
          className="max-w-none"
        />
      </div>
    </div>
  );
};

export default ComparisonPreview;
