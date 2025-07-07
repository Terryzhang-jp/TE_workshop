import React, { useState, useEffect } from 'react';
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  LineChart, Line, Cell, PieChart, Pie, RadialBarChart, RadialBar
} from 'recharts';
import { TrendingUp, TrendingDown, Target, AlertCircle, Award, Zap } from 'lucide-react';
import realData from '../data/realData2022Jan7.json';

interface ComparisonData {
  hour: number;
  predicted_value: number;
  actual_value: number;
  difference: number;
  percentage_error: number;
  is_adjusted: boolean;
}

interface PredictionComparisonProps {
  userPredictions: any[]; // 用户的预测调整数据
  className?: string;
}

const PredictionComparison: React.FC<PredictionComparisonProps> = ({ 
  userPredictions, 
  className = '' 
}) => {
  const [comparisonData, setComparisonData] = useState<ComparisonData[]>([]);
  const [summary, setSummary] = useState({
    totalError: 0,
    averageError: 0,
    adjustedHours: 0,
    bestHour: { hour: 0, error: 0 },
    worstHour: { hour: 0, error: 0 },
    accuracy: 0,
    errorDistribution: { excellent: 0, good: 0, fair: 0, poor: 0 }
  });
  const [heatmapData, setHeatmapData] = useState<any[]>([]);

  useEffect(() => {
    calculateComparison();
  }, [userPredictions]);

  const calculateComparison = () => {
    const comparison: ComparisonData[] = [];
    const heatmap: any[] = [];
    let totalError = 0;
    let adjustedCount = 0;
    let bestError = Infinity;
    let worstError = 0;
    let bestHour = 0;
    let worstHour = 0;
    let errorDistribution = { excellent: 0, good: 0, fair: 0, poor: 0 };

    // 为每个小时创建对比数据
    for (let hour = 0; hour < 24; hour++) {
      const realHourData = realData.data.find(d => d.hour === hour);
      const userHourData = userPredictions.find(d => d.hour === hour);
      
      if (realHourData && userHourData) {
        const predictedValue = userHourData.predicted_usage || userHourData.current_prediction || 0;
        const actualValue = realHourData.actual_usage;
        const difference = predictedValue - actualValue;
        const percentageError = Math.abs(difference / actualValue) * 100;
        const isAdjusted = userHourData.isAdjusted || false;

        comparison.push({
          hour,
          predicted_value: predictedValue,
          actual_value: actualValue,
          difference,
          percentage_error: percentageError,
          is_adjusted: isAdjusted
        });

        totalError += Math.abs(difference);
        if (isAdjusted) adjustedCount++;

        // 误差分类
        if (percentageError <= 5) errorDistribution.excellent++;
        else if (percentageError <= 10) errorDistribution.good++;
        else if (percentageError <= 20) errorDistribution.fair++;
        else errorDistribution.poor++;

        // 热力图数据
        heatmap.push({
          hour,
          error: Math.abs(difference),
          errorPercent: percentageError,
          intensity: Math.min(percentageError / 30, 1) // 归一化到0-1
        });

        if (Math.abs(difference) < bestError) {
          bestError = Math.abs(difference);
          bestHour = hour;
        }
        if (Math.abs(difference) > worstError) {
          worstError = Math.abs(difference);
          worstHour = hour;
        }
      }
    }

    const accuracy = Math.max(0, 100 - (totalError / 24 / 5000) * 100); // 基于平均误差计算准确度

    setComparisonData(comparison);
    setHeatmapData(heatmap);
    setSummary({
      totalError,
      averageError: totalError / 24,
      adjustedHours: adjustedCount,
      bestHour: { hour: bestHour, error: bestError },
      worstHour: { hour: worstHour, error: worstError },
      accuracy: Math.round(accuracy),
      errorDistribution
    });
  };

  const formatValue = (value: number) => {
    return Math.round(value).toLocaleString();
  };

  const formatPercentage = (value: number) => {
    return `${value.toFixed(1)}%`;
  };

  const getHeatmapColor = (intensity: number) => {
    // 从绿色(准确)到红色(误差大)的渐变
    const red = Math.round(255 * intensity);
    const green = Math.round(255 * (1 - intensity));
    return `rgb(${red}, ${green}, 50)`;
  };

  const getAccuracyColor = (accuracy: number) => {
    if (accuracy >= 90) return '#10b981'; // 绿色
    if (accuracy >= 80) return '#f59e0b'; // 黄色
    if (accuracy >= 70) return '#f97316'; // 橙色
    return '#ef4444'; // 红色
  };

  return (
    <div className={`bg-white rounded-lg shadow-lg p-6 ${className}`}>
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-2 flex items-center">
          <Target className="mr-2 text-blue-600" size={24} />
          Prediction vs Reality Comparison
        </h2>
        <p className="text-gray-600">
          Your predictions compared to actual electricity usage on January 7, 2022
        </p>
      </div>

      {/* 准确度仪表盘 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* 整体准确度 */}
        <div className="bg-gradient-to-br from-blue-50 to-indigo-100 p-6 rounded-xl">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-800">Overall Accuracy</h3>
            <Award className="text-indigo-600" size={24} />
          </div>
          <div className="relative w-32 h-32 mx-auto">
            <svg className="w-32 h-32 transform -rotate-90" viewBox="0 0 36 36">
              <path
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                fill="none"
                stroke="#e5e7eb"
                strokeWidth="3"
              />
              <path
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                fill="none"
                stroke={getAccuracyColor(summary.accuracy)}
                strokeWidth="3"
                strokeDasharray={`${summary.accuracy}, 100`}
                strokeLinecap="round"
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-2xl font-bold" style={{ color: getAccuracyColor(summary.accuracy) }}>
                {summary.accuracy}%
              </span>
            </div>
          </div>
        </div>

        {/* 误差分布 */}
        <div className="bg-gradient-to-br from-green-50 to-emerald-100 p-6 rounded-xl">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-800">Error Distribution</h3>
            <Zap className="text-emerald-600" size={24} />
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Excellent (&le;5%)</span>
              <span className="font-semibold text-green-600">{summary.errorDistribution.excellent}h</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Good (&le;10%)</span>
              <span className="font-semibold text-blue-600">{summary.errorDistribution.good}h</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Fair (&le;20%)</span>
              <span className="font-semibold text-yellow-600">{summary.errorDistribution.fair}h</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Poor (&gt;20%)</span>
              <span className="font-semibold text-red-600">{summary.errorDistribution.poor}h</span>
            </div>
          </div>
        </div>

        {/* 关键统计 */}
        <div className="bg-gradient-to-br from-purple-50 to-violet-100 p-6 rounded-xl">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-800">Key Stats</h3>
            <Target className="text-violet-600" size={24} />
          </div>
          <div className="space-y-3">
            <div>
              <div className="text-sm text-gray-600">Average Error</div>
              <div className="text-xl font-bold text-violet-800">
                {formatValue(summary.averageError)} MW
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Adjustments Made</div>
              <div className="text-xl font-bold text-violet-800">
                {summary.adjustedHours} / 24 hours
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Best Hour</div>
              <div className="text-lg font-bold text-violet-800">
                {summary.bestHour.hour}:00 ({formatValue(summary.bestHour.error)} MW)
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 差距面积图 */}
      <div className="mb-8">
        <h3 className="text-xl font-semibold text-gray-800 mb-4">Prediction vs Reality Gap Analysis</h3>
        <div className="h-96 bg-white rounded-lg border border-gray-200 p-4">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={comparisonData}>
              <defs>
                <linearGradient id="overPrediction" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0.1}/>
                </linearGradient>
                <linearGradient id="underPrediction" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0.1}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
              <XAxis
                dataKey="hour"
                tickFormatter={(value) => `${value}:00`}
                stroke="#6b7280"
              />
              <YAxis
                tickFormatter={(value) => `${(value/1000).toFixed(1)}k MW`}
                stroke="#6b7280"
              />
              <Tooltip
                content={({ active, payload, label }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload;
                    const gap = data.predicted_value - data.actual_value;
                    return (
                      <div className="bg-white p-4 border border-gray-200 rounded-lg shadow-lg">
                        <p className="font-semibold">{`Hour: ${label}:00`}</p>
                        <p className="text-blue-600">{`Your Prediction: ${formatValue(data.predicted_value)} MW`}</p>
                        <p className="text-red-600">{`Actual Usage: ${formatValue(data.actual_value)} MW`}</p>
                        <p className={`font-semibold ${gap > 0 ? 'text-red-600' : 'text-green-600'}`}>
                          {`Gap: ${gap > 0 ? '+' : ''}${formatValue(gap)} MW (${gap > 0 ? 'Over' : 'Under'} predicted)`}
                        </p>
                        {data.is_adjusted && (
                          <p className="text-purple-600 text-sm">✓ Adjusted by you</p>
                        )}
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Area
                type="monotone"
                dataKey="actual_value"
                stroke="#ef4444"
                strokeWidth={3}
                fill="transparent"
                name="Actual Usage"
              />
              <Area
                type="monotone"
                dataKey="predicted_value"
                stroke="#3b82f6"
                strokeWidth={3}
                fill="transparent"
                name="Your Prediction"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        <div className="mt-4 flex items-center justify-center space-x-6 text-sm">
          <div className="flex items-center">
            <div className="w-4 h-4 bg-blue-500 rounded mr-2"></div>
            <span>Your Prediction</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-red-500 rounded mr-2"></div>
            <span>Actual Usage</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-purple-500 rounded mr-2"></div>
            <span>Adjusted Hours</span>
          </div>
        </div>
      </div>

      {/* 24小时误差热力图 */}
      <div className="mb-8">
        <h3 className="text-xl font-semibold text-gray-800 mb-4">24-Hour Error Heatmap</h3>
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="grid grid-cols-12 gap-2 mb-4">
            {heatmapData.map((item) => (
              <div
                key={item.hour}
                className="relative group cursor-pointer"
                style={{
                  backgroundColor: getHeatmapColor(item.intensity),
                  height: '60px',
                  borderRadius: '8px',
                  border: '2px solid transparent',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.border = '2px solid #374151';
                  e.currentTarget.style.transform = 'scale(1.05)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.border = '2px solid transparent';
                  e.currentTarget.style.transform = 'scale(1)';
                }}
              >
                <div className="absolute inset-0 flex flex-col items-center justify-center text-white text-xs font-semibold">
                  <div>{item.hour}:00</div>
                  <div>{formatPercentage(item.errorPercent)}</div>
                </div>

                {/* Tooltip */}
                <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-800 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-10 whitespace-nowrap">
                  <div>Hour: {item.hour}:00</div>
                  <div>Error: {formatValue(item.error)} MW</div>
                  <div>Error %: {formatPercentage(item.errorPercent)}</div>
                  <div className="absolute top-full left-1/2 transform -translate-x-1/2 border-4 border-transparent border-t-gray-800"></div>
                </div>
              </div>
            ))}
          </div>

          {/* 热力图图例 */}
          <div className="flex items-center justify-between text-sm text-gray-600">
            <div className="flex items-center space-x-4">
              <span>Error Level:</span>
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 rounded" style={{ backgroundColor: getHeatmapColor(0) }}></div>
                <span>Low</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 rounded" style={{ backgroundColor: getHeatmapColor(0.5) }}></div>
                <span>Medium</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 rounded" style={{ backgroundColor: getHeatmapColor(1) }}></div>
                <span>High</span>
              </div>
            </div>
            <div className="text-xs text-gray-500">
              Hover over each hour for details
            </div>
          </div>
        </div>
      </div>

      {/* 误差柱状图 */}
      <div className="mb-8">
        <h3 className="text-xl font-semibold text-gray-800 mb-4">Detailed Error Analysis</h3>
        <div className="h-80 bg-white rounded-lg border border-gray-200 p-4">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={comparisonData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
              <XAxis
                dataKey="hour"
                tickFormatter={(value) => `${value}:00`}
                stroke="#6b7280"
              />
              <YAxis
                tickFormatter={(value) => `${formatValue(Math.abs(value))} MW`}
                stroke="#6b7280"
              />
              <Tooltip
                content={({ active, payload, label }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload;
                    return (
                      <div className="bg-white p-4 border border-gray-200 rounded-lg shadow-lg">
                        <p className="font-semibold">{`Hour: ${label}:00`}</p>
                        <p className={`${data.difference > 0 ? 'text-red-600' : 'text-green-600'}`}>
                          {`Error: ${data.difference > 0 ? '+' : ''}${formatValue(data.difference)} MW`}
                        </p>
                        <p className="text-gray-600">
                          {`Error Rate: ${formatPercentage(data.percentage_error)}`}
                        </p>
                        {data.is_adjusted && (
                          <p className="text-purple-600 text-sm">✓ Adjusted by you</p>
                        )}
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Bar
                dataKey="difference"
                name="Error (Predicted - Actual)"
              >
                {comparisonData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={entry.is_adjusted ? '#8b5cf6' : (entry.difference > 0 ? '#ef4444' : '#10b981')}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="mt-4 flex items-center justify-center space-x-6 text-sm">
          <div className="flex items-center">
            <div className="w-4 h-4 bg-red-500 rounded mr-2"></div>
            <span>Over-predicted</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-green-500 rounded mr-2"></div>
            <span>Under-predicted</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-purple-500 rounded mr-2"></div>
            <span>Your Adjustments</span>
          </div>
        </div>
      </div>

      {/* 简化的数据摘要 */}
      <div className="bg-gray-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Quick Summary</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{comparisonData.length}</div>
            <div className="text-sm text-gray-600">Hours Analyzed</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {comparisonData.filter(d => d.percentage_error <= 10).length}
            </div>
            <div className="text-sm text-gray-600">Good Predictions (&le;10%)</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">{summary.adjustedHours}</div>
            <div className="text-sm text-gray-600">Hours Adjusted</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">
              {Math.round(summary.averageError / 1000 * 10) / 10}k
            </div>
            <div className="text-sm text-gray-600">Avg Error (MW)</div>
          </div>
        </div>

        <div className="mt-6 text-center">
          <div className="text-sm text-gray-600 mb-2">
            Your prediction accuracy compared to actual electricity usage on January 7, 2022
          </div>
          <div className="text-xs text-gray-500">
            Hover over the heatmap and charts above for detailed hour-by-hour analysis
          </div>
        </div>
      </div>
    </div>
  );
};

export default PredictionComparison;
