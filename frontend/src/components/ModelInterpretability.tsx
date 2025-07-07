import React, { useState, useEffect, useMemo, useRef } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
  ScatterChart,
  Scatter,
  Cell
} from 'recharts';
import { Brain, TrendingUp, Clock, Thermometer, Calendar, Hash, Maximize2, X } from 'lucide-react';
import { useUser } from '../context/UserContext';

// Declare global Plotly from CDN
declare global {
  interface Window {
    Plotly: any;
  }
}

interface ModelInterpretabilityProps {
  className?: string;
}

interface FeatureImportance {
  feature: string;
  feature_chinese: string;
  importance: number;
  rank: number;
}

interface DependencePoint {
  feature_value: number;
  shap_value: number;
  sample_index?: number;
  hour?: number;
  time?: string;
  context?: string;
}

interface FeatureDependence {
  feature: string;
  feature_chinese: string;
  data_points: DependencePoint[];
  value_range: { min: number; max: number };
  shap_range: { min: number; max: number };
  total_points: number;
  unique_values?: number;
}

interface ThreeDVisualizationData {
  title: string;
  x_axis: {
    name: string;
    values: number[];
    labels: string[];
  };
  y_axis: {
    name: string;
    values: number[];
    labels: string[];
  };
  z_axis: {
    name: string;
    power_demand_matrix: number[][];
    shap_effect_matrix: number[][];
  };
  metadata: {
    fixed_features: Record<string, any>;
    description: string;
  };
}

interface LIMEHourlyExplanation {
  hour: number;
  time: string;
  prediction: number;
  feature_contributions: {
    [key: string]: {
      contribution: number;
      feature_value: number;
      feature_chinese: string;
    };
  };
  sorted_contributions: Array<{
    feature: string;
    feature_chinese: string;
    contribution: number;
    feature_value: number;
    abs_contribution: number;
  }>;
  explanation_text: string;
}

interface LIMEData {
  hourly_explanations: LIMEHourlyExplanation[];
  feature_importance_by_hour: {
    [key: string]: number[];
  };
  summary: {
    total_hours: number;
    features: string[];
    features_chinese: string[];
  };
}

interface SHAPData {
  metadata: {
    date: string;
    description: string;
    features: string[];
    features_chinese: string[];
    base_prediction: number;
    total_hours: number;
  };
  shap_analysis: {
    feature_importance: FeatureImportance[];
    feature_dependence: {
      [key: string]: FeatureDependence;
    };
  };
  lime_analysis: LIMEData;
}

