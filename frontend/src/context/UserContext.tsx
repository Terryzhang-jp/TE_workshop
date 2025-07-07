import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import type { UserData, UserExperimentData, UserAdjustment, UserInteraction, Decision } from '../types/index.js';
import ApiService from '../services/api';

interface UserContextType {
  // 用户状态
  currentUser: UserData | null;
  experimentData: UserExperimentData | null;
  
  // 用户操作
  loginUser: (userData: UserData) => void;
  logoutUser: () => void;
  
  // 实验数据操作
  addDecision: (decision: Decision) => void;
  updateDecision: (decisionId: string, updates: Partial<Decision>) => void;
  addAdjustment: (adjustment: UserAdjustment) => void;
  addInteraction: (interaction: UserInteraction) => void;
  
  // 实验控制
  startExperiment: () => void;
  completeExperiment: () => Promise<void>;
  
  // 数据获取
  getExperimentSummary: () => ExperimentSummary;
}

interface ExperimentSummary {
  totalDecisions: number;
  totalAdjustments: number;
  totalInteractions: number;
  experimentDuration: number; // in minutes
  status: 'in_progress' | 'completed';
}

interface UserProviderProps {
  children: ReactNode;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export const UserProvider: React.FC<UserProviderProps> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<UserData | null>(null);
  const [experimentData, setExperimentData] = useState<UserExperimentData | null>(null);

  // 从localStorage恢复用户会话
  useEffect(() => {
    const savedUser = localStorage.getItem('currentUser');
    const savedExperiment = localStorage.getItem('experimentData');
    
    if (savedUser) {
      try {
        const userData = JSON.parse(savedUser);
        setCurrentUser(userData);
      } catch (error) {
        console.error('Failed to restore user session:', error);
        localStorage.removeItem('currentUser');
      }
    }
    
    if (savedExperiment) {
      try {
        const expData = JSON.parse(savedExperiment);
        setExperimentData(expData);
      } catch (error) {
        console.error('Failed to restore experiment data:', error);
        localStorage.removeItem('experimentData');
      }
    }
  }, []);

  // 保存用户会话到localStorage
  useEffect(() => {
    if (currentUser) {
      localStorage.setItem('currentUser', JSON.stringify(currentUser));
    } else {
      localStorage.removeItem('currentUser');
    }
  }, [currentUser]);

  // 保存实验数据到localStorage
  useEffect(() => {
    if (experimentData) {
      localStorage.setItem('experimentData', JSON.stringify(experimentData));
    } else {
      localStorage.removeItem('experimentData');
    }
  }, [experimentData]);

  const loginUser = (userData: UserData) => {
    setCurrentUser(userData);
    
    // 初始化实验数据
    const newExperimentData: UserExperimentData = {
      userId: userData.userId,
      username: userData.username,
      sessionId: userData.sessionId,
      startTime: new Date().toISOString(),
      decisions: [],
      adjustments: [],
      interactions: [],
      status: 'in_progress'
    };
    setExperimentData(newExperimentData);
    
    // 记录登录交互
    addInteraction({
      id: `interaction_${Date.now()}`,
      type: 'page_view',
      component: 'UserLogin',
      action: 'user_login',
      timestamp: new Date().toISOString(),
      metadata: { username: userData.username }
    });
  };

  const logoutUser = () => {
    setCurrentUser(null);
    setExperimentData(null);
    localStorage.removeItem('currentUser');
    localStorage.removeItem('experimentData');
  };

  const addDecision = (decision: Decision) => {
    if (!experimentData) return;
    
    setExperimentData(prev => prev ? {
      ...prev,
      decisions: [...prev.decisions, decision]
    } : null);
  };

  const updateDecision = (decisionId: string, updates: Partial<Decision>) => {
    if (!experimentData) return;
    
    setExperimentData(prev => prev ? {
      ...prev,
      decisions: prev.decisions.map(d => 
        d.id === decisionId ? { ...d, ...updates } : d
      )
    } : null);
  };

  const addAdjustment = (adjustment: UserAdjustment) => {
    if (!experimentData) return;
    
    setExperimentData(prev => prev ? {
      ...prev,
      adjustments: [...prev.adjustments, adjustment]
    } : null);
  };

  const addInteraction = (interaction: UserInteraction) => {
    if (!experimentData) return;
    
    setExperimentData(prev => prev ? {
      ...prev,
      interactions: [...prev.interactions, interaction]
    } : null);
  };

  const startExperiment = () => {
    if (!experimentData) return;
    
    addInteraction({
      id: `interaction_${Date.now()}`,
      type: 'page_view',
      component: 'ExperimentMain',
      action: 'experiment_started',
      timestamp: new Date().toISOString()
    });
  };

  const completeExperiment = async (): Promise<void> => {
    if (!experimentData || !currentUser) return;
    
    const completionTime = new Date().toISOString();
    
    // 更新实验状态
    const finalExperimentData = {
      ...experimentData,
      completionTime,
      status: 'completed' as const
    };
    
    setExperimentData(finalExperimentData);
    
    // 记录完成交互
    addInteraction({
      id: `interaction_${Date.now()}`,
      type: 'page_view',
      component: 'ExperimentCompletion',
      action: 'experiment_completed',
      timestamp: completionTime
    });
    
    try {
      // 发送数据到后端
      console.log('Experiment completed, data to be sent:', finalExperimentData);

      // 调用API发送数据到后端
      const result = await ApiService.completeExperiment(finalExperimentData);
      console.log('Experiment submitted successfully:', result);

    } catch (error) {
      console.error('Failed to submit experiment data:', error);
      throw error;
    }
  };

  const getExperimentSummary = (): ExperimentSummary => {
    if (!experimentData) {
      return {
        totalDecisions: 0,
        totalAdjustments: 0,
        totalInteractions: 0,
        experimentDuration: 0,
        status: 'in_progress'
      };
    }
    
    const startTime = new Date(experimentData.startTime);
    const endTime = experimentData.completionTime 
      ? new Date(experimentData.completionTime) 
      : new Date();
    
    const durationMs = endTime.getTime() - startTime.getTime();
    const durationMinutes = Math.round(durationMs / (1000 * 60));
    
    return {
      totalDecisions: experimentData.decisions.length,
      totalAdjustments: experimentData.adjustments.length,
      totalInteractions: experimentData.interactions.length,
      experimentDuration: durationMinutes,
      status: experimentData.status
    };
  };

  const value: UserContextType = {
    currentUser,
    experimentData,
    loginUser,
    logoutUser,
    addDecision,
    updateDecision,
    addAdjustment,
    addInteraction,
    startExperiment,
    completeExperiment,
    getExperimentSummary
  };

  return (
    <UserContext.Provider value={value}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = (): UserContextType => {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};

export default UserContext;
