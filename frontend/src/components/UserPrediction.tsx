import React, { useState, useEffect, useCallback } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Dot
} from 'recharts';

import type { PredictionResult } from '../types/index.js';
import ApiService from '../services/api';
import { useUser } from '../context/UserContext';

interface UserPredictionProps {
  className?: string;
  onPredictionUpdate?: (predictions: PredictionResult[]) => void;
  hasActiveDecision?: boolean;
  onAdjustmentMade?: (hour: number, originalValue: number, adjustedValue: number) => void;
  onPredictionDataChange?: (data: any[]) => void; // 添加数据变化回调
}

interface ChartData {
  hour: number;
  predicted_usage: number;
  confidence_min: number;
  confidence_max: number;
  original_prediction?: number;
  isAdjusted?: boolean;
}

const UserPrediction: React.FC<UserPredictionProps> = ({
  className = '',
  onPredictionUpdate,
  hasActiveDecision = false,
  onAdjustmentMade,
  onPredictionDataChange
}) => {
  const [predictions, setPredictions] = useState<PredictionResult[]>([]);
  const [chartData, setChartData] = useState<ChartData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hoveredPoint, setHoveredPoint] = useState<number | null>(null);
  const [selectedPoint, setSelectedPoint] = useState<number | null>(null);
  const [adjustmentValue, setAdjustmentValue] = useState<number>(0); // 平衡轴调整值
  const [showAdjustmentBar, setShowAdjustmentBar] = useState<boolean>(false); // 控制平衡轴显示

  // 使用UserContext记录交互
  const { recordButtonClick, recordInteraction } = useUser();

  // Calculate dynamic Y-axis domain based on current data
  const calculateYAxisDomain = useCallback(() => {
    if (!chartData.length) return [2000, 5000];

    const values = chartData.map(item => item.predicted_usage);
    const minValue = Math.min(...values);
    const maxValue = Math.max(...values);

    // Add 10% padding on both sides
    const padding = (maxValue - minValue) * 0.1;
    const yMin = Math.max(0, Math.floor((minValue - padding) / 100) * 100); // Round down to nearest 100
    const yMax = Math.ceil((maxValue + padding) / 100) * 100; // Round up to nearest 100

    // Ensure minimum range of 1000MW
    const minRange = 1000;
    if (yMax - yMin < minRange) {
      const center = (yMin + yMax) / 2;
      return [Math.max(0, center - minRange / 2), center + minRange / 2];
    }

    return [yMin, yMax];
  }, [chartData]);

  useEffect(() => {
    loadPredictions();
  }, []);

  // 通知父组件数据变化
  useEffect(() => {
    if (onPredictionDataChange && chartData.length > 0) {
      onPredictionDataChange(chartData);
    }
  }, [chartData, onPredictionDataChange]);

  const loadPredictions = async () => {
    try {
      setLoading(true);

      // Load actual prediction data from CSV file
      const response = await fetch('/data/worst_day_1_2022_01_07_winter_extreme_cold.csv');
      const csvText = await response.text();

      const lines = csvText.split('\n');
      const targetDateData = lines.filter(line => line.includes('2022-01-07'));

      if (targetDateData.length === 0) {
        throw new Error('No data found for target date 2022-01-07');
      }

      const actualPredictions: PredictionResult[] = targetDateData.map(line => {
        const values = line.split(',');
        const datetime = values[0];
        const predictedPower = parseFloat(values[1]) || 0;

        // Extract hour from datetime
        const hour = new Date(datetime).getHours();

        // Generate confidence interval based on predicted value (±5%)
        const margin = predictedPower * 0.05;
        const confidence_min = Math.round(predictedPower - margin);
        const confidence_max = Math.round(predictedPower + margin);

        return {
          hour,
          predicted_usage: Math.round(predictedPower),
          confidence_interval: [confidence_min, confidence_max] as [number, number]
        };
      }).sort((a, b) => a.hour - b.hour); // Sort by hour

      setPredictions(actualPredictions);

      // Convert data format for chart display
      const formattedData = actualPredictions.map((item) => ({
        hour: item.hour,
        predicted_usage: item.predicted_usage,
        confidence_min: item.confidence_interval[0],
        confidence_max: item.confidence_interval[1],
        original_prediction: item.predicted_usage,
        isAdjusted: false
      }));

      setChartData(formattedData);
      onPredictionUpdate?.(actualPredictions);
    } catch (err) {
      setError('Failed to load prediction data');
      console.error('Error loading predictions:', err);
    } finally {
      setLoading(false);
    }
  };

  const resetPredictions = () => {
    try {
      // Reset local data to original state
      const resetData = chartData.map(item => ({
        ...item,
        predicted_usage: item.original_prediction || item.predicted_usage,
        isAdjusted: false
      }));

      setChartData(resetData);

      // Also reset predictions data
      const resetPredictions = resetData.map(item => ({
        hour: item.hour,
        predicted_usage: item.predicted_usage,
        confidence_interval: [item.confidence_min, item.confidence_max] as [number, number]
      }));

      setPredictions(resetPredictions);
      onPredictionUpdate?.(resetPredictions);

      console.log('Prediction data has been reset to original state');
    } catch (err) {
      console.error('Error resetting predictions:', err);
    }
  };

  const exportResults = async () => {
    try {
      const blob = await ApiService.exportResults('csv');
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `prediction_results_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Error exporting results:', err);
    }
  };

  // Custom Tooltip
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      const userPrediction = data.predicted_usage;
      const aiBaseline = data.original_prediction;
      const difference = userPrediction - aiBaseline;

      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="text-sm font-medium text-gray-800">{`Time: ${label}:00`}</p>
          <p className="text-sm text-red-600">
            User Prediction: {userPrediction} MW
          </p>
          <p className="text-sm" style={{ color: '#A0A7B4' }}>
            AI Baseline: {aiBaseline} MW
          </p>
          {Math.abs(difference) > 0.1 && (
            <p className="text-sm" style={{ color: difference > 0 ? '#059669' : '#dc2626' }}>
              Difference: {difference > 0 ? '+' : ''}{difference.toFixed(0)} MW
            </p>
          )}
          <p className="text-sm text-gray-600">
            Confidence Interval: {data.confidence_min} - {data.confidence_max} MW
          </p>
        </div>
      );
    }
    return null;
  };

  // Handle point click selection
  const handlePointClick = useCallback((hour: number) => {
    if (!hasActiveDecision) return;

    // Select the point and show adjustment bar
    setSelectedPoint(hour);
    setShowAdjustmentBar(true);
    const currentData = chartData.find(d => d.hour === hour);
    const originalValue = currentData?.original_prediction || currentData?.predicted_usage || 0;
    const currentValue = currentData?.predicted_usage || 0;
    const currentAdjustment = currentValue - originalValue;
    setAdjustmentValue(currentAdjustment);

    // 记录数据点点击交互
    recordInteraction(
      'UserPrediction',
      'data_point_click',
      {
        hour,
        action: 'select_point',
        currentValue: currentData?.predicted_usage
      }
    );
  }, [hasActiveDecision, chartData, recordInteraction]);

  // Handle adjustment slider change
  const handleAdjustmentChange = useCallback((newAdjustment: number) => {
    if (selectedPoint === null || !hasActiveDecision) return;

    setAdjustmentValue(newAdjustment);

    // Update chart data immediately
    setChartData(prevData => {
      const newData = [...prevData];
      const pointIndex = newData.findIndex(item => item.hour === selectedPoint);
      if (pointIndex !== -1) {
        const originalValue = newData[pointIndex].original_prediction || newData[pointIndex].predicted_usage;
        const adjustedValue = Math.max(0, originalValue + newAdjustment);

        newData[pointIndex] = {
          ...newData[pointIndex],
          predicted_usage: adjustedValue,
          isAdjusted: newAdjustment !== 0
        };

        // Notify DecisionMaking component of adjustment
        if (newAdjustment !== 0) {
          onAdjustmentMade?.(selectedPoint, originalValue, adjustedValue);
        }
      }
      return newData;
    });

    // Record interaction
    recordInteraction(
      'UserPrediction',
      'slider_adjustment',
      {
        hour: selectedPoint,
        adjustmentValue: newAdjustment
      }
    );
  }, [selectedPoint, hasActiveDecision, onAdjustmentMade, recordInteraction]);

  // Handle closing adjustment bar
  const handleCloseAdjustmentBar = useCallback(() => {
    setShowAdjustmentBar(false);
    setSelectedPoint(null);
    setAdjustmentValue(0);

    // Record interaction
    recordInteraction(
      'UserPrediction',
      'close_adjustment_bar',
      {}
    );
  }, [recordInteraction]);

  const CustomDot = (props: any) => {
    const { cx, cy, payload } = props;
    const isAdjusted = payload?.isAdjusted || false;
    const isSelected = selectedPoint === payload.hour;
    const isHovered = hoveredPoint === payload.hour;

    // Dynamically calculate dot size
    const baseRadius = 10; // Increased base radius
    const hoverBonus = isHovered ? 3 : 0;
    const selectedBonus = isSelected ? 2 : 0;
    const outerRadius = baseRadius + hoverBonus + selectedBonus;
    const innerRadius = Math.max(4, outerRadius - 6);

    // Determine interaction capability based on decision status
    const canInteract = hasActiveDecision;
    const cursorStyle = !canInteract ? 'not-allowed' : 'pointer';
    const opacity = !canInteract ? 0.6 : 1;

    return (
      <g>
        {/* Large transparent click area - easier to click */}
        <circle
          cx={cx}
          cy={cy}
          r={25}
          fill="transparent"
          style={{ cursor: cursorStyle }}
          onMouseEnter={() => canInteract && setHoveredPoint(payload.hour)}
          onMouseLeave={() => setHoveredPoint(null)}
          onClick={() => canInteract && handlePointClick(payload.hour)}
        />

        {/* Hover indicator circle - shows clickable area */}
        {isHovered && canInteract && (
          <circle
            cx={cx}
            cy={cy}
            r={20}
            fill="rgba(255, 0, 0, 0.1)"
            stroke="rgba(255, 0, 0, 0.3)"
            strokeWidth={1}
            strokeDasharray="2 2"
          />
        )}

        {/* Disabled state indicator circle */}
        {isHovered && !canInteract && (
          <circle
            cx={cx}
            cy={cy}
            r={20}
            fill="rgba(128, 128, 128, 0.1)"
            stroke="rgba(128, 128, 128, 0.5)"
            strokeWidth={1}
            strokeDasharray="2 2"
          />
        )}

        {/* Selection indicator circle */}
        {isSelected && (
          <circle
            cx={cx}
            cy={cy}
            r={outerRadius + 4}
            fill="none"
            stroke="#0066ff"
            strokeWidth={2}
            strokeDasharray="4 4"
          />
        )}

        {/* Outer circle - dynamic size */}
        <circle
          cx={cx}
          cy={cy}
          r={outerRadius}
          fill={isAdjusted ? "#f59e0b" : "#ff0000"}
          stroke="#ffffff"
          strokeWidth={3}
          opacity={opacity}
          style={{
            cursor: cursorStyle,
            filter: isHovered && canInteract ? 'brightness(1.2)' : 'none'
          }}
          onMouseEnter={() => canInteract && setHoveredPoint(payload.hour)}
          onMouseLeave={() => setHoveredPoint(null)}
          onClick={() => canInteract && handlePointClick(payload.hour)}
        />

        {/* Inner circle */}
        <circle
          cx={cx}
          cy={cy}
          r={innerRadius}
          fill="#ffffff"
          style={{
            cursor: 'pointer',
            pointerEvents: 'none' // Avoid interfering with clicks
          }}
        />

        {/* Adjustment indicator */}
        {isAdjusted && (
          <circle
            cx={cx + outerRadius + 2}
            cy={cy - outerRadius - 2}
            r={5}
            fill="#28a745"
            stroke="#ffffff"
            strokeWidth={2}
          />
        )}

        {/* Hour label - shown on hover */}
        {isHovered && (
          <text
            x={cx}
            y={cy - outerRadius - 8}
            textAnchor="middle"
            fontSize="10"
            fill="#333"
            fontWeight="bold"
            style={{ pointerEvents: 'none' }}
          >
            {payload.hour}:00
          </text>
        )}
      </g>
    );
  };

  if (loading) {
    return (
      <div className={`card p-6 ${className}`}>
        <h3 className="text-lg font-semibold text-gray-800 mb-4">User Prediction</h3>
        <div className="animate-pulse">
          <div className="h-80 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`card p-6 ${className}`}>
        <h3 className="text-lg font-semibold text-gray-800 mb-4">User Prediction</h3>
        <div className="text-red-500 text-sm">{error}</div>
      </div>
    );
  }

  return (
    <div className="module-box">
      <div className="flex items-center justify-between mb-4" style={{ flexShrink: 0 }}>
        <div className="flex items-center gap-4">
          <div className="module-title">User Prediction</div>
          {/* AI Baseline indicator - moved to right side with larger font */}
          <div className="flex items-center gap-2" style={{ fontSize: '16px', color: '#A0A7B4', fontWeight: '500' }}>
            <span style={{
              display: 'inline-block',
              width: '20px',
              height: '2px',
              backgroundColor: '#A0A7B4',
              borderTop: '2px dashed #A0A7B4',
              verticalAlign: 'middle'
            }}></span>
            AI Baseline
          </div>
        </div>
        {/* Action buttons moved to top right */}
        <div className="flex gap-2">
          <button
            onClick={() => {
              resetPredictions();
              // 记录重置按钮点击
              recordButtonClick('UserPrediction', 'reset_button', 'Reset');
            }}
            className="px-3 py-1 text-xs bg-gray-500 text-white border-none rounded cursor-pointer hover:bg-gray-600 transition-colors"
          >
            🔄 Reset
          </button>
          <button
            onClick={() => {
              exportResults();
              // 记录导出按钮点击
              recordButtonClick('UserPrediction', 'export_button', 'Export');
            }}
            className="px-3 py-1 text-xs bg-green-500 text-white border-none rounded cursor-pointer hover:bg-green-600 transition-colors"
          >
            📥 Export
          </button>
        </div>
      </div>

      {/* Optimized chart area - use flex to fill available space */}
      <div className="chart-content-area">
        <div className="chart-wrapper" style={{ position: 'relative' }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={chartData}
              margin={{ top: 20, right: 20, left: 40, bottom: 40 }}

            >
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
              <XAxis
                dataKey="hour"
                tick={{ fontSize: 10 }}
                label={{ value: 'Time (Hours)', position: 'insideBottom', offset: -10, style: { fontSize: '10px' } }}
              />
              <YAxis
                tick={{ fontSize: 10 }}
                label={{ value: 'Power Demand (MW)', angle: -90, position: 'insideLeft', style: { fontSize: '10px' } }}
                domain={calculateYAxisDomain()}
              />
              <Tooltip content={<CustomTooltip />} />

              {/* AI baseline - original prediction */}
              <Line
                type="monotone"
                dataKey="original_prediction"
                stroke="#A0A7B4"
                strokeWidth={2}
                strokeDasharray="6 6"
                dot={false}
                name="AI Baseline"
                connectNulls={false}
              />

              {/* User adjusted prediction line */}
              <Line
                type="monotone"
                dataKey="predicted_usage"
                stroke="#ff0000"
                strokeWidth={3}
                dot={<CustomDot />}
                name="User Prediction"
                connectNulls={false}
              />

              {/* Confidence interval fill */}
              <Line
                type="monotone"
                dataKey="confidence_max"
                stroke="#ff9999"
                strokeWidth={1}
                strokeDasharray="2 2"
                dot={false}
                name="Confidence Upper Limit"
              />
              <Line
                type="monotone"
                dataKey="confidence_min"
                stroke="#ff9999"
                strokeWidth={1}
                strokeDasharray="2 2"
                dot={false}
                name="Confidence Lower Limit"
              />
            </LineChart>
          </ResponsiveContainer>


        </div>

        {/* 平衡轴调整控件 */}
        {selectedPoint !== null && hasActiveDecision && showAdjustmentBar && (
          <div style={{
            marginTop: '20px',
            padding: '20px',
            backgroundColor: '#f8f9fa',
            borderRadius: '8px',
            border: '1px solid #e9ecef',
            position: 'relative'
          }}>
            {/* 关闭按钮 */}
            <button
              onClick={handleCloseAdjustmentBar}
              style={{
                position: 'absolute',
                top: '8px',
                right: '8px',
                width: '24px',
                height: '24px',
                border: 'none',
                borderRadius: '50%',
                backgroundColor: '#dc3545',
                color: 'white',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '14px',
                fontWeight: 'bold',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#c82333';
                e.currentTarget.style.transform = 'scale(1.1)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#dc3545';
                e.currentTarget.style.transform = 'scale(1)';
              }}
              title="Close adjustment bar"
            >
              ×
            </button>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '15px'
            }}>
              {/* 左端标记 */}
              <span style={{
                fontSize: '14px',
                fontWeight: '600',
                color: '#dc3545',
                minWidth: '60px',
                textAlign: 'center'
              }}>
                -1000
              </span>

              {/* 平衡轴滑块 */}
              <div style={{ position: 'relative', flex: 1, maxWidth: '400px' }}>
                <input
                  type="range"
                  min="-1000"
                  max="1000"
                  step="10"
                  value={adjustmentValue}
                  onChange={(e) => handleAdjustmentChange(Number(e.target.value))}
                  style={{
                    width: '100%',
                    height: '6px',
                    borderRadius: '3px',
                    background: `linear-gradient(to right,
                      #dc3545 0%,
                      #dc3545 50%,
                      #28a745 50%,
                      #28a745 100%)`,
                    outline: 'none',
                    appearance: 'none',
                    cursor: 'pointer'
                  }}
                />

                {/* 中心点标记 */}
                <div style={{
                  position: 'absolute',
                  top: '-2px',
                  left: '50%',
                  transform: 'translateX(-50%)',
                  width: '2px',
                  height: '10px',
                  backgroundColor: '#6c757d',
                  borderRadius: '1px'
                }} />

                {/* 当前数值显示 */}
                <div style={{
                  position: 'absolute',
                  top: '-30px',
                  left: '50%',
                  transform: 'translateX(-50%)',
                  fontSize: '12px',
                  fontWeight: '600',
                  color: adjustmentValue === 0 ? '#6c757d' : (adjustmentValue > 0 ? '#28a745' : '#dc3545'),
                  backgroundColor: 'white',
                  padding: '2px 6px',
                  borderRadius: '4px',
                  border: '1px solid #dee2e6'
                }}>
                  {adjustmentValue > 0 ? '+' : ''}{adjustmentValue}
                </div>
              </div>

              {/* 右端标记 */}
              <span style={{
                fontSize: '14px',
                fontWeight: '600',
                color: '#28a745',
                minWidth: '60px',
                textAlign: 'center'
              }}>
                +1000
              </span>
            </div>
          </div>
        )}
      </div>

      {/* 滑块样式 */}
      <style>{`
        input[type="range"] {
          -webkit-appearance: none;
          appearance: none;
        }

        input[type="range"]::-webkit-slider-thumb {
          -webkit-appearance: none;
          appearance: none;
          width: 20px;
          height: 20px;
          border-radius: 50%;
          background: #007bff;
          border: 2px solid white;
          box-shadow: 0 2px 4px rgba(0,0,0,0.2);
          cursor: pointer;
          transition: all 0.2s ease;
        }

        input[type="range"]::-webkit-slider-thumb:hover {
          background: #0056b3;
          transform: scale(1.1);
        }

        input[type="range"]::-moz-range-thumb {
          width: 20px;
          height: 20px;
          border-radius: 50%;
          background: #007bff;
          border: 2px solid white;
          box-shadow: 0 2px 4px rgba(0,0,0,0.2);
          cursor: pointer;
          transition: all 0.2s ease;
        }

        input[type="range"]::-moz-range-thumb:hover {
          background: #0056b3;
          transform: scale(1.1);
        }
      `}</style>
    </div>
  );
};

export default UserPrediction;
