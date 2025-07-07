import React, { useState, useEffect } from 'react';
import { Zap, AlertCircle, CheckCircle } from 'lucide-react';
import ComparisonPreview from './components/ComparisonPreview';
import ExperimentResultsPage from './components/ExperimentResultsPage';
import ExperimentCover from './components/ExperimentCover';
import UserLogin from './components/UserLogin';
import ExperimentCompletion from './components/ExperimentCompletion';
import ContextInformation from './components/ContextInformation';
import DataAnalysis from './components/DataAnalysis';
import ModelInterpretability from './components/ModelInterpretability';
import UserPrediction from './components/UserPrediction';
import DecisionMaking from './components/DecisionMaking';
import { UserProvider, useUser } from './context/UserContext';
import type { PredictionResult, UserData, UserExperimentData } from './types/index.js';
import ApiService from './services/api';
import './styles/ExperimentCover.css';

interface ScreenDimensions {
  width: number;
  height: number;
  availableHeight: number;
}

// 内部应用组件，使用UserContext
function AppContent() {
  // 检查是否是预览模式
  const isPreviewMode = window.location.search.includes('preview=comparison');

  const [predictions, setPredictions] = useState<PredictionResult[]>([]);
  const [currentPredictionData, setCurrentPredictionData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [systemStatus, setSystemStatus] = useState<'loading' | 'ready' | 'error'>('loading');
  const [hasActiveDecision, setHasActiveDecision] = useState(false);
  const [decisionMakingRef, setDecisionMakingRef] = useState<any>(null);
  const [showExperiment, setShowExperiment] = useState(false);

  // 用户状态管理 - 使用UserContext
  const [showUserLogin, setShowUserLogin] = useState(false);
  const [showExperimentCompletion, setShowExperimentCompletion] = useState(false);
  const [showResultsPage, setShowResultsPage] = useState(false);

  // 使用UserContext
  const {
    currentUser,
    experimentData,
    loginUser,
    completeExperiment: completeUserExperiment,
    addInteraction
  } = useUser();
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

  const handlePredictionDataChange = (data: any[]) => {
    setCurrentPredictionData(data);
  };

  const handleStartExperiment = () => {
    setShowExperiment(true);
  };

  // 处理用户登录
  const handleUserLogin = async (userData: UserData) => {
    try {
      // 调用后端登录API
      const loginResponse = await ApiService.loginUser(userData.username);

      // 使用后端返回的用户数据
      const backendUserData = loginResponse.user_data;

      // 使用UserContext登录用户
      loginUser(backendUserData);

      setShowUserLogin(false);
      setShowExperiment(true);

      console.log('User logged in:', backendUserData);
    } catch (error) {
      console.error('Login failed:', error);
      setError('登录失败，请重试');
    }
  };

  // 处理用户准备状态
  const handleUserReady = (showLogin: boolean) => {
    setShowUserLogin(showLogin);
  };

  // 处理完成实验
  const handleCompleteExperiment = () => {
    console.log('handleCompleteExperiment called');
    console.log('experimentData:', experimentData);
    console.log('currentPredictionData:', currentPredictionData);
    console.log('currentUser:', currentUser);

    if (!currentUser) {
      alert('Please login first to complete the experiment!');
      setShowUserLogin(true);
      return;
    }

    if (experimentData) {
      console.log('Setting showExperimentCompletion to true');
      setShowExperimentCompletion(true);
    } else {
      console.log('No experimentData available - this should not happen after login');
      alert('Experiment data not found. Please try logging in again.');
      setShowUserLogin(true);
    }
  };

  // 处理实验完成提交
  const handleExperimentSubmission = async (): Promise<void> => {
    if (!experimentData) {
      throw new Error('No experiment data to submit');
    }

    try {
      // 使用UserContext的完成实验方法
      await completeUserExperiment();
      console.log('Experiment submitted successfully');

      // 实验完成后跳转到结果页面
      setShowExperimentCompletion(false);
      setShowResultsPage(true);

    } catch (error) {
      console.error('Failed to submit experiment:', error);
      throw error;
    }
  };

  // 取消实验完成
  const handleCancelCompletion = () => {
    setShowExperimentCompletion(false);
  };

  // 从结果页面返回
  const handleBackFromResults = () => {
    setShowResultsPage(false);
    setShowExperiment(false);
    setShowUserLogin(false);
  };

  // 预览模式
  if (isPreviewMode) {
    return <ComparisonPreview />;
  }

  // 显示结果页面
  if (showResultsPage && experimentData) {
    return (
      <ExperimentResultsPage
        userPredictions={currentPredictionData}
        userAdjustments={experimentData.adjustments || []}
        experimentData={experimentData}
        onBack={handleBackFromResults}
      />
    );
  }

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

  // 显示实验完成界面
  console.log('Checking ExperimentCompletion display:', {
    showExperimentCompletion,
    hasExperimentData: !!experimentData,
    currentPredictionDataLength: currentPredictionData.length
  });

  if (showExperimentCompletion && experimentData) {
    console.log('Rendering ExperimentCompletion component');
    return (
      <ExperimentCompletion
        experimentData={experimentData}
        currentPredictionData={currentPredictionData}
        onComplete={handleExperimentSubmission}
        onCancel={handleCancelCompletion}
      />
    );
  }

  // 显示用户登录界面
  if (showUserLogin) {
    return <UserLogin onUserLogin={handleUserLogin} />;
  }

  // 显示实验封面
  if (!showExperiment) {
    return <ExperimentCover onStartExperiment={handleStartExperiment} onUserReady={handleUserReady} />;
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
            onPredictionDataChange={handlePredictionDataChange}
          />
        </div>

        <div style={{ gridColumn: '3', gridRow: '2', overflow: 'hidden' }}>
          <DecisionMaking
            ref={setDecisionMakingRef}
            predictions={predictions}
            currentPredictionData={currentPredictionData}
            onAdjustmentApplied={handleAdjustmentApplied}
            onDecisionStatusChange={setHasActiveDecision}
            onCompleteExperiment={handleCompleteExperiment}
          />
        </div>

        {/* 屏幕信息显示 */}
        <div className="fixed bottom-2 right-2 bg-black bg-opacity-50 text-white text-xs p-2 rounded z-50">
          {screenDimensions.width} × {screenDimensions.height} (Available: {screenDimensions.availableHeight})
        </div>
    </div>
  );
}

// 主App组件，提供UserContext
function App() {
  return (
    <UserProvider>
      <AppContent />
    </UserProvider>
  );
}

export default App;