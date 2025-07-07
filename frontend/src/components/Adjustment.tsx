import React, { useState, useEffect } from 'react';

import type { GlobalAdjustment, LocalAdjustment, PredictionResult } from '../types/index.js';
import ApiService from '../services/api';

interface AdjustmentProps {
  className?: string;
  predictions?: PredictionResult[];
  onAdjustmentApplied?: (adjustedPredictions: PredictionResult[]) => void;
}

const Adjustment: React.FC<AdjustmentProps> = ({ 
  className = '', 
  predictions = [],
  onAdjustmentApplied 
}) => {
  const [adjustmentType, setAdjustmentType] = useState<'global' | 'local'>('global');
  const [globalAdjustment, setGlobalAdjustment] = useState<GlobalAdjustment>({
    start_hour: 9,
    end_hour: 17,
    direction: 'increase',
    percentage: 10
  });
  const [localAdjustments, setLocalAdjustments] = useState<LocalAdjustment[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [adjustmentHistory, setAdjustmentHistory] = useState<any[]>([]);

  useEffect(() => {
    loadAdjustmentHistory();
  }, []);

  const loadAdjustmentHistory = async () => {
    try {
      const history = await ApiService.getAdjustmentHistory();
      setAdjustmentHistory(history.adjustments || []);
    } catch (err) {
      console.error('Error loading adjustment history:', err);
    }
  };

  const applyGlobalAdjustment = async () => {
    if (predictions.length === 0) {
      setError('No prediction data available');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const response = await ApiService.applyGlobalAdjustment(
        predictions,
        globalAdjustment
      );
      
      setSuccess('Global adjustment applied successfully');
      onAdjustmentApplied?.(response.adjusted_predictions);
      await loadAdjustmentHistory();
      
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError('Failed to apply global adjustment');
      console.error('Error applying global adjustment:', err);
    } finally {
      setLoading(false);
    }
  };

  const applyLocalAdjustment = async () => {
    if (localAdjustments.length === 0) {
      setError('请添加至少一个局部调整');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const response = await ApiService.applyLocalAdjustment(
        predictions,
        localAdjustments
      );
      
      setSuccess('局部调整应用成功');
      onAdjustmentApplied?.(response.adjusted_predictions);
      await loadAdjustmentHistory();
      
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError('应用局部调整失败');
      console.error('Error applying local adjustment:', err);
    } finally {
      setLoading(false);
    }
  };

  const resetAdjustments = async () => {
    try {
      setLoading(true);
      await ApiService.resetAdjustments();
      setLocalAdjustments([]);
      setSuccess('调整已重置');
      await loadAdjustmentHistory();
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError('重置调整失败');
      console.error('Error resetting adjustments:', err);
    } finally {
      setLoading(false);
    }
  };

  const addLocalAdjustment = () => {
    setLocalAdjustments([
      ...localAdjustments,
      { hour: 12, new_value: 3500 }
    ]);
  };

  const updateLocalAdjustment = (index: number, field: keyof LocalAdjustment, value: number) => {
    const updated = [...localAdjustments];
    updated[index] = { ...updated[index], [field]: value };
    setLocalAdjustments(updated);
  };

  const removeLocalAdjustment = (index: number) => {
    setLocalAdjustments(localAdjustments.filter((_, i) => i !== index));
  };

  return (
    <div className="module-box">
      <div className="module-title">Adjustment</div>

      {/* 优化的调整类型选择 - 统一字体至12px */}
      <div style={{ marginBottom: '15px', fontSize: '12px' }}>
        <div style={{ marginBottom: '8px', fontWeight: 'bold' }}>
          🔧 调整类型
        </div>
        <select
          value={adjustmentType}
          onChange={(e) => setAdjustmentType(e.target.value as 'global' | 'local')}
          style={{
            width: '100%',
            fontSize: '11px',
            padding: '6px',
            border: '1px solid #ccc',
            borderRadius: '4px',
            backgroundColor: '#fff'
          }}
        >
          <option value="global">🌐 全局调整</option>
          <option value="local">📍 局部调整</option>
        </select>
      </div>

      {/* 优化的全局调整 */}
      {adjustmentType === 'global' && (
        <div style={{ fontSize: '12px' }}>
          <div style={{ marginBottom: '12px', fontWeight: 'bold', color: '#495057' }}>
            🌐 全局调整设置
          </div>

          <div style={{ marginBottom: '10px' }}>
            <label style={{ display: 'block', marginBottom: '4px', fontSize: '11px', fontWeight: 'bold' }}>
              ⏰ 开始时间:
            </label>
            <select
              value={globalAdjustment.start_hour}
              onChange={(e) => setGlobalAdjustment({
                ...globalAdjustment,
                start_hour: parseInt(e.target.value)
              })}
              style={{
                width: '100%',
                fontSize: '11px',
                padding: '4px',
                border: '1px solid #ccc',
                borderRadius: '4px'
              }}
            >
              {Array.from({ length: 24 }, (_, i) => (
                <option key={i} value={i}>{i}:00</option>
              ))}
            </select>
          </div>

          <div style={{ marginBottom: '10px' }}>
            <label style={{ display: 'block', marginBottom: '4px', fontSize: '11px', fontWeight: 'bold' }}>
              ⏰ 结束时间:
            </label>
            <select
              value={globalAdjustment.end_hour}
              onChange={(e) => setGlobalAdjustment({
                ...globalAdjustment,
                end_hour: parseInt(e.target.value)
              })}
              style={{
                width: '100%',
                fontSize: '11px',
                padding: '4px',
                border: '1px solid #ccc',
                borderRadius: '4px'
              }}
            >
              {Array.from({ length: 24 }, (_, i) => (
                <option key={i} value={i}>{i}:00</option>
              ))}
            </select>
          </div>

          <div style={{ marginBottom: '10px' }}>
            <label style={{ display: 'block', marginBottom: '4px', fontSize: '11px', fontWeight: 'bold' }}>
              📈 调整方向:
            </label>
            <select
              value={globalAdjustment.direction}
              onChange={(e) => setGlobalAdjustment({
                ...globalAdjustment,
                direction: e.target.value as 'increase' | 'decrease'
              })}
              style={{
                width: '100%',
                fontSize: '11px',
                padding: '4px',
                border: '1px solid #ccc',
                borderRadius: '4px'
              }}
            >
              <option value="increase">📈 增加</option>
              <option value="decrease">📉 减少</option>
            </select>
          </div>

          <div style={{ marginBottom: '12px' }}>
            <label style={{ display: 'block', marginBottom: '4px', fontSize: '11px', fontWeight: 'bold' }}>
              📊 调整百分比:
            </label>
            <input
              type="number"
              min="1"
              max="50"
              value={globalAdjustment.percentage}
              onChange={(e) => setGlobalAdjustment({
                ...globalAdjustment,
                percentage: parseFloat(e.target.value)
              })}
              style={{
                width: '100%',
                fontSize: '11px',
                padding: '4px',
                border: '1px solid #ccc',
                borderRadius: '4px'
              }}
              placeholder="1-50%"
            />
          </div>

          <button
            onClick={applyGlobalAdjustment}
            disabled={loading}
            style={{
              width: '100%',
              fontSize: '11px',
              padding: '8px',
              backgroundColor: loading ? '#6c757d' : '#0066cc',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontWeight: 'bold'
            }}
          >
            {loading ? '⏳ 应用中...' : '✅ 应用全局调整'}
          </button>
        </div>
      )}

      {/* 优化的局部调整 */}
      {adjustmentType === 'local' && (
        <div style={{ fontSize: '12px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <div style={{ fontWeight: 'bold', color: '#495057' }}>
              📍 局部调整设置
            </div>
            <button
              onClick={addLocalAdjustment}
              style={{
                fontSize: '10px',
                padding: '4px 8px',
                backgroundColor: '#28a745',
                color: 'white',
                border: 'none',
                borderRadius: '3px',
                cursor: 'pointer'
              }}
            >
              ➕ 添加
            </button>
          </div>

          {localAdjustments.length === 0 ? (
            <div style={{
              textAlign: 'center',
              color: '#6c757d',
              padding: '20px',
              backgroundColor: '#f8f9fa',
              borderRadius: '6px',
              border: '1px dashed #dee2e6'
            }}>
              <div style={{ fontSize: '24px', marginBottom: '8px' }}>⚙️</div>
              <div style={{ marginBottom: '4px' }}>暂无局部调整</div>
              <div style={{ fontSize: '10px' }}>点击"添加"按钮开始设置</div>
            </div>
          ) : (
            <div style={{ marginBottom: '12px' }}>
              {localAdjustments.map((adjustment, index) => (
                <div key={index} style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '8px',
                  backgroundColor: '#f8f9fa',
                  borderRadius: '4px',
                  marginBottom: '6px',
                  border: '1px solid #e9ecef'
                }}>
                  <div style={{ flex: 1 }}>
                    <label style={{ display: 'block', fontSize: '10px', color: '#6c757d', marginBottom: '2px' }}>
                      时间
                    </label>
                    <select
                      value={adjustment.hour}
                      onChange={(e) => updateLocalAdjustment(index, 'hour', parseInt(e.target.value))}
                      style={{
                        width: '100%',
                        fontSize: '10px',
                        padding: '3px',
                        border: '1px solid #ccc',
                        borderRadius: '3px'
                      }}
                    >
                      {Array.from({ length: 24 }, (_, i) => (
                        <option key={i} value={i}>{i}:00</option>
                      ))}
                    </select>
                  </div>
                  <div style={{ flex: 1 }}>
                    <label style={{ display: 'block', fontSize: '10px', color: '#6c757d', marginBottom: '2px' }}>
                      新值 (MW)
                    </label>
                    <input
                      type="number"
                      value={adjustment.new_value}
                      onChange={(e) => updateLocalAdjustment(index, 'new_value', parseFloat(e.target.value))}
                      style={{
                        width: '100%',
                        fontSize: '10px',
                        padding: '3px',
                        border: '1px solid #ccc',
                        borderRadius: '3px'
                      }}
                    />
                  </div>
                  <button
                    onClick={() => removeLocalAdjustment(index)}
                    style={{
                      fontSize: '12px',
                      color: '#dc3545',
                      backgroundColor: 'transparent',
                      border: 'none',
                      cursor: 'pointer',
                      padding: '2px'
                    }}
                    title="删除"
                  >
                    ❌
                  </button>
                </div>
              ))}
            </div>
          )}

          {localAdjustments.length > 0 && (
            <button
              onClick={applyLocalAdjustment}
              disabled={loading}
              style={{
                width: '100%',
                fontSize: '11px',
                padding: '8px',
                backgroundColor: loading ? '#6c757d' : '#28a745',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: loading ? 'not-allowed' : 'pointer',
                fontWeight: 'bold'
              }}
            >
              {loading ? '⏳ 应用中...' : '✅ 应用局部调整'}
            </button>
          )}
        </div>
      )}

      {/* 优化的重置按钮和状态显示 */}
      <div style={{
        marginTop: '15px',
        paddingTop: '12px',
        borderTop: '1px solid #dee2e6'
      }}>
        <button
          onClick={resetAdjustments}
          disabled={loading}
          style={{
            width: '100%',
            fontSize: '11px',
            padding: '8px',
            backgroundColor: loading ? '#6c757d' : '#dc3545',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: loading ? 'not-allowed' : 'pointer',
            fontWeight: 'bold',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '4px'
          }}
        >
          🔄 {loading ? '重置中...' : '重置所有调整'}
        </button>
      </div>

      {/* 状态消息显示 */}
      {error && (
        <div style={{
          marginTop: '8px',
          padding: '6px',
          backgroundColor: '#f8d7da',
          color: '#721c24',
          borderRadius: '4px',
          fontSize: '10px',
          border: '1px solid #f5c6cb'
        }}>
          ❌ {error}
        </div>
      )}

      {success && (
        <div style={{
          marginTop: '8px',
          padding: '6px',
          backgroundColor: '#d4edda',
          color: '#155724',
          borderRadius: '4px',
          fontSize: '10px',
          border: '1px solid #c3e6cb'
        }}>
          ✅ {success}
        </div>
      )}

      {/* 调整历史 */}
      {adjustmentHistory.length > 0 && (
        <div style={{
          marginTop: '12px',
          paddingTop: '8px',
          borderTop: '1px solid #dee2e6'
        }}>
          <div style={{ fontSize: '11px', fontWeight: 'bold', marginBottom: '4px', color: '#495057' }}>
            📋 调整历史
          </div>
          <div style={{ fontSize: '10px', color: '#6c757d' }}>
            共 {adjustmentHistory.length} 次调整记录
          </div>
        </div>
      )}
    </div>
  );
};

export default Adjustment;