const ModelInterpretability: React.FC<ModelInterpretabilityProps> = ({ className = '' }) => {
  const [shapData, setSHAPData] = useState<SHAPData | null>(null);
  const [selectedMethod, setSelectedMethod] = useState<'SHAP' | 'LIME'>('SHAP');
  const [selectedSHAPView, setSelectedSHAPView] = useState<'importance' | 'dependence'>('importance');
  const [selectedFeature, setSelectedFeature] = useState<string>('Hour');
  const [selectedHour, setSelectedHour] = useState<number>(0);
  const [threeDData, setThreeDData] = useState<Record<string, ThreeDVisualizationData>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // 使用UserContext记录交互
  const { recordViewChange, recordButtonClick, recordModalInteraction, recordInputInteraction } = useUser();

  const plotRef = useRef<HTMLDivElement>(null);
  const modalPlotRef = useRef<HTMLDivElement>(null);

  // Helper function to convert Chinese feature names to English
  const getEnglishFeatureName = (chineseName: string) => {
    const featureMap: { [key: string]: string } = {
      '小时': 'Hour',
      '温度': 'Temperature',
      '星期': 'Day of Week',
      '周数': 'Week of Month'
    };
    return featureMap[chineseName] || chineseName;
  };

  // Helper function to generate English explanation text
  const generateEnglishExplanation = (hourData: LIMEHourlyExplanation) => {
    const positiveFeatures = hourData.sorted_contributions
      .filter(c => c.contribution > 0)
      .map(c => `${getEnglishFeatureName(c.feature_chinese)} (+${c.contribution.toFixed(1)})`);

    const negativeFeatures = hourData.sorted_contributions
      .filter(c => c.contribution < 0)
      .map(c => `${getEnglishFeatureName(c.feature_chinese)} (${c.contribution.toFixed(1)})`);

    let explanation = `At ${hourData.hour}:00, `;

    if (positiveFeatures.length > 0) {
      explanation += `${positiveFeatures[0].split(' ')[0]} contributes most to increasing power demand (${positiveFeatures[0].match(/\([^)]+\)/)?.[0]})`;
      if (negativeFeatures.length > 0) {
        explanation += `, while ${negativeFeatures[0].split(' ')[0]} contributes most to decreasing demand (${negativeFeatures[0].match(/\([^)]+\)/)?.[0]})`;
      }
    } else if (negativeFeatures.length > 0) {
      explanation += `${negativeFeatures[0].split(' ')[0]} contributes most to decreasing power demand (${negativeFeatures[0].match(/\([^)]+\)/)?.[0]})`;
    }

    return explanation + '.';
  };

  // Load SHAP data
  useEffect(() => {
    const loadSHAPData = async () => {
      try {
        setLoading(true);
        const response = await fetch('/data/shap_data_complete.json');
        if (!response.ok) {
          throw new Error('Failed to load SHAP data');
        }
        const data = await response.json();
        setSHAPData(data);
        setError(null);
      } catch (err) {
        console.error('Error loading SHAP data:', err);
        setError('Unable to load SHAP data');
      } finally {
        setLoading(false);
      }
    };

    loadSHAPData();
  }, []);

  // Load 3D visualization data for SHAP interaction analysis
  useEffect(() => {
    const load3DData = async () => {
      try {
        const datasets = ['temperature_hour', 'day_of_week_hour', 'week_of_month_hour'];
        const loadedData: Record<string, ThreeDVisualizationData> = {};

        for (const dataset of datasets) {
          const response = await fetch(`/data/${dataset}_3d.json`);
          if (response.ok) {
            loadedData[dataset] = await response.json();
          }
        }

        setThreeDData(loadedData);
      } catch (err) {
        console.error('Failed to load 3D data:', err);
      }
    };

    load3DData();
  }, []);

  // Function to create 3D plot
  const create3DPlot = (container: HTMLDivElement, isModal = false) => {
    if (!window.Plotly) return;

    const is3DFeature = ['Temperature_Hour', 'Day_of_Week_Hour', 'Week_of_Month_Hour'].includes(selectedFeature);
    if (!is3DFeature) return;

    const get3DDataKey = () => {
      switch (selectedFeature) {
        case 'Temperature_Hour': return 'temperature_hour';
        case 'Day_of_Week_Hour': return 'day_of_week_hour';
        case 'Week_of_Month_Hour': return 'week_of_month_hour';
        default: return null;
      }
    };

    const dataKey = get3DDataKey();
    if (!dataKey || !threeDData[dataKey]) return;

    const data = threeDData[dataKey];
    const matrix = data.z_axis.shap_effect_matrix;
    const xValues = data.x_axis.values;
    const yValues = data.y_axis.values;
    const xLabels = data.x_axis.labels;
    const yLabels = data.y_axis.labels;

    const plotData = [{
      type: 'surface',
      x: xValues,
      y: yValues,
      z: matrix,
      colorscale: [
        [0, '#3B82F6'],
        [0.25, '#06B6D4'],
        [0.5, '#10B981'],
        [0.75, '#F59E0B'],
        [1, '#EF4444']
      ],
      showscale: true,
      colorbar: {
        title: 'SHAP Effect (MW)',
        titleside: 'right',
        orientation: 'v',
        thickness: isModal ? 20 : 15,
        len: 0.9,
        x: 1.02,
        tickfont: { size: isModal ? 14 : 12 }
      },
      hovertemplate:
        '<b>%{text}</b><br>' +
        data.x_axis.name + ': %{customdata[0]}<br>' +
        data.y_axis.name + ': %{customdata[1]}<br>' +
        'SHAP Effect: %{z:.2f} MW<br>' +
        '<extra></extra>',
      text: matrix.map((row, i) =>
        row.map((_, j) => `${yLabels[i]} × ${xLabels[j]}`)
      ),
      customdata: matrix.map((row, i) =>
        row.map((_, j) => [xLabels[j], yLabels[i]])
      )
    }];

    const layout = {
      title: {
        text: `${data.title}`,
        font: { size: isModal ? 18 : 14 },
        x: 0.5,
        xanchor: 'center'
      },
      scene: {
        xaxis: {
          title: data.x_axis.name,
          tickmode: 'array',
          tickvals: xValues,
          ticktext: xLabels,
          titlefont: { size: isModal ? 16 : 12 },
          tickfont: { size: isModal ? 12 : 10 }
        },
        yaxis: {
          title: data.y_axis.name,
          tickmode: 'array',
          tickvals: yValues,
          ticktext: yLabels,
          titlefont: { size: isModal ? 16 : 12 },
          tickfont: { size: isModal ? 12 : 10 }
        },
        zaxis: {
          title: 'SHAP Effect (MW)',
          titlefont: { size: isModal ? 16 : 12 },
          tickfont: { size: isModal ? 12 : 10 }
        },
        camera: {
          eye: { x: 1.5, y: 1.5, z: 1.2 }
        }
      },
      margin: { l: 0, r: isModal ? 140 : 120, t: isModal ? 60 : 40, b: 0 },
      autosize: true
    };

    const config = {
      displayModeBar: true,
      modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
      displaylogo: false,
      responsive: true
    };

    window.Plotly.newPlot(container, plotData, layout, config);
  };

  // Enhanced 3D plot rendering for regular display
  useEffect(() => {
    if (!plotRef.current || selectedMethod !== 'SHAP') return;
    create3DPlot(plotRef.current, false);

    return () => {
      if (plotRef.current) {
        window.Plotly.purge(plotRef.current);
      }
    };
  }, [selectedFeature, selectedMethod, threeDData]);

  // Modal 3D plot rendering
  useEffect(() => {
    if (!modalPlotRef.current || !showModal) return;

    // 延迟一点确保模态框完全显示
    const timer = setTimeout(() => {
      if (modalPlotRef.current) {
        create3DPlot(modalPlotRef.current, true);
      }
    }, 100);

    return () => {
      clearTimeout(timer);
      if (modalPlotRef.current) {
        window.Plotly.purge(modalPlotRef.current);
      }
    };
  }, [showModal, selectedFeature, threeDData]);

  // 键盘事件监听
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isModalOpen) {
        setIsModalOpen(false);
        // 记录ESC键关闭模态框
        recordModalInteraction('ModelInterpretability', 'close', 'fullscreen_view');
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

  // Process feature dependence data
  const processedDependenceData = useMemo(() => {
    if (!shapData || selectedMethod !== 'SHAP' || !shapData.shap_analysis.feature_dependence[selectedFeature]) {
      return [];
    }

    const featureData = shapData.shap_analysis.feature_dependence[selectedFeature];
    const points = featureData.data_points;

    if (selectedFeature === 'Day_of_Week') {
      const dayGroups: { [key: number]: number[] } = {};
      points.forEach(point => {
        const day = point.feature_value;
        if (!dayGroups[day]) dayGroups[day] = [];
        dayGroups[day].push(point.shap_value);
      });

      const dayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
      return Object.keys(dayGroups).map(day => ({
        name: dayNames[parseInt(day)],
        value: parseInt(day),
        shap_value: dayGroups[parseInt(day)].reduce((a, b) => a + b, 0) / dayGroups[parseInt(day)].length
      }));
    } else if (selectedFeature === 'Week_of_Month') {
      const weekGroups: { [key: number]: number[] } = {};
      points.forEach(point => {
        const week = point.feature_value;
        if (!weekGroups[week]) weekGroups[week] = [];
        weekGroups[week].push(point.shap_value);
      });

      return Object.keys(weekGroups).map(week => ({
        name: `Week ${week}`,
        value: parseInt(week),
        shap_value: weekGroups[parseInt(week)].reduce((a, b) => a + b, 0) / weekGroups[parseInt(week)].length
      }));
    } else if (selectedFeature === 'Hour') {
      const hourGroups: { [key: number]: number[] } = {};
      points.forEach(point => {
        const hour = point.feature_value;
        if (!hourGroups[hour]) hourGroups[hour] = [];
        hourGroups[hour].push(point.shap_value);
      });

      return Object.keys(hourGroups).sort((a, b) => parseInt(a) - parseInt(b)).map(hour => ({
        name: `${hour}:00`,
        value: parseInt(hour),
        shap_value: hourGroups[parseInt(hour)].reduce((a, b) => a + b, 0) / hourGroups[parseInt(hour)].length
      }));
    } else {
      return points.map(point => ({
        name: `${point.feature_value.toFixed(1)}°C`,
        value: point.feature_value,
        shap_value: point.shap_value
      }));
    }
  }, [shapData, selectedFeature]);

  // Process LIME data
  const processedLIMEData = useMemo(() => {
    if (!shapData || selectedMethod !== 'LIME') {
      return [];
    }

    const hourData = shapData.lime_analysis.hourly_explanations.find(exp => exp.hour === selectedHour);
    if (!hourData) return [];

    return hourData.sorted_contributions.map(contrib => ({
      name: getEnglishFeatureName(contrib.feature_chinese),
      value: contrib.feature_value,
      contribution: contrib.contribution,
      feature: contrib.feature
    }));
  }, [shapData, selectedMethod, selectedHour]);

  // Get chart colors
  const getBarColor = (value: number) => {
    return value >= 0 ? '#10B981' : '#EF4444';
  };

  // Check if current feature is 3D
  const is3DFeature = () => {
    return ['Temperature_Hour', 'Day_of_Week_Hour', 'Week_of_Month_Hour'].includes(selectedFeature);
  };

  // Compact feature importance rendering
  const renderFeatureImportance = () => {
    if (!shapData) return null;

    if (selectedMethod === 'SHAP') {
      return (
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-gray-700 flex items-center">
            <TrendingUp className="w-4 h-4 mr-1" />
            Global Feature Importance
          </h3>
          <div className="grid grid-cols-1 gap-2">
            {shapData.shap_analysis.feature_importance.map((item, index) => (
              <div key={item.feature} className="flex items-center justify-between py-2 px-3 bg-gray-50 rounded text-sm">
                <div className="flex items-center">
                  <span className="w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-xs font-bold mr-2">
                    {index + 1}
                  </span>
                  <span className="text-gray-700">{getEnglishFeatureName(item.feature_chinese)}</span>
                </div>
                <div className="text-right">
                  <div className="font-semibold text-gray-800">{item.importance.toFixed(1)} MW</div>
                  <div className="text-xs text-gray-500">Impact Score</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      );
    } else {
      const hourData = shapData.lime_analysis.hourly_explanations.find(exp => exp.hour === selectedHour);
      if (!hourData) return null;

      return (
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-gray-700 flex items-center">
            <Clock className="w-4 h-4 mr-1" />
            Local Feature Contributions at {selectedHour}:00
          </h3>
          <div className="grid grid-cols-1 gap-2">
            {hourData.sorted_contributions.map((item, index) => (
              <div key={item.feature} className="flex items-center justify-between py-2 px-3 bg-gray-50 rounded text-sm">
                <div className="flex items-center">
                  <span className="w-6 h-6 bg-gray-400 text-white rounded-full flex items-center justify-center text-xs font-bold mr-2">
                    {index + 1}
                  </span>
                  <span className="text-gray-700">{getEnglishFeatureName(item.feature_chinese)}</span>
                </div>
                <div className={`font-semibold ${item.contribution >= 0 ? 'text-red-600' : 'text-blue-600'}`}>
                  {item.contribution >= 0 ? '+' : ''}{item.contribution.toFixed(1)} MW
                </div>
              </div>
            ))}
          </div>
        </div>
      );
    }
  };

  // Compact feature tabs
  const renderFeatureTabs = () => {
    if (!shapData || selectedMethod !== 'SHAP') return null;

    const features = [
      { key: 'Hour', name: 'Hour', icon: Clock },
      { key: 'Temperature_Hour', name: 'Temp×Hour', icon: Thermometer },
      { key: 'Day_of_Week_Hour', name: 'Day×Hour', icon: Calendar },
      { key: 'Week_of_Month_Hour', name: 'Week×Hour', icon: Hash }
    ];

    return (
      <div className="flex border-b border-gray-200 mb-3 justify-between items-center">
        <div className="flex">
          {features.map(({ key, name, icon: Icon }) => (
            <button
              key={key}
              onClick={() => {
                const previousFeature = selectedFeature;
                setSelectedFeature(key);

                // 记录特征标签页切换交互
                recordViewChange(
                  'ModelInterpretability',
                  'feature_tab',
                  key,
                  previousFeature
                );
              }}
              className={`flex items-center px-3 py-2 text-xs font-medium border-b-2 transition-colors ${
                selectedFeature === key
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <Icon className="w-3 h-3 mr-1" />
              {name}
            </button>
          ))}
        </div>
        
        {/* 放大按钮 - 只在3D特征时显示 */}
        {is3DFeature() && (
          <button
            onClick={() => {
              setShowModal(true);
              // 记录3D可视化放大按钮点击
              recordModalInteraction('ModelInterpretability', 'open', '3d_visualization');
            }}
            className="flex items-center px-3 py-1 text-xs font-medium bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
            title="Enlarge 3D Visualization"
          >
            <Maximize2 className="w-3 h-3 mr-1" />
            Enlarge
          </button>
        )}
      </div>
    );
  };

  // Full-width chart rendering with improved space utilization
  const renderDependenceChart = () => {
    if (selectedMethod === 'LIME') {
      if (!processedLIMEData.length) return null;

      return (
        <div className="h-48">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={processedLIMEData} layout="vertical" margin={{ left: 60, right: 10, top: 10, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis type="number" tickFormatter={(value) => `${value.toFixed(0)} MW`} fontSize={10} />
              <YAxis type="category" dataKey="name" fontSize={10} width={50} />
              <Tooltip formatter={(value: number) => [`${value.toFixed(1)} MW`, 'LIME Contribution']} />
              <Bar dataKey="contribution">
                {processedLIMEData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getBarColor(entry.contribution)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      );
    }

    // SHAP mode
    if (selectedFeature === 'Hour') {
      const chartData = processedDependenceData;
      if (!chartData.length) return null;

      return (
        <div className="h-48">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ left: 10, right: 10, top: 10, bottom: 40 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="name" fontSize={10} angle={-45} textAnchor="end" height={40} />
              <YAxis tickFormatter={(value) => `${value.toFixed(0)}`} fontSize={10} />
              <Tooltip formatter={(value: number) => [`${value.toFixed(1)} MW`, 'SHAP Value']} />
              <Bar dataKey="shap_value">
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getBarColor((entry as any).shap_value)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      );
    }

    // 3D visualizations - improved space utilization
    const get3DDataKey = () => {
      switch (selectedFeature) {
        case 'Temperature_Hour': return 'temperature_hour';
        case 'Day_of_Week_Hour': return 'day_of_week_hour';
        case 'Week_of_Month_Hour': return 'week_of_month_hour';
        default: return null;
      }
    };

    const dataKey = get3DDataKey();
    if (!dataKey || !threeDData[dataKey]) {
      return <div className="text-center py-8 text-gray-500 text-sm">Loading 3D data...</div>;
    }

    // 改进空间利用 - 减少预留空间
    return (
      <div style={{ height: 'calc(100% - 80px)', width: '100%' }}>
        <div ref={plotRef} style={{ width: '100%', height: '100%' }}></div>
      </div>
    );
  };

  // 3D可视化放大模态框
  const render3DModal = () => {
    if (!showModal) return null;

    return (
      <div
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          zIndex: 9999,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '20px'
        }}
        onClick={() => {
          setShowModal(false);
          // 记录3D可视化模态框关闭（背景点击）
          recordModalInteraction('ModelInterpretability', 'close', '3d_visualization');
        }}
      >
        <div
          style={{
            backgroundColor: 'white',
            borderRadius: '8px',
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
            width: '90vw',
            height: '80vh',
            maxWidth: '1200px',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden'
          }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* 模态框头部 */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '16px',
            borderBottom: '1px solid #e5e7eb'
          }}>
            <h3 style={{
              fontSize: '18px',
              fontWeight: '600',
              color: '#1f2937',
              margin: 0
            }}>
              3D SHAP Visualization - {threeDData[
                selectedFeature === 'Temperature_Hour' ? 'temperature_hour' :
                selectedFeature === 'Day_of_Week_Hour' ? 'day_of_week_hour' :
                'week_of_month_hour'
              ]?.title}
            </h3>
            <button
              onClick={() => {
                setShowModal(false);
                // 记录3D可视化模态框关闭（X按钮）
                recordModalInteraction('ModelInterpretability', 'close', '3d_visualization');
              }}
              style={{
                padding: '8px',
                backgroundColor: 'transparent',
                border: 'none',
                borderRadius: '50%',
                cursor: 'pointer',
                transition: 'background-color 0.2s',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f3f4f6'}
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
            >
              <X size={20} color="#6b7280" />
            </button>
          </div>

          {/* 3D图表容器 */}
          <div style={{ flex: 1, padding: '16px' }}>
            <div ref={modalPlotRef} style={{ width: '100%', height: '100%' }}></div>
          </div>

          {/* 模态框底部说明 */}
          <div style={{
            padding: '16px',
            borderTop: '1px solid #e5e7eb',
            backgroundColor: '#f9fafb'
          }}>
            <p style={{
              fontSize: '14px',
              color: '#6b7280',
              margin: 0,
              lineHeight: '1.5'
            }}>
              Interactive 3D surface showing SHAP interaction effects. Use mouse to rotate, zoom, and explore the visualization.
              Red areas indicate higher positive impact on power consumption, while blue areas show negative impact.
            </p>
          </div>
        </div>
      </div>
    );
  };

  // Compact LIME analysis
  const renderLIMEAnalysis = () => {
    if (!shapData) return null;

    const hourData = shapData.lime_analysis.hourly_explanations.find(exp => exp.hour === selectedHour);
    if (!hourData) return null;

    const positiveContributions = processedLIMEData.filter(item => item.contribution > 0);
    const negativeContributions = processedLIMEData.filter(item => item.contribution < 0);

    return (
      <div className="space-y-4">
        {/* Hour selection and prediction */}
        <div className="bg-blue-50 rounded p-3 border border-blue-200">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-800">LIME Local Explanation</h3>
            <select
              value={selectedHour}
              onChange={(e) => {
                const newHour = parseInt(e.target.value);
                setSelectedHour(newHour);

                // 记录LIME小时选择交互
                recordInputInteraction(
                  'ModelInterpretability',
                  'lime_hour_selector',
                  newHour.toString(),
                  'selected_hour'
                );
              }}
              className="px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              {Array.from({length: 24}, (_, i) => (
                <option key={i} value={i}>{i}:00</option>
              ))}
            </select>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-800">{hourData.prediction.toFixed(1)} MW</div>
            <p className="text-xs text-blue-600">Predicted power consumption at {selectedHour}:00</p>
          </div>
        </div>

        {/* Feature contributions */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-green-50 rounded p-3 border border-green-200">
            <div className="flex items-center mb-2">
              <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
              <h4 className="text-sm font-medium text-green-800">Positive Impact</h4>
            </div>
            {positiveContributions.length > 0 ? (
              <div className="space-y-2">
                {positiveContributions.slice(0, 3).map((item) => (
                  <div key={item.feature} className="flex items-center justify-between text-xs">
                    <span className="text-gray-700">{item.name}</span>
                    <span className="font-medium text-green-700">+{item.contribution.toFixed(1)}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-gray-500 italic">No positive factors</p>
            )}
          </div>

          <div className="bg-red-50 rounded p-3 border border-red-200">
            <div className="flex items-center mb-2">
              <div className="w-3 h-3 bg-red-500 rounded-full mr-2"></div>
              <h4 className="text-sm font-medium text-red-800">Negative Impact</h4>
            </div>
            {negativeContributions.length > 0 ? (
              <div className="space-y-2">
                {negativeContributions.slice(0, 3).map((item) => (
                  <div key={item.feature} className="flex items-center justify-between text-xs">
                    <span className="text-gray-700">{item.name}</span>
                    <span className="font-medium text-red-700">{item.contribution.toFixed(1)}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-gray-500 italic">No negative factors</p>
            )}
          </div>
        </div>

        {/* Chart */}
        {renderDependenceChart()}

        {/* Explanation */}
        <div className="bg-gray-50 rounded p-3 border border-gray-200">
          <h4 className="text-sm font-medium text-gray-800 mb-1">Model Decision Explanation</h4>
          <p className="text-xs text-gray-600">{generateEnglishExplanation(hourData)}</p>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className={`module-box ${className}`}>
        <div className="flex items-center justify-center h-full">
          <div className="text-gray-500 text-sm">Loading...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`module-box ${className}`}>
        <div className="flex items-center justify-center h-full">
          <div className="text-red-500 text-sm">{error}</div>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className={`module-box ${className}`} style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <div className="flex items-center justify-between mb-3" style={{ flexShrink: 0 }}>
          <div className="flex items-center">
            <Brain className="w-5 h-5 text-blue-600 mr-2" />
            <h2 className="module-title">Model Interpretability Analysis</h2>
          </div>
          <div className="flex items-center space-x-3">
            <label className="text-xs text-gray-600">Analysis Method:</label>
            <select
              value={selectedMethod}
              onChange={(e) => {
                const newMethod = e.target.value as 'SHAP' | 'LIME';
                const previousMethod = selectedMethod;
                setSelectedMethod(newMethod);

                // 记录分析方法切换交互
                recordViewChange(
                  'ModelInterpretability',
                  'analysis_method',
                  newMethod,
                  previousMethod
                );
              }}
              className="px-2 py-1 border border-gray-300 rounded text-xs focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="SHAP">SHAP - Global Analysis</option>
              <option value="LIME">LIME - Local Explanation</option>
            </select>
            <button
              onClick={() => {
                setIsModalOpen(true);
                // 记录主模态框打开
                recordModalInteraction('ModelInterpretability', 'open', 'fullscreen_view');
              }}
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
        </div>

        {/* SHAP sub-selection */}
        {selectedMethod === 'SHAP' && (
          <div className="flex items-center justify-between mb-3" style={{ flexShrink: 0 }}>
            <label className="text-xs text-gray-600">View Type:</label>
            <div className="flex space-x-2">
              <button
                onClick={() => {
                  const previousView = selectedSHAPView;
                  setSelectedSHAPView('importance');

                  // 记录SHAP视图切换交互
                  recordViewChange(
                    'ModelInterpretability',
                    'shap_view_type',
                    'importance',
                    previousView
                  );
                }}
                className={`px-3 py-1 text-xs font-medium rounded transition-colors ${
                  selectedSHAPView === 'importance'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
                }`}
              >
                Feature Importance
              </button>
              <button
                onClick={() => {
                  const previousView = selectedSHAPView;
                  setSelectedSHAPView('dependence');

                  // 记录SHAP视图切换交互
                  recordViewChange(
                    'ModelInterpretability',
                    'shap_view_type',
                    'dependence',
                    previousView
                  );
                }}
                className={`px-3 py-1 text-xs font-medium rounded transition-colors ${
                  selectedSHAPView === 'dependence'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
                }`}
              >
                Feature Dependence
              </button>
            </div>
          </div>
        )}

        {/* Feature tabs for SHAP dependence view */}
        {selectedMethod === 'SHAP' && selectedSHAPView === 'dependence' && renderFeatureTabs()}

        {/* Content */}
        <div className="flex-1 overflow-hidden">
          {selectedMethod === 'SHAP' && selectedSHAPView === 'importance' && (
            <div className="h-full overflow-auto">
              {renderFeatureImportance()}
            </div>
          )}
          {selectedMethod === 'SHAP' && selectedSHAPView === 'dependence' && (
            <div className="h-full">
              {renderDependenceChart()}
            </div>
          )}
          {selectedMethod === 'LIME' && (
            <div className="h-full overflow-auto">
              {renderLIMEAnalysis()}
            </div>
          )}
        </div>
      </div>

      {/* 3D放大模态框 */}
      {render3DModal()}

      {/* 完整模态弹窗 */}
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
          onClick={() => {
            setIsModalOpen(false);
            // 记录主模态框关闭（背景点击）
            recordModalInteraction('ModelInterpretability', 'close', 'fullscreen_view');
          }}
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
                Model Interpretability Analysis - Detailed View
              </h2>
              <button
                onClick={() => {
                  setIsModalOpen(false);
                  // 记录主模态框关闭（X按钮）
                  recordModalInteraction('ModelInterpretability', 'close', 'fullscreen_view');
                }}
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

            {/* 弹窗控制区域 */}
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              padding: '12px 20px',
              borderBottom: '1px solid #e5e7eb',
              flexShrink: 0,
              backgroundColor: '#f9fafb'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <label style={{ fontSize: '14px', color: '#6b7280' }}>Analysis Method:</label>
                <select
                  value={selectedMethod}
                  onChange={(e) => {
                    const newMethod = e.target.value as 'SHAP' | 'LIME';
                    const previousMethod = selectedMethod;
                    setSelectedMethod(newMethod);

                    // 记录分析方法切换交互（模态框中）
                    recordViewChange(
                      'ModelInterpretability',
                      'analysis_method_modal',
                      newMethod,
                      previousMethod
                    );
                  }}
                  style={{
                    fontSize: '14px',
                    padding: '6px 8px',
                    border: '1px solid #d1d5db',
                    borderRadius: '4px',
                    minWidth: '180px'
                  }}
                >
                  <option value="SHAP">SHAP - Global Analysis</option>
                  <option value="LIME">LIME - Local Explanation</option>
                </select>
              </div>

              {selectedMethod === 'SHAP' && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <label style={{ fontSize: '14px', color: '#6b7280' }}>View Type:</label>
                  <div style={{ display: 'flex', gap: '4px' }}>
                    <button
                      onClick={() => setSelectedSHAPView('importance')}
                      style={{
                        padding: '6px 12px',
                        fontSize: '14px',
                        border: 'none',
                        borderRadius: '6px',
                        backgroundColor: selectedSHAPView === 'importance' ? '#3b82f6' : '#f3f4f6',
                        color: selectedSHAPView === 'importance' ? 'white' : '#6b7280',
                        cursor: 'pointer',
                        transition: 'all 0.2s'
                      }}
                    >
                      Feature Importance
                    </button>
                    <button
                      onClick={() => setSelectedSHAPView('dependence')}
                      style={{
                        padding: '6px 12px',
                        fontSize: '14px',
                        border: 'none',
                        borderRadius: '6px',
                        backgroundColor: selectedSHAPView === 'dependence' ? '#3b82f6' : '#f3f4f6',
                        color: selectedSHAPView === 'dependence' ? 'white' : '#6b7280',
                        cursor: 'pointer',
                        transition: 'all 0.2s'
                      }}
                    >
                      Feature Dependence
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Feature tabs for SHAP dependence view */}
            {selectedMethod === 'SHAP' && selectedSHAPView === 'dependence' && (
              <div style={{
                padding: '12px 20px',
                borderBottom: '1px solid #e5e7eb',
                flexShrink: 0,
                backgroundColor: '#f9fafb'
              }}>
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                  {[
                    { key: 'Hour', name: 'Hour', icon: Clock },
                    { key: 'Temperature_Hour', name: 'Temp×Hour', icon: Thermometer },
                    { key: 'Day_of_Week_Hour', name: 'Day×Hour', icon: Calendar },
                    { key: 'Week_of_Month_Hour', name: 'Week×Hour', icon: Hash }
                  ].map(({ key, name, icon: Icon }) => (
                    <button
                      key={key}
                      onClick={() => {
                        const previousFeature = selectedFeature;
                        setSelectedFeature(key);

                        // 记录特征标签页切换交互（模态框中）
                        recordViewChange(
                          'ModelInterpretability',
                          'feature_tab_modal',
                          key,
                          previousFeature
                        );
                      }}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        padding: '8px 12px',
                        fontSize: '14px',
                        border: 'none',
                        borderRadius: '6px',
                        backgroundColor: selectedFeature === key ? '#3b82f6' : '#f3f4f6',
                        color: selectedFeature === key ? 'white' : '#6b7280',
                        cursor: 'pointer',
                        transition: 'all 0.2s'
                      }}
                    >
                      <Icon size={16} />
                      {name}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* 弹窗内容区域 */}
            <div style={{ flex: 1, padding: '20px', overflow: 'auto' }}>
              {selectedMethod === 'SHAP' && selectedSHAPView === 'importance' && (
                <div style={{ height: '100%' }}>
                  {renderFeatureImportance()}
                </div>
              )}
              {selectedMethod === 'SHAP' && selectedSHAPView === 'dependence' && (
                <div style={{ height: '100%' }}>
                  {renderDependenceChart()}
                </div>
              )}
              {selectedMethod === 'LIME' && (
                <div style={{ height: '100%' }}>
                  {renderLIMEAnalysis()}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default ModelInterpretability;