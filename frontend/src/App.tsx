import React, { useState, useEffect } from 'react';
import { Zap, AlertCircle, CheckCircle } from 'lucide-react';
import ExperimentCover from './components/ExperimentCover';
import UserLogin from './components/UserLogin';
import ContextInformation from './components/ContextInformation';
import DataAnalysis from './components/DataAnalysis';
import ModelInterpretability from './components/ModelInterpretability';
import UserPrediction from './components/UserPrediction';
import DecisionMaking from './components/DecisionMaking';
import type { PredictionResult } from './types/index.js';
import ApiService from './services/api';
import { useInteractionLogger } from './hooks/useInteractionLogger';
import './styles/ExperimentCover.css';

interface ScreenDimensions {
  width: number;
  height: number;
  availableHeight: number;
}

interface UserSession {
  user_id: string;
  username: string;
  session_id: string;
  created_at: string;
  last_active: string;
}

function App() {
  const [predictions, setPredictions] = useState<PredictionResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [systemStatus, setSystemStatus] = useState<'loading' | 'ready' | 'error'>('loading');
  const [hasActiveDecision, setHasActiveDecision] = useState(false);
  const [decisionMakingRef, setDecisionMakingRef] = useState<any>(null);
  const [showExperiment, setShowExperiment] = useState(false);
  const [showUserLogin, setShowUserLogin] = useState(false);
  const [userSession, setUserSession] = useState<UserSession | null>(null);
  const [experimentStartTime, setExperimentStartTime] = useState<Date | null>(null);
  const [screenDimensions, setScreenDimensions] = useState<ScreenDimensions>({
    width: window.innerWidth,
    height: window.innerHeight,
    availableHeight: window.innerHeight - 32 // 增加padding空间
  });

  // 交互记录Hook
  const interactionLogger = useInteractionLogger(userSession);

  // 屏幕尺寸检测和响应
  useEffect(() => {
    const updateScreenDimensions = () => {
      const newDimensions = {
        width: window.innerWidth,
        height: window.innerHeight,
        availableHeight: window.innerHeight - 32 // 考虑上下padding
      };
      setScreenDimensions(newDimensions);
      console.log('Screen dimensions updated:', newDimensions);
    };

    window.addEventListener('resize', updateScreenDimensions);
    updateScreenDimensions();

    return () => {
      window.removeEventListener('resize', updateScreenDimensions);
    };
  }, []);

  useEffect(() => {
    initializeSystem();
  }, []);

  const initializeSystem = async () => {
    try {
      setLoading(true);
      setSystemStatus('loading');

      await ApiService.healthCheck();
      console.log('Health check passed');

      setSystemStatus('ready');

      const mockPredictions = Array.from({ length: 24 }, (_, hour) => ({
        hour,
        predicted_usage: 3000 + Math.sin(hour * Math.PI / 12) * 500 + Math.random() * 200,
        confidence_interval: [2800, 3400] as [number, number],
        original_prediction: 3000 + Math.sin(hour * Math.PI / 12) * 500
      }));
      setPredictions(mockPredictions);

    } catch (err) {
      console.error('System initialization failed:', err);
      setError('System initialization failed, please check if backend service is running normally');
      setSystemStatus('error');
    } finally {
      setLoading(false);
    }
  };

  const handlePredictionUpdate = (newPredictions: PredictionResult[]) => {
    setPredictions(newPredictions);
  };

  const handleAdjustmentApplied = (adjustedPredictions: PredictionResult[]) => {
    setPredictions(adjustedPredictions);
  };

  const handleAdjustmentMade = (hour: number, originalValue: number, adjustedValue: number) => {
    if (decisionMakingRef && decisionMakingRef.addAdjustment) {
      decisionMakingRef.addAdjustment(hour, originalValue, adjustedValue);
    }
  };

  const handleStartExperiment = () => {
    setShowUserLogin(true);
  };

  const handleLoginSuccess = (session: UserSession) => {
    setUserSession(session);
    setExperimentStartTime(new Date());
    setShowUserLogin(false);
    setShowExperiment(true);
  };

  const handleCompleteExperiment = async () => {
    if (!userSession) return;

    try {
      // 收集最终预测结果
      const finalPredictions = predictions.map(pred => ({
        hour: pred.hour,
        predicted_usage: pred.predicted_usage,
        confidence_interval: pred.confidence_interval,
        original_prediction: pred.original_prediction
      }));

      // 发送到后端保存
      await ApiService.completeExperiment(userSession.session_id, finalPredictions);

      alert('实验已完成！您的结果已保存。感谢您的参与！');

      // 重置应用状态
      setUserSession(null);
      setExperimentStartTime(null);
      setShowExperiment(false);
      setShowUserLogin(false);
      setPredictions([]);
      setHasActiveDecision(false);

    } catch (error) {
      console.error('完成实验失败:', error);
      alert('保存实验结果时出现错误，请重试。');
    }
  };

  // 修复布局样式计算
  const getLayoutStyle = () => {
    const { availableHeight } = screenDimensions;
    
    // 更合理的高度分配：上排60%，下排38%，间距2%
    const topRowHeight = Math.floor(availableHeight * 0.58);
    const bottomRowHeight = Math.floor(availableHeight * 0.40);
    const gap = 8; // 固定间距

    return {
      height: `${availableHeight}px`,
      display: 'grid',
      gridTemplateRows: `${topRowHeight}px ${bottomRowHeight}px`,
      gridTemplateColumns: '1fr 1fr 1fr', // 三列等宽
      gap: `${gap}px`,
      padding: '16px',
      backgroundColor: '#f3f4f6'
    };
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">System Initializing</h2>
          <p className="text-gray-600">Loading data and training models...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-800 mb-2">System Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={initializeSystem}
            className="btn btn-primary"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!showExperiment && !showUserLogin) {
    return <ExperimentCover onStartExperiment={handleStartExperiment} />;
  }

  if (showUserLogin) {
    return <UserLogin onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <>
      {/* 用户信息和完成实验按钮 */}
      <div style={{
        position: 'fixed',
        top: '16px',
        left: '16px',
        right: '16px',
        zIndex: 1000,
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        background: 'rgba(255, 255, 255, 0.95)',
        padding: '12px 20px',
        borderRadius: '8px',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
        backdropFilter: 'blur(10px)'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px'
        }}>
          <div style={{
            width: '32px',
            height: '32px',
            borderRadius: '50%',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontSize: '14px',
            fontWeight: 'bold'
          }}>
            {userSession?.username.charAt(0).toUpperCase()}
          </div>
          <div>
            <div style={{ fontSize: '14px', fontWeight: '600', color: '#374151' }}>
              {userSession?.username}
            </div>
            <div style={{ fontSize: '12px', color: '#6b7280' }}>
              Session: {userSession?.session_id.slice(0, 8)}...
            </div>
          </div>
        </div>

        <button
          onClick={handleCompleteExperiment}
          style={{
            padding: '10px 20px',
            background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            fontSize: '14px',
            fontWeight: '600',
            cursor: 'pointer',
            transition: 'all 0.2s',
            boxShadow: '0 2px 4px rgba(16, 185, 129, 0.2)'
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.transform = 'translateY(-1px)';
            e.currentTarget.style.boxShadow = '0 4px 8px rgba(16, 185, 129, 0.3)';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.boxShadow = '0 2px 4px rgba(16, 185, 129, 0.2)';
          }}
        >
          Complete Experiment
        </button>
      </div>

      {/* 主要内容区域 - 保持原有网格布局，增加顶部边距 */}
      <div style={{
        ...getLayoutStyle(),
        paddingTop: '96px' // 为顶部栏留出空间
      }}>
        {/* 第一行：三个模块 */}
        <div style={{ gridColumn: '1', gridRow: '1', overflow: 'hidden' }}>
          <ContextInformation
            onInteraction={interactionLogger.logContextInformationInteraction}
          />
        </div>

        <div style={{ gridColumn: '2', gridRow: '1', overflow: 'hidden' }}>
          <DataAnalysis
            onInteraction={interactionLogger.logDataAnalysisInteraction}
          />
        </div>

        <div style={{ gridColumn: '3', gridRow: '1', overflow: 'hidden' }}>
          <ModelInterpretability
            onInteraction={interactionLogger.logModelInterpretabilityInteraction}
          />
        </div>

        {/* 第二行：两个模块 */}
        <div style={{ gridColumn: '1 / 3', gridRow: '2', overflow: 'hidden' }}>
          <UserPrediction
            onPredictionUpdate={handlePredictionUpdate}
            hasActiveDecision={hasActiveDecision}
            onAdjustmentMade={handleAdjustmentMade}
            onInteraction={interactionLogger.logUserPredictionInteraction}
          />
        </div>

        <div style={{ gridColumn: '3', gridRow: '2', overflow: 'hidden' }}>
          <DecisionMaking
            ref={setDecisionMakingRef}
            predictions={predictions}
            onAdjustmentApplied={handleAdjustmentApplied}
            onDecisionStatusChange={setHasActiveDecision}
            userSession={userSession}
            onInteraction={interactionLogger.logDecisionMakingInteraction}
          />
        </div>

        {/* 屏幕信息显示 */}
        <div className="fixed bottom-2 right-2 bg-black bg-opacity-50 text-white text-xs p-2 rounded z-50">
          {screenDimensions.width} × {screenDimensions.height} (Available: {screenDimensions.availableHeight})
        </div>
      </div>
    </>
  );
}

export default App;