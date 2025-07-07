import { useState, useEffect, useCallback } from 'react';
import type { UserData, UserExperimentData } from '../types/index.js';

interface SessionConfig {
  timeoutMinutes?: number;
  autoSave?: boolean;
  saveInterval?: number; // in milliseconds
}

interface UseUserSessionReturn {
  isSessionActive: boolean;
  sessionTimeRemaining: number; // in minutes
  lastActivity: Date | null;
  
  // Session management
  startSession: (userData: UserData) => void;
  endSession: () => void;
  extendSession: () => void;
  updateActivity: () => void;
  
  // Data persistence
  saveSessionData: (data: UserExperimentData) => void;
  loadSessionData: () => UserExperimentData | null;
  clearSessionData: () => void;
  
  // Session status
  isSessionExpired: boolean;
  sessionWarning: boolean; // true when session is about to expire
}

const DEFAULT_CONFIG: Required<SessionConfig> = {
  timeoutMinutes: 120, // 2 hours
  autoSave: true,
  saveInterval: 30000 // 30 seconds
};

export const useUserSession = (config: SessionConfig = {}): UseUserSessionReturn => {
  const finalConfig = { ...DEFAULT_CONFIG, ...config };
  
  const [isSessionActive, setIsSessionActive] = useState(false);
  const [sessionStartTime, setSessionStartTime] = useState<Date | null>(null);
  const [lastActivity, setLastActivity] = useState<Date | null>(null);
  const [sessionData, setSessionData] = useState<UserExperimentData | null>(null);

  // Calculate session time remaining
  const sessionTimeRemaining = lastActivity 
    ? Math.max(0, finalConfig.timeoutMinutes - 
        Math.floor((Date.now() - lastActivity.getTime()) / (1000 * 60)))
    : 0;

  const isSessionExpired = sessionTimeRemaining <= 0 && isSessionActive;
  const sessionWarning = sessionTimeRemaining <= 10 && sessionTimeRemaining > 0; // Warning when 10 minutes left

  // Update activity timestamp
  const updateActivity = useCallback(() => {
    const now = new Date();
    setLastActivity(now);
    localStorage.setItem('lastActivity', now.toISOString());
  }, []);

  // Start a new session
  const startSession = useCallback((userData: UserData) => {
    const now = new Date();
    setIsSessionActive(true);
    setSessionStartTime(now);
    setLastActivity(now);
    
    // Save session info to localStorage
    localStorage.setItem('sessionActive', 'true');
    localStorage.setItem('sessionStartTime', now.toISOString());
    localStorage.setItem('lastActivity', now.toISOString());
    localStorage.setItem('currentUser', JSON.stringify(userData));
    
    console.log('Session started for user:', userData.username);
  }, []);

  // End the current session
  const endSession = useCallback(() => {
    setIsSessionActive(false);
    setSessionStartTime(null);
    setLastActivity(null);
    setSessionData(null);
    
    // Clear session data from localStorage
    localStorage.removeItem('sessionActive');
    localStorage.removeItem('sessionStartTime');
    localStorage.removeItem('lastActivity');
    localStorage.removeItem('currentUser');
    localStorage.removeItem('experimentData');
    
    console.log('Session ended');
  }, []);

  // Extend session (reset timeout)
  const extendSession = useCallback(() => {
    if (isSessionActive) {
      updateActivity();
      console.log('Session extended');
    }
  }, [isSessionActive, updateActivity]);

  // Save session data
  const saveSessionData = useCallback((data: UserExperimentData) => {
    setSessionData(data);
    if (finalConfig.autoSave) {
      localStorage.setItem('experimentData', JSON.stringify(data));
      localStorage.setItem('lastSave', new Date().toISOString());
    }
  }, [finalConfig.autoSave]);

  // Load session data
  const loadSessionData = useCallback((): UserExperimentData | null => {
    try {
      const saved = localStorage.getItem('experimentData');
      if (saved) {
        const data = JSON.parse(saved);
        setSessionData(data);
        return data;
      }
    } catch (error) {
      console.error('Failed to load session data:', error);
    }
    return null;
  }, []);

  // Clear session data
  const clearSessionData = useCallback(() => {
    setSessionData(null);
    localStorage.removeItem('experimentData');
    localStorage.removeItem('lastSave');
  }, []);

  // Restore session on mount
  useEffect(() => {
    const sessionActive = localStorage.getItem('sessionActive') === 'true';
    const lastActivityStr = localStorage.getItem('lastActivity');
    const sessionStartStr = localStorage.getItem('sessionStartTime');
    
    if (sessionActive && lastActivityStr && sessionStartStr) {
      const lastActivityTime = new Date(lastActivityStr);
      const sessionStartTime = new Date(sessionStartStr);
      const timeSinceActivity = Date.now() - lastActivityTime.getTime();
      const minutesSinceActivity = timeSinceActivity / (1000 * 60);
      
      // Check if session is still valid
      if (minutesSinceActivity < finalConfig.timeoutMinutes) {
        setIsSessionActive(true);
        setSessionStartTime(sessionStartTime);
        setLastActivity(lastActivityTime);
        
        // Load session data
        loadSessionData();
        
        console.log('Session restored, time since last activity:', Math.round(minutesSinceActivity), 'minutes');
      } else {
        // Session expired, clean up
        endSession();
        console.log('Session expired, cleaning up');
      }
    }
  }, [finalConfig.timeoutMinutes, loadSessionData, endSession]);

  // Auto-save interval
  useEffect(() => {
    if (!isSessionActive || !finalConfig.autoSave) return;

    const interval = setInterval(() => {
      if (sessionData) {
        localStorage.setItem('experimentData', JSON.stringify(sessionData));
        localStorage.setItem('lastSave', new Date().toISOString());
      }
    }, finalConfig.saveInterval);

    return () => clearInterval(interval);
  }, [isSessionActive, sessionData, finalConfig.autoSave, finalConfig.saveInterval]);

  // Session timeout check
  useEffect(() => {
    if (!isSessionActive) return;

    const checkTimeout = () => {
      if (isSessionExpired) {
        console.log('Session expired due to inactivity');
        endSession();
      }
    };

    const interval = setInterval(checkTimeout, 60000); // Check every minute
    return () => clearInterval(interval);
  }, [isSessionActive, isSessionExpired, endSession]);

  // Activity listeners
  useEffect(() => {
    if (!isSessionActive) return;

    const activityEvents = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
    
    const handleActivity = () => {
      updateActivity();
    };

    // Throttle activity updates to avoid too frequent updates
    let lastUpdate = 0;
    const throttledHandleActivity = () => {
      const now = Date.now();
      if (now - lastUpdate > 30000) { // Update at most every 30 seconds
        lastUpdate = now;
        handleActivity();
      }
    };

    activityEvents.forEach(event => {
      document.addEventListener(event, throttledHandleActivity, true);
    });

    return () => {
      activityEvents.forEach(event => {
        document.removeEventListener(event, throttledHandleActivity, true);
      });
    };
  }, [isSessionActive, updateActivity]);

  return {
    isSessionActive,
    sessionTimeRemaining,
    lastActivity,
    startSession,
    endSession,
    extendSession,
    updateActivity,
    saveSessionData,
    loadSessionData,
    clearSessionData,
    isSessionExpired,
    sessionWarning
  };
};

export default useUserSession;
