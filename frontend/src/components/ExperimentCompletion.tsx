import React, { useState } from 'react';
import { CheckCircle, Download, Clock, BarChart3, AlertCircle } from 'lucide-react';
import { useUser } from '../context/UserContext';
import PredictionComparison from './PredictionComparison';
import type { UserExperimentData } from '../types/index.js';

interface ExperimentCompletionProps {
  experimentData: UserExperimentData;
  onComplete: () => Promise<void>;
  onCancel: () => void;
  currentPredictionData?: any[]; // 添加当前预测数据
}

interface ExperimentStats {
  totalDecisions: number;
  totalAdjustments: number;
  experimentDuration: string;
  adjustmentRange: { min: number; max: number };
  mostAdjustedHour: number;
}

const ExperimentCompletion: React.FC<ExperimentCompletionProps> = ({
  experimentData,
  onComplete,
  onCancel,
  currentPredictionData = []
}) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [showComparison, setShowComparison] = useState(false);

  // 使用UserContext记录交互
  const { recordButtonClick, recordInteraction } = useUser();

  // Calculate experiment statistics
  const calculateStats = (): ExperimentStats => {
    const startTime = new Date(experimentData.startTime);
    const endTime = new Date();
    const durationMs = endTime.getTime() - startTime.getTime();
    const durationMinutes = Math.floor(durationMs / (1000 * 60));
    const hours = Math.floor(durationMinutes / 60);
    const minutes = durationMinutes % 60;
    
    const durationStr = hours > 0 
      ? `${hours}h ${minutes}m` 
      : `${minutes}m`;

    // Calculate adjustment statistics
    const adjustmentValues = experimentData.adjustments.map(adj => 
      Math.abs(adj.adjustedValue - adj.originalValue)
    );
    
    const adjustmentRange = adjustmentValues.length > 0 
      ? {
          min: Math.min(...adjustmentValues),
          max: Math.max(...adjustmentValues)
        }
      : { min: 0, max: 0 };

    // Find most adjusted hour
    const hourCounts = experimentData.adjustments.reduce((acc, adj) => {
      acc[adj.hour] = (acc[adj.hour] || 0) + 1;
      return acc;
    }, {} as Record<number, number>);
    
    const mostAdjustedHour = Object.entries(hourCounts).reduce((max, [hour, count]) => 
      count > (hourCounts[max] || 0) ? parseInt(hour) : max, 0
    );

    return {
      totalDecisions: experimentData.decisions.length,
      totalAdjustments: experimentData.adjustments.length,
      experimentDuration: durationStr,
      adjustmentRange,
      mostAdjustedHour
    };
  };

  const stats = calculateStats();

  const handleSubmit = async () => {
    if (!showConfirmation) {
      setShowConfirmation(true);
      // 记录显示确认对话框
      recordInteraction(
        'ExperimentCompletion',
        'show_confirmation',
        { action: 'complete_experiment' }
      );
      return;
    }

    setIsSubmitting(true);
    setSubmitError(null);

    // 记录最终提交实验
    recordButtonClick('ExperimentCompletion', 'final_submit', 'Complete Experiment');

    try {
      await onComplete();
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : 'Failed to submit experiment data');
      setIsSubmitting(false);
    }
  };

  const handleCancel = () => {
    if (showConfirmation) {
      setShowConfirmation(false);
      // 记录取消确认
      recordButtonClick('ExperimentCompletion', 'cancel_confirmation', 'Back');
    } else {
      // 记录取消实验完成
      recordButtonClick('ExperimentCompletion', 'cancel_experiment', 'Cancel');
      onCancel();
    }
  };

  const exportData = () => {
    // 记录导出数据按钮点击
    recordButtonClick('ExperimentCompletion', 'export_data', 'Export Data');

    const dataStr = JSON.stringify(experimentData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);

    const link = document.createElement('a');
    link.href = url;
    link.download = `experiment_${experimentData.username}_${experimentData.sessionId}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    URL.revokeObjectURL(url);
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '20px'
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '12px',
        padding: '32px',
        maxWidth: '500px',
        width: '100%',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
      }}>
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '24px' }}>
          <div style={{
            width: '60px',
            height: '60px',
            backgroundColor: showConfirmation ? '#f59e0b' : '#10b981',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 16px'
          }}>
            {showConfirmation ? (
              <AlertCircle size={30} color="white" />
            ) : (
              <CheckCircle size={30} color="white" />
            )}
          </div>
          <h2 style={{
            margin: 0,
            fontSize: '24px',
            fontWeight: '600',
            color: '#1f2937',
            marginBottom: '8px'
          }}>
            {showConfirmation ? 'Confirm Experiment Completion' : 'Complete Experiment'}
          </h2>
          <p style={{
            margin: 0,
            fontSize: '14px',
            color: '#6b7280',
            lineHeight: '1.5'
          }}>
            {showConfirmation 
              ? 'Are you sure you want to complete the experiment? This action cannot be undone.'
              : 'Review your experiment data and submit your results'
            }
          </p>
        </div>

        {!showConfirmation && (
          <>
            {/* Experiment Statistics */}
            <div style={{
              backgroundColor: '#f9fafb',
              borderRadius: '8px',
              padding: '20px',
              marginBottom: '24px'
            }}>
              <h3 style={{
                margin: '0 0 16px 0',
                fontSize: '16px',
                fontWeight: '600',
                color: '#374151'
              }}>
                Experiment Summary
              </h3>
              
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <BarChart3 size={16} color="#6b7280" />
                  <div>
                    <div style={{ fontSize: '12px', color: '#6b7280' }}>Decisions Made</div>
                    <div style={{ fontSize: '16px', fontWeight: '600', color: '#1f2937' }}>
                      {stats.totalDecisions}
                    </div>
                  </div>
                </div>
                
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <BarChart3 size={16} color="#6b7280" />
                  <div>
                    <div style={{ fontSize: '12px', color: '#6b7280' }}>Adjustments Made</div>
                    <div style={{ fontSize: '16px', fontWeight: '600', color: '#1f2937' }}>
                      {stats.totalAdjustments}
                    </div>
                  </div>
                </div>
                
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Clock size={16} color="#6b7280" />
                  <div>
                    <div style={{ fontSize: '12px', color: '#6b7280' }}>Duration</div>
                    <div style={{ fontSize: '16px', fontWeight: '600', color: '#1f2937' }}>
                      {stats.experimentDuration}
                    </div>
                  </div>
                </div>
                
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <BarChart3 size={16} color="#6b7280" />
                  <div>
                    <div style={{ fontSize: '12px', color: '#6b7280' }}>Most Adjusted Hour</div>
                    <div style={{ fontSize: '16px', fontWeight: '600', color: '#1f2937' }}>
                      {stats.mostAdjustedHour}:00
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* User Information */}
            <div style={{
              backgroundColor: '#eff6ff',
              borderRadius: '8px',
              padding: '16px',
              marginBottom: '24px'
            }}>
              <div style={{ fontSize: '12px', color: '#1e40af', marginBottom: '4px' }}>
                Participant Information
              </div>
              <div style={{ fontSize: '14px', color: '#1e40af' }}>
                <strong>Username:</strong> {experimentData.username}<br />
                <strong>Session ID:</strong> {experimentData.sessionId}<br />
                <strong>Start Time:</strong> {new Date(experimentData.startTime).toLocaleString()}
              </div>
            </div>
          </>
        )}

        {/* Error Message */}
        {submitError && (
          <div style={{
            backgroundColor: '#fef2f2',
            border: '1px solid #fecaca',
            borderRadius: '8px',
            padding: '12px',
            marginBottom: '16px'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              color: '#dc2626',
              fontSize: '14px'
            }}>
              <AlertCircle size={16} />
              <span>{submitError}</span>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div style={{
          display: 'flex',
          gap: '12px',
          justifyContent: 'flex-end'
        }}>
          {!showConfirmation && (
            <button
              onClick={exportData}
              style={{
                padding: '10px 16px',
                fontSize: '14px',
                fontWeight: '500',
                color: '#6b7280',
                backgroundColor: 'white',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              <Download size={14} />
              Export Data
            </button>
          )}

          {/* 查看对比按钮 - 已禁用 */}
          {/*
          <button
            onClick={() => {
              setShowComparison(!showComparison);
              recordButtonClick('ExperimentCompletion', 'toggle_comparison', showComparison ? 'Hide Comparison' : 'Show Comparison');
            }}
            style={{
              padding: '10px 16px',
              fontSize: '14px',
              fontWeight: '500',
              color: '#8b5cf6',
              backgroundColor: 'white',
              border: '1px solid #8b5cf6',
              borderRadius: '6px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <BarChart3 size={14} />
            {showComparison ? 'Hide Comparison' : 'View vs Reality'}
          </button>
          */}

          <button
            onClick={handleCancel}
            disabled={isSubmitting}
            style={{
              padding: '10px 16px',
              fontSize: '14px',
              fontWeight: '500',
              color: '#6b7280',
              backgroundColor: 'white',
              border: '1px solid #d1d5db',
              borderRadius: '6px',
              cursor: isSubmitting ? 'not-allowed' : 'pointer'
            }}
          >
            {showConfirmation ? 'Back' : 'Cancel'}
          </button>
          
          <button
            onClick={handleSubmit}
            disabled={isSubmitting}
            style={{
              padding: '10px 20px',
              fontSize: '14px',
              fontWeight: '600',
              color: 'white',
              backgroundColor: isSubmitting ? '#9ca3af' : (showConfirmation ? '#dc2626' : '#3b82f6'),
              border: 'none',
              borderRadius: '6px',
              cursor: isSubmitting ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            {isSubmitting ? (
              <>
                <div style={{
                  width: '14px',
                  height: '14px',
                  border: '2px solid transparent',
                  borderTop: '2px solid white',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite'
                }} />
                Submitting...
              </>
            ) : (
              showConfirmation ? 'Yes, Complete Experiment' : 'Complete Experiment'
            )}
          </button>
        </div>
      </div>

      {/* 预测对比组件 - 已禁用 */}
      {/*
      {showComparison && currentPredictionData.length > 0 && (
        <div style={{ marginTop: '24px' }}>
          <PredictionComparison
            userPredictions={currentPredictionData}
            className="border-t pt-6"
          />
        </div>
      )}
      */}

      {/* CSS Animation */}
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default ExperimentCompletion;
