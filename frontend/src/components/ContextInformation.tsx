import React, { useState, useEffect } from 'react';
import { Calendar, Thermometer, AlertTriangle, ChevronDown } from 'lucide-react';
import { useUser } from '../context/UserContext';
import type { WeatherInfo, SpecialEventInfo } from '../types/index.js';
import ApiService from '../services/api';

interface ContextInformationProps {
  className?: string;
}

const ContextInformation: React.FC<ContextInformationProps> = ({ className = '' }) => {
  const [weatherData, setWeatherData] = useState<WeatherInfo[]>([]);
  const [specialEventsData, setSpecialEventsData] = useState<SpecialEventInfo[]>([]);
  const [selectedView, setSelectedView] = useState<'weather' | 'events'>('weather');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 使用UserContext记录交互
  const { recordViewChange, recordInteraction } = useUser();

  useEffect(() => {
    loadContextData();

    // 记录组件加载交互
    recordInteraction(
      'ContextInformation',
      'component_loaded',
      { initialView: selectedView }
    );
  }, []);

  const loadContextData = async () => {
    try {
      setLoading(true);

      // Weather Information Data
      const weatherInfo: WeatherInfo[] = [
        { date: "2021-12-30", day_of_week: "Thu", max_temperature: "14.5 °C" },
        { date: "2021-12-31", day_of_week: "Fri", max_temperature: "6.0 °C" },
        { date: "2022-01-01", day_of_week: "Sat", max_temperature: "7.8 °C" },
        { date: "2022-01-02", day_of_week: "Sun", max_temperature: "7.9 °C" },
        { date: "2022-01-03", day_of_week: "Mon*", max_temperature: "10.5 °C" },
        { date: "2022-01-04", day_of_week: "Tue", max_temperature: "12.4 °C" },
        { date: "2022-01-05", day_of_week: "Wed", max_temperature: "8.7 °C" },
        { date: "2022-01-06", day_of_week: "Thu", max_temperature: "2.6 °C", special_note: "(Snow Day)" },
        { date: "2022-01-07", day_of_week: "Fri", max_temperature: "8.4 °C", special_note: "(Clear・Min -3.5 °C)" }
      ];

      // Special Events Information Data
      const specialEvents: SpecialEventInfo[] = [
        {
          date: "2022-01-03",
          event_summary: "Last day of New Year holidays; holiday return peak, temperature rises above 10°C, limited impact on electricity demand."
        },
        {
          date: "2022-01-04",
          event_summary: "First working day; JMA begins warning of possible snowfall on the 6th, power companies enter routine alert."
        },
        {
          date: "2022-01-05",
          event_summary: "Latest overnight numerical forecast shows increased probability of \"warning-level heavy snow\"; Tokyo metropolitan media intensively reminds of commuting risks on the 6th."
        },
        {
          date: "2022-01-06",
          event_summary: "16:00 Tokyo 23 wards issued first heavy snow warning in 4 years; 19:00 snow accumulation reached 10 cm. OCCTO twice ordered TEPCO to add 1.22 GW power supply to the wide-area market, peak demand-supply ratio around 97% at 17:00."
        },
        {
          date: "2022-01-07",
          event_summary: "(Warning) Early morning -3.5°C, road surface freezing; first trains and highways partially speed-limited. JMA continues \"road surface freezing caution\"."
        }
      ];

      setWeatherData(weatherInfo);
      setSpecialEventsData(specialEvents);
    } catch (err) {
      setError('Failed to load context information');
      console.error('Error loading context data:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="module-box">
        <div className="module-title">Context Information</div>
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-3/4 mb-3"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2 mb-3"></div>
          <div className="h-4 bg-gray-200 rounded w-2/3"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="module-box">
        <div className="module-title">Context Information</div>
        <div className="text-red-500" style={{ fontSize: '14px' }}>{error}</div>
      </div>
    );
  }

  return (
    <div className="module-box">
      <div className="flex items-center justify-between mb-4">
        <div className="module-title">Context Information</div>

        {/* Dropdown selector */}
        <div className="relative">
          <select
            value={selectedView}
            onChange={(e) => {
              const newValue = e.target.value as 'weather' | 'events';
              const previousValue = selectedView;
              setSelectedView(newValue);

              // 记录视图切换交互
              recordViewChange(
                'ContextInformation',
                'dropdown_selection',
                newValue,
                previousValue
              );
            }}
            className="px-3 py-1 text-xs border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
          >
            <option value="weather">Weather Information</option>
            <option value="events">Special Events Information</option>
          </select>
        </div>
      </div>

      {/* Content display based on selection */}
      <div style={{ fontSize: '12px', lineHeight: '1.6', height: '100%', overflowY: 'auto' }}>
        {selectedView === 'weather' ? (
          <div>
            <div style={{ fontWeight: 'bold', marginBottom: '12px', color: '#2563eb' }}>
              Weather Information
            </div>
            <div style={{ marginBottom: '8px', fontSize: '11px', color: '#6b7280' }}>
              * January 3rd is still the last day of the "Shogatsu Sanganichi" legal holiday period.
            </div>

            {/* Weather table */}
            <div style={{ border: '1px solid #e5e7eb', borderRadius: '4px', overflow: 'hidden' }}>
              <div style={{
                display: 'grid',
                gridTemplateColumns: '1fr 1fr 1fr',
                backgroundColor: '#f9fafb',
                padding: '8px',
                fontWeight: 'bold',
                fontSize: '11px',
                borderBottom: '1px solid #e5e7eb'
              }}>
                <div>Date</div>
                <div>Day of Week</div>
                <div>Daily Max Temperature</div>
              </div>

              {weatherData.map((item) => (
                <div key={item.date} style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr 1fr',
                  padding: '6px 8px',
                  borderBottom: '1px solid #f3f4f6',
                  fontSize: '11px'
                }}>
                  <div>{item.date}</div>
                  <div>{item.day_of_week}</div>
                  <div>
                    {item.max_temperature}
                    {item.special_note && (
                      <span style={{ color: '#dc2626', marginLeft: '4px' }}>
                        {item.special_note}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div>
            <div style={{ fontWeight: 'bold', marginBottom: '12px', color: '#dc2626' }}>
              Special Events Information
            </div>
            <div style={{ marginBottom: '12px', fontSize: '11px', color: '#6b7280' }}>
              (Social/meteorological events with significant impact on electricity demand or forecasting)
            </div>

            {specialEventsData.map((item) => (
              <div key={item.date} style={{ marginBottom: '10px' }}>
                <div style={{ fontWeight: 'bold', marginBottom: '4px', color: '#dc2626', fontSize: '12px' }}>
                  {item.date}
                </div>
                <div style={{ fontSize: '11px', lineHeight: '1.5', color: '#374151' }}>
                  {item.event_summary}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ContextInformation;
