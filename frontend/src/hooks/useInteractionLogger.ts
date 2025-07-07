import { useCallback } from 'react';
import ApiService from '../services/api';

interface UserSession {
  user_id: string;
  username: string;
  session_id: string;
  created_at: string;
  last_active: string;
}

export const useInteractionLogger = (userSession: UserSession | null) => {
  const logInteraction = useCallback(async (
    component: string,
    actionType: string,
    actionDetails: any = {}
  ) => {
    if (!userSession) {
      console.warn('No user session available for interaction logging');
      return;
    }

    try {
      await ApiService.recordUserInteraction(
        userSession.session_id,
        component,
        actionType,
        actionDetails
      );
      console.log(`Interaction logged: ${component} - ${actionType}`, actionDetails);
    } catch (error) {
      console.error('Failed to log interaction:', error);
    }
  }, [userSession]);

  // 预定义的组件交互记录函数
  const logDataAnalysisInteraction = useCallback((actionType: string, details: any) => {
    logInteraction('DataAnalysis', actionType, details);
  }, [logInteraction]);

  const logModelInterpretabilityInteraction = useCallback((actionType: string, details: any) => {
    logInteraction('ModelInterpretability', actionType, details);
  }, [logInteraction]);

  const logContextInformationInteraction = useCallback((actionType: string, details: any) => {
    logInteraction('ContextInformation', actionType, details);
  }, [logInteraction]);

  const logUserPredictionInteraction = useCallback((actionType: string, details: any) => {
    logInteraction('UserPrediction', actionType, details);
  }, [logInteraction]);

  const logDecisionMakingInteraction = useCallback((actionType: string, details: any) => {
    logInteraction('DecisionMaking', actionType, details);
  }, [logInteraction]);

  return {
    logInteraction,
    logDataAnalysisInteraction,
    logModelInterpretabilityInteraction,
    logContextInformationInteraction,
    logUserPredictionInteraction,
    logDecisionMakingInteraction
  };
};
