import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { ArrowLeft } from 'lucide-react';
import realData from '../data/realData2022Jan7.json';

interface ExperimentResultsPageProps {
  userPredictions: any[];
  userAdjustments: any[];
  experimentData: any;
  onBack: () => void;
}

interface ChartData {
  hour: number;
  real_usage: number;
  user_prediction: number;
}

const ExperimentResultsPage: React.FC<ExperimentResultsPageProps> = ({
  userPredictions,
  userAdjustments,
  experimentData,
  onBack
}) => {
  const [chartData, setChartData] = useState<ChartData[]>([]);

  useEffect(() => {
    console.log('ExperimentResultsPage - Props received:');
    console.log('userPredictions:', userPredictions);
    console.log('userAdjustments:', userAdjustments);
    console.log('experimentData:', experimentData);

    prepareChartData();
  }, [userPredictions, userAdjustments]);

  const prepareChartData = () => {
    const data: ChartData[] = [];

    // 为每个小时创建数据点
    for (let hour = 0; hour < 24; hour++) {
      const realHourData = realData.data.find(d => d.hour === hour);
      const userHourData = userPredictions.find(d => d.hour === hour);

      if (realHourData && userHourData) {
        data.push({
          hour,
          real_usage: realHourData.actual_usage,
          user_prediction: userHourData.predicted_usage || userHourData.current_prediction || 0
        });
      }
    }

    console.log('Prepared chart data:', data);
    setChartData(data);
  };

  const formatValue = (value: number) => {
    return `${(value/1000).toFixed(1)}k MW`;
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        {/* 返回按钮 */}
        <button
          onClick={onBack}
          className="flex items-center text-blue-600 hover:text-blue-800 mb-8 transition-colors"
        >
          <ArrowLeft size={20} className="mr-2" />
          Back to Experiment
        </button>

        {/* 主标题 */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Your Predictions vs Reality
          </h1>
          <p className="text-gray-600">
            January 7, 2022 - 24 Hour Electricity Usage Comparison
          </p>
        </div>

        {/* 主图表 */}
        <div className="bg-white rounded-lg shadow-lg p-8">
          {/* 调试信息 */}
          <div className="mb-4 text-sm text-gray-600">
            Chart Data Points: {chartData.length}
            {chartData.length > 0 && (
              <span className="ml-4">
                Sample: Hour {chartData[0].hour}, Real: {chartData[0].real_usage}, User: {chartData[0].user_prediction}
              </span>
            )}
          </div>

          <div style={{ width: '100%', height: '400px', border: '1px solid #ddd', backgroundColor: '#f9f9f9' }}>
            {chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="hour" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="real_usage"
                    stroke="#ef4444"
                    strokeWidth={3}
                    name="Real Usage"
                  />
                  <Line
                    type="monotone"
                    dataKey="user_prediction"
                    stroke="#3b82f6"
                    strokeWidth={3}
                    name="Your Prediction"
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-full text-gray-500">
                Loading chart data...
              </div>
            )}
          </div>

          {/* 图例说明 */}
          <div className="mt-6 flex items-center justify-center space-x-8">
            <div className="flex items-center">
              <div className="w-6 h-1 bg-red-500 rounded mr-3"></div>
              <span className="text-gray-700 font-medium">Real Electricity Usage</span>
            </div>
            <div className="flex items-center">
              <div className="w-6 h-1 bg-blue-500 rounded mr-3"></div>
              <span className="text-gray-700 font-medium">Your Adjusted Prediction</span>
            </div>
          </div>
        </div>

        {/* 备用数据表格 - 如果图表不显示 */}
        {chartData.length > 0 && (
          <div className="bg-white rounded-lg shadow-lg p-8 mt-8">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Data Table (Backup View)</h2>
            <div className="grid grid-cols-6 gap-4 text-sm">
              {chartData.slice(0, 6).map((item) => (
                <div key={item.hour} className="text-center p-2 border rounded">
                  <div className="font-semibold">{item.hour}:00</div>
                  <div className="text-red-600">{formatValue(item.real_usage)}</div>
                  <div className="text-blue-600">{formatValue(item.user_prediction)}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ExperimentResultsPage;