import React, { useState, useEffect, useCallback } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,

} from 'recharts';

import type { PredictionResult } from '../types/index.js';
import ApiService from '../services/api';

interface UserPredictionProps {
  className?: string;
  onPredictionUpdate?: (predictions: PredictionResult[]) => void;
  hasActiveDecision?: boolean;
  onAdjustmentMade?: (hour: number, originalValue: number, adjustedValue: number) => void;
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
  onAdjustmentMade
}) => {
  const [predictions, setPredictions] = useState<PredictionResult[]>([]);
  const [chartData, setChartData] = useState<ChartData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [draggedPoint, setDraggedPoint] = useState<number | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [hoveredPoint, setHoveredPoint] = useState<number | null>(null);
  const [selectedPoint, setSelectedPoint] = useState<number | null>(null);
  const [dragStartYDomain, setDragStartYDomain] = useState<[number, number] | null>(null);

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
    if (selectedPoint === hour) {
      // If already selected, start dragging
      setDraggedPoint(hour);
      setIsDragging(true);
    } else {
      // Select this point
      setSelectedPoint(hour);
    }
  }, [selectedPoint]);

  // Handle drag start
  const handleDragStart = useCallback((hour: number) => {
    if (!hasActiveDecision) {
      // If no active decision, don't allow dragging
      return;
    }
    // Store the Y-axis domain at the start of dragging to ensure consistent calculations
    setDragStartYDomain(calculateYAxisDomain() as [number, number]);
    setDraggedPoint(hour);
    setIsDragging(true);
    setSelectedPoint(hour);
  }, [hasActiveDecision, calculateYAxisDomain]);

  // Handle drag end
  const handleDragEnd = useCallback(() => {
    // Update predictions data when drag ends
    if (draggedPoint !== null) {
      const pointIndex = chartData.findIndex(item => item.hour === draggedPoint);
      if (pointIndex !== -1) {
        const originalValue = chartData[pointIndex].original_prediction || chartData[pointIndex].predicted_usage;
        const adjustedValue = chartData[pointIndex].predicted_usage;

        // Notify DecisionMaking component of adjustment
        if (originalValue !== adjustedValue) {
          onAdjustmentMade?.(draggedPoint, originalValue, adjustedValue);
        }

        const newPredictions = [...predictions];
        newPredictions[pointIndex] = {
          ...newPredictions[pointIndex],
          predicted_usage: chartData[pointIndex].predicted_usage
        };
        setPredictions(newPredictions);
        onPredictionUpdate?.(newPredictions);
      }
    }

    setDraggedPoint(null);
    setIsDragging(false);
    setDragStartYDomain(null); // Clear the stored domain
  }, [draggedPoint, chartData, predictions, onPredictionUpdate, onAdjustmentMade]);

  // Handle mouse move (dragging) - instant response, no delay
  const handleMouseMove = useCallback((e: any) => {
    if (draggedPoint !== null && e && e.activeCoordinate && hasActiveDecision && dragStartYDomain) {
      const chartHeight = 360; // Chart height
      const [yMin, yMax] = dragStartYDomain; // Use stored Y-axis range for consistent dragging
      const marginTop = 20; // Chart top margin

      // Precisely calculate new prediction value - instant response
      const mouseY = e.activeCoordinate.y;
      const relativeY = Math.max(0, Math.min(chartHeight, mouseY - marginTop));
      const valueRatio = 1 - (relativeY / chartHeight); // Invert Y-axis
      const newValue = yMin + valueRatio * (yMax - yMin);

      // Allow values beyond current range - don't clamp to current domain
      const adjustedValue = Math.max(0, Math.round(newValue));

      // Immediately update chartData for instant response
      setChartData(prevData => {
        const newData = [...prevData];
        const pointIndex = newData.findIndex(item => item.hour === draggedPoint);
        if (pointIndex !== -1 && newData[pointIndex].predicted_usage !== adjustedValue) {
          newData[pointIndex] = {
            ...newData[pointIndex],
            predicted_usage: adjustedValue,
            isAdjusted: true
          };
        }
        return newData;
      });
    }
  }, [draggedPoint, hasActiveDecision, dragStartYDomain]);

  // Custom dot component with drag support - improved interaction experience
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
    const cursorStyle = !canInteract ? 'not-allowed' : (isDragging ? 'grabbing' : 'pointer');
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
          onMouseDown={() => canInteract && handleDragStart(payload.hour)}
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
          onMouseDown={() => canInteract && handleDragStart(payload.hour)}
          onClick={() => canInteract && handlePointClick(payload.hour)}
        />

        {/* Inner circle */}
        <circle
          cx={cx}
          cy={cy}
          r={innerRadius}
          fill="#ffffff"
          style={{
            cursor: isDragging ? 'grabbing' : 'pointer',
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
            onClick={resetPredictions}
            className="px-3 py-1 text-xs bg-gray-500 text-white border-none rounded cursor-pointer hover:bg-gray-600 transition-colors"
          >
            🔄 Reset
          </button>
          <button
            onClick={exportResults}
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
              onMouseMove={handleMouseMove}
              onMouseUp={handleDragEnd}
              onMouseLeave={handleDragEnd}
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

          {/* Selected time period indicator - floating above chart */}
          {selectedPoint !== null && (
            <div style={{
              position: 'absolute',
              top: '10px',
              left: '50%',
              transform: 'translateX(-50%)',
              fontSize: '16px',
              fontWeight: '500',
              color: '#333',
              backgroundColor: '#F2F3F5',
              padding: '6px 12px',
              borderRadius: '4px',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
              zIndex: 10
            }}>
              Currently Selected: {selectedPoint}:00
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default UserPrediction;
