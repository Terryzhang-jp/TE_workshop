import React, { useState, useEffect } from 'react';
import { Zap, AlertCircle, CheckCircle } from 'lucide-react';
import ExperimentCover from './components/ExperimentCover';
import ContextInformation from './components/ContextInformation';
import DataAnalysis from './components/DataAnalysis';
import ModelInterpretability from './components/ModelInterpretability';
import UserPrediction from './components/UserPrediction';
import DecisionMaking from './components/DecisionMaking';
import type { PredictionResult } from './types/index.js';
import ApiService from './services/api';
import './styles/ExperimentCover.css';

interface ScreenDimensions {
  width: number;
  height: number;
  availableHeight: number;
}

function App() {
  const [predictions, setPredictions] = useState<PredictionResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [systemStatus, setSystemStatus] = useState<'loading' | 'ready' | 'error'>('loading');
  const [hasActiveDecision, setHasActiveDecision] = useState(false);
  const [decisionMakingRef, setDecisionMakingRef] = useState<any>(null);
  const [showExperiment, setShowExperiment] = useState(false);
  const [screenDimensions, setScreenDimensions] = useState<ScreenDimensions>({
    width: window.innerWidth,
    height: window.innerHeight,
    availableHeight: window.innerHeight - 32 // 增加padding空间
  });

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
    setShowExperiment(true);
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

  if (!showExperiment) {
    return <ExperimentCover onStartExperiment={handleStartExperiment} />;
  }

  return (
    <div style={getLayoutStyle()}>
      {/* 第一行：三个模块 */}
      <div style={{ gridColumn: '1', gridRow: '1', overflow: 'hidden' }}>
        <ContextInformation />
      </div>
      
      <div style={{ gridColumn: '2', gridRow: '1', overflow: 'hidden' }}>
        <DataAnalysis />
      </div>
      
      <div style={{ gridColumn: '3', gridRow: '1', overflow: 'hidden' }}>
        <ModelInterpretability />
      </div>

      {/* 第二行：两个模块 */}
      <div style={{ gridColumn: '1 / 3', gridRow: '2', overflow: 'hidden' }}>
        <UserPrediction
          onPredictionUpdate={handlePredictionUpdate}
          hasActiveDecision={hasActiveDecision}
          onAdjustmentMade={handleAdjustmentMade}
        />
      </div>
      
      <div style={{ gridColumn: '3', gridRow: '2', overflow: 'hidden' }}>
        <DecisionMaking
          ref={setDecisionMakingRef}
          predictions={predictions}
          onAdjustmentApplied={handleAdjustmentApplied}
          onDecisionStatusChange={setHasActiveDecision}
        />
      </div>

      {/* 屏幕信息显示 */}
      <div className="fixed bottom-2 right-2 bg-black bg-opacity-50 text-white text-xs p-2 rounded z-50">
        {screenDimensions.width} × {screenDimensions.height} (Available: {screenDimensions.availableHeight})
      </div>
    </div>
  );
}

export default App;