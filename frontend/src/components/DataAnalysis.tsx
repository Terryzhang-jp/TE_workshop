import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';
import { Zap, Thermometer, Maximize2, X } from 'lucide-react';

interface DataAnalysisProps {
  className?: string;
  onInteraction?: (actionType: string, details: any) => void;
}

interface ChartData {
  time: string;
  predictedPower: number;
  actualPower: number | null;
  predictedTemp: number;
  timestamp: string;
  isTargetDay: boolean;
}

const DataAnalysis: React.FC<DataAnalysisProps> = ({ className = '', onInteraction }) => {
  const [chartData, setChartData] = useState<ChartData[]>([]);
  const [filteredData, setFilteredData] = useState<ChartData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [viewType, setViewType] = useState<'electricity' | 'weather'>('electricity');
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [minDate, setMinDate] = useState<string>('');
  const [maxDate, setMaxDate] = useState<string>('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  const loadWorstDayData = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch('/data/worst_day_1_2022_01_07_winter_extreme_cold.csv');
      const csvText = await response.text();

      const lines = csvText.split('\n');
      const data = lines.slice(1).filter(line => line.trim()).map(line => {
        const values = line.split(',');
        return {
          time: values[0],
          predictedPower: parseFloat(values[1]) || 0,
          actualPower: values[2] === '' || values[2] === undefined ? null : parseFloat(values[2]),
          predictedTemp: parseFloat(values[3]) || 0
        };
      });

      const processedData = data.map((item: any) => {
        const date = new Date(item.time);
        const isTargetDay = date.getDate() === 7 && date.getMonth() === 0;

        return {
          time: `${date.getMonth() + 1}/${date.getDate()} ${String(date.getHours()).padStart(2, '0')}:00`,
          predictedPower: item.predictedPower,
          actualPower: item.actualPower,
          predictedTemp: item.predictedTemp,
          timestamp: item.time,
          isTargetDay
        };
      });

      setChartData(processedData);
      setFilteredData(processedData);

      if (processedData.length > 0) {
        const dates = processedData.map(d => d.timestamp);
        const minDateTime = new Date(Math.min(...dates.map(d => new Date(d).getTime())));
        const maxDateTime = new Date(Math.max(...dates.map(d => new Date(d).getTime())));

        const minDateStr = minDateTime.toISOString().split('T')[0];
        const maxDateStr = maxDateTime.toISOString().split('T')[0];

        setMinDate(minDateStr);
        setMaxDate(maxDateStr);
        setStartDate(minDateStr);
        setEndDate(maxDateStr);
      }

    } catch (err) {
      console.error('Failed to load data:', err);
      setError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const filterDataByDateRange = () => {
    if (!chartData.length || !startDate || !endDate) {
      setFilteredData(chartData);
      return;
    }

    const start = new Date(startDate + 'T00:00:00');
    const end = new Date(endDate + 'T23:59:59');

    const filtered = chartData.filter(item => {
      const itemDate = new Date(item.timestamp);
      return itemDate >= start && itemDate <= end;
    });

    setFilteredData(filtered);
  };

  const calculateYAxisDomain = (data: ChartData[], key: keyof ChartData) => {
    if (!data.length) return [0, 100];
    
    const values = data.map(d => d[key] as number).filter(v => v !== null && !isNaN(v));
    if (!values.length) return [0, 100];
    
    const minValue = Math.min(...values);
    const maxValue = Math.max(...values);
    const padding = (maxValue - minValue) * 0.05;
    
    return [minValue - padding, maxValue + padding];
  };

  useEffect(() => {
    loadWorstDayData();
  }, []);

  useEffect(() => {
    filterDataByDateRange();
  }, [chartData, startDate, endDate]);

  // 键盘事件监听
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isModalOpen) {
        setIsModalOpen(false);
      }
    };

    if (isModalOpen) {
      document.addEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'hidden'; // 防止背景滚动
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'unset';
    };
  }, [isModalOpen]);

  const openModal = () => setIsModalOpen(true);
  const closeModal = () => setIsModalOpen(false);

  if (loading) {
    return (
      <div className="module-box">
        <div className="module-title">Data Analysis Information</div>
        <div className="flex items-center justify-center" style={{ height: 'calc(100% - 40px)' }}>
          <div className="text-gray-500 text-sm">Loading...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="module-box">
        <div className="module-title">Data Analysis Information</div>
        <div className="flex items-center justify-center" style={{ height: 'calc(100% - 40px)' }}>
          <div className="text-red-500 text-sm">{error}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="module-box">
      <div className="module-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span>Data Analysis Information</span>
        <button
          onClick={openModal}
          style={{
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            padding: '4px',
            borderRadius: '4px',
            display: 'flex',
            alignItems: 'center',
            color: '#6b7280',
            transition: 'color 0.2s'
          }}
          onMouseEnter={(e) => e.currentTarget.style.color = '#3b82f6'}
          onMouseLeave={(e) => e.currentTarget.style.color = '#6b7280'}
          title="Expand to full view"
        >
          <Maximize2 size={16} />
        </button>
      </div>
      
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        marginBottom: '8px',
        padding: '4px 0',
        borderBottom: '1px solid #e5e7eb',
        flexShrink: 0
      }}>
        <div style={{ display: 'flex', gap: '2px' }}>
          <button
            onClick={() => {
              setViewType('electricity');
              onInteraction?.('view_change', {
                view_type: 'electricity',
                previous_view: viewType
              });
            }}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              padding: '4px 8px',
              fontSize: '10px',
              border: 'none',
              borderRadius: '4px',
              backgroundColor: viewType === 'electricity' ? '#3b82f6' : '#f3f4f6',
              color: viewType === 'electricity' ? 'white' : '#6b7280',
              cursor: 'pointer'
            }}
          >
            <Zap size={12} />
            Power
          </button>
          <button
            onClick={() => {
              setViewType('weather');
              onInteraction?.('view_change', {
                view_type: 'weather',
                previous_view: viewType
              });
            }}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              padding: '4px 8px',
              fontSize: '10px',
              border: 'none',
              borderRadius: '4px',
              backgroundColor: viewType === 'weather' ? '#3b82f6' : '#f3f4f6',
              color: viewType === 'weather' ? 'white' : '#6b7280',
              cursor: 'pointer'
            }}
          >
            <Thermometer size={12} />
            Weather
          </button>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <input
            type="date"
            value={startDate}
            min={minDate}
            max={endDate || maxDate}
            onChange={(e) => {
              const newStartDate = e.target.value;
              setStartDate(newStartDate);
              if (endDate && newStartDate > endDate) {
                setEndDate(newStartDate);
              }
              onInteraction?.('date_change', {
                date_type: 'start_date',
                new_value: newStartDate,
                previous_value: startDate
              });
            }}
            style={{
              fontSize: '9px',
              padding: '2px 4px',
              border: '1px solid #d1d5db',
              borderRadius: '2px',
              width: '90px'
            }}
          />
          <span style={{ color: '#9ca3af', fontSize: '10px' }}>-</span>
          <input
            type="date"
            value={endDate}
            min={startDate || minDate}
            max={maxDate}
            onChange={(e) => {
              const newEndDate = e.target.value;
              setEndDate(newEndDate);
              if (startDate && newEndDate < startDate) {
                setStartDate(newEndDate);
              }
              onInteraction?.('date_change', {
                date_type: 'end_date',
                new_value: newEndDate,
                previous_value: endDate
              });
            }}
            style={{
              fontSize: '9px',
              padding: '2px 4px',
              border: '1px solid #d1d5db',
              borderRadius: '2px',
              width: '90px'
            }}
          />
        </div>
      </div>

      <div style={{ 
        flex: 1, 
        minHeight: '300px',
        position: 'relative'
      }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={filteredData} margin={{ top: 10, right: 10, left: 10, bottom: 40 }}>
            <CartesianGrid strokeDasharray="2 2" stroke="#e5e7eb" strokeOpacity={0.5} />
            <XAxis
              dataKey="time"
              tick={{ fontSize: 8 }}
              interval={Math.floor(filteredData.length / 12)}
              angle={-45}
              textAnchor="end"
              height={35}
              stroke="#6b7280"
            />
            <YAxis
              tick={{ fontSize: 8 }}
              label={{ 
                value: viewType === 'electricity' ? 'Power (MW)' : 'Temperature (°C)', 
                angle: -90, 
                position: 'insideLeft',
                style: { textAnchor: 'middle', fontSize: '10px' }
              }}
              domain={calculateYAxisDomain(filteredData, viewType === 'electricity' ? 'predictedPower' : 'predictedTemp')}
              tickFormatter={(value) => Number(value).toFixed(0)}
              stroke="#6b7280"
            />
            <Tooltip
              content={({ active, payload, label }) => {
                if (active && payload && payload.length) {
                  const data = payload[0].payload;
                  return (
                    <div style={{
                      backgroundColor: 'rgba(255, 255, 255, 0.95)',
                      border: '1px solid #d1d5db',
                      borderRadius: '6px',
                      padding: '6px 8px',
                      fontSize: '10px',
                      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                    }}>
                      <p style={{ margin: 0, fontWeight: 'bold', fontSize: '9px' }}>{label}</p>
                      {viewType === 'electricity' ? (
                        <>
                          <p style={{ margin: '2px 0 0 0', color: '#3b82f6' }}>
                            Predicted: {data.predictedPower?.toFixed(1)} MW
                          </p>
                          {data.actualPower !== null && (
                            <p style={{ margin: '2px 0 0 0', color: '#ef4444' }}>
                              Actual: {data.actualPower?.toFixed(1)} MW
                            </p>
                          )}
                        </>
                      ) : (
                        <p style={{ margin: '2px 0 0 0', color: '#059669' }}>
                          Temperature: {data.predictedTemp?.toFixed(1)}°C
                        </p>
                      )}
                      {data.isTargetDay && (
                        <p style={{ margin: '2px 0 0 0', color: '#f59e0b', fontWeight: 'bold', fontSize: '9px' }}>
                          Target Day
                        </p>
                      )}
                    </div>
                  );
                }
                return null;
              }}
            />
            
            {viewType === 'electricity' ? (
              <>
                <Line
                  type="monotone"
                  dataKey="predictedPower"
                  stroke="#3b82f6"
                  strokeWidth={1.5}
                  dot={false}
                  activeDot={{ r: 3, stroke: '#3b82f6', strokeWidth: 2 }}
                  name="Predicted"
                />
                <Line
                  type="monotone"
                  dataKey="actualPower"
                  stroke="#ef4444"
                  strokeWidth={1.5}
                  dot={false}
                  activeDot={{ r: 3, stroke: '#ef4444', strokeWidth: 2 }}
                  connectNulls={false}
                  name="Actual"
                />
                <ReferenceLine 
                  x="1/7 00:00" 
                  stroke="#f59e0b" 
                  strokeDasharray="3 3" 
                  strokeWidth={1}
                />
              </>
            ) : (
              <Line
                type="monotone"
                dataKey="predictedTemp"
                stroke="#059669"
                strokeWidth={1.5}
                dot={false}
                activeDot={{ r: 3, stroke: '#059669', strokeWidth: 2 }}
                name="Temperature"
              />
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* 模态弹窗 */}
      {isModalOpen && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            zIndex: 1000,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '20px'
          }}
          onClick={closeModal}
        >
          <div
            style={{
              backgroundColor: 'white',
              borderRadius: '12px',
              width: '95vw',
              height: '90vh',
              maxWidth: '1400px',
              display: 'flex',
              flexDirection: 'column',
              overflow: 'hidden',
              boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* 弹窗标题栏 */}
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              padding: '16px 20px',
              borderBottom: '1px solid #e5e7eb',
              flexShrink: 0
            }}>
              <h2 style={{ margin: 0, fontSize: '18px', fontWeight: '600', color: '#1f2937' }}>
                Data Analysis - Detailed View
              </h2>
              <button
                onClick={closeModal}
                style={{
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  padding: '8px',
                  borderRadius: '6px',
                  display: 'flex',
                  alignItems: 'center',
                  color: '#6b7280',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#f3f4f6';
                  e.currentTarget.style.color = '#374151';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'transparent';
                  e.currentTarget.style.color = '#6b7280';
                }}
              >
                <X size={20} />
              </button>
            </div>

            {/* 弹窗过滤控件 */}
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              padding: '12px 20px',
              borderBottom: '1px solid #e5e7eb',
              flexShrink: 0,
              backgroundColor: '#f9fafb'
            }}>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button
                  onClick={() => setViewType('electricity')}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    padding: '8px 12px',
                    fontSize: '14px',
                    border: 'none',
                    borderRadius: '6px',
                    backgroundColor: viewType === 'electricity' ? '#3b82f6' : '#f3f4f6',
                    color: viewType === 'electricity' ? 'white' : '#6b7280',
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                >
                  <Zap size={16} />
                  Power Analysis
                </button>
                <button
                  onClick={() => setViewType('weather')}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    padding: '8px 12px',
                    fontSize: '14px',
                    border: 'none',
                    borderRadius: '6px',
                    backgroundColor: viewType === 'weather' ? '#3b82f6' : '#f3f4f6',
                    color: viewType === 'weather' ? 'white' : '#6b7280',
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                >
                  <Thermometer size={16} />
                  Weather Analysis
                </button>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <input
                  type="date"
                  value={startDate}
                  min={minDate}
                  max={endDate || maxDate}
                  onChange={(e) => {
                    const newStartDate = e.target.value;
                    setStartDate(newStartDate);
                    if (endDate && newStartDate > endDate) {
                      setEndDate(newStartDate);
                    }
                  }}
                  style={{
                    fontSize: '12px',
                    padding: '6px 8px',
                    border: '1px solid #d1d5db',
                    borderRadius: '4px',
                    width: '120px'
                  }}
                />
                <span style={{ color: '#9ca3af', fontSize: '14px' }}>to</span>
                <input
                  type="date"
                  value={endDate}
                  min={startDate || minDate}
                  max={maxDate}
                  onChange={(e) => {
                    const newEndDate = e.target.value;
                    setEndDate(newEndDate);
                    if (startDate && newEndDate < startDate) {
                      setStartDate(newEndDate);
                    }
                  }}
                  style={{
                    fontSize: '12px',
                    padding: '6px 8px',
                    border: '1px solid #d1d5db',
                    borderRadius: '4px',
                    width: '120px'
                  }}
                />
              </div>
            </div>

            {/* 弹窗图表区域 */}
            <div style={{ flex: 1, padding: '20px', overflow: 'hidden' }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={filteredData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
                  <CartesianGrid strokeDasharray="2 2" stroke="#e5e7eb" strokeOpacity={0.7} />
                  <XAxis
                    dataKey="time"
                    tick={{ fontSize: 11 }}
                    interval={Math.floor(filteredData.length / 20)}
                    angle={-45}
                    textAnchor="end"
                    height={50}
                    stroke="#6b7280"
                  />
                  <YAxis
                    tick={{ fontSize: 11 }}
                    label={{
                      value: viewType === 'electricity' ? 'Power (MW)' : 'Temperature (°C)',
                      angle: -90,
                      position: 'insideLeft',
                      style: { textAnchor: 'middle', fontSize: '12px' }
                    }}
                    domain={calculateYAxisDomain(filteredData, viewType === 'electricity' ? 'predictedPower' : 'predictedTemp')}
                    tickFormatter={(value) => Number(value).toFixed(1)}
                    stroke="#6b7280"
                  />
                  <Tooltip
                    content={({ active, payload, label }) => {
                      if (active && payload && payload.length) {
                        const data = payload[0].payload;
                        return (
                          <div style={{
                            backgroundColor: 'rgba(255, 255, 255, 0.98)',
                            border: '1px solid #d1d5db',
                            borderRadius: '8px',
                            padding: '12px 16px',
                            fontSize: '12px',
                            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
                            minWidth: '200px'
                          }}>
                            <p style={{ margin: '0 0 8px 0', fontWeight: 'bold', fontSize: '13px', color: '#1f2937' }}>
                              {label}
                            </p>
                            {viewType === 'electricity' ? (
                              <>
                                <p style={{ margin: '4px 0', color: '#3b82f6', display: 'flex', justifyContent: 'space-between' }}>
                                  <span>Predicted:</span>
                                  <span style={{ fontWeight: '600' }}>{data.predictedPower?.toFixed(2)} MW</span>
                                </p>
                                {data.actualPower !== null && (
                                  <p style={{ margin: '4px 0', color: '#ef4444', display: 'flex', justifyContent: 'space-between' }}>
                                    <span>Actual:</span>
                                    <span style={{ fontWeight: '600' }}>{data.actualPower?.toFixed(2)} MW</span>
                                  </p>
                                )}
                                {data.actualPower !== null && (
                                  <p style={{ margin: '4px 0', color: '#6b7280', display: 'flex', justifyContent: 'space-between' }}>
                                    <span>Difference:</span>
                                    <span style={{ fontWeight: '600' }}>
                                      {(data.actualPower - data.predictedPower).toFixed(2)} MW
                                    </span>
                                  </p>
                                )}
                              </>
                            ) : (
                              <p style={{ margin: '4px 0', color: '#059669', display: 'flex', justifyContent: 'space-between' }}>
                                <span>Temperature:</span>
                                <span style={{ fontWeight: '600' }}>{data.predictedTemp?.toFixed(1)}°C</span>
                              </p>
                            )}
                            {data.isTargetDay && (
                              <p style={{ margin: '8px 0 0 0', color: '#f59e0b', fontWeight: 'bold', fontSize: '11px', textAlign: 'center' }}>
                                🎯 Target Day
                              </p>
                            )}
                          </div>
                        );
                      }
                      return null;
                    }}
                  />

                  {viewType === 'electricity' ? (
                    <>
                      <Line
                        type="monotone"
                        dataKey="predictedPower"
                        stroke="#3b82f6"
                        strokeWidth={2}
                        dot={false}
                        activeDot={{ r: 4, stroke: '#3b82f6', strokeWidth: 2, fill: '#3b82f6' }}
                        name="Predicted Power"
                      />
                      <Line
                        type="monotone"
                        dataKey="actualPower"
                        stroke="#ef4444"
                        strokeWidth={2}
                        dot={false}
                        activeDot={{ r: 4, stroke: '#ef4444', strokeWidth: 2, fill: '#ef4444' }}
                        connectNulls={false}
                        name="Actual Power"
                      />
                      <ReferenceLine
                        x="1/7 00:00"
                        stroke="#f59e0b"
                        strokeDasharray="4 4"
                        strokeWidth={2}
                        label={{ value: "Target Day", position: "top" }}
                      />
                    </>
                  ) : (
                    <Line
                      type="monotone"
                      dataKey="predictedTemp"
                      stroke="#059669"
                      strokeWidth={2}
                      dot={false}
                      activeDot={{ r: 4, stroke: '#059669', strokeWidth: 2, fill: '#059669' }}
                      name="Temperature"
                    />
                  )}
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DataAnalysis;
