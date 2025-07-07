import React, { useState } from 'react';
import { User, ArrowRight, AlertCircle } from 'lucide-react';

interface UserLoginProps {
  onUserLogin: (userData: UserData) => void;
}

export interface UserData {
  userId: string;
  username: string;
  sessionId: string;
  loginTime: string;
}

const UserLogin: React.FC<UserLoginProps> = ({ onUserLogin }) => {
  const [username, setUsername] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const validateUsername = (name: string): string | null => {
    if (!name.trim()) {
      return 'Please enter your username';
    }
    if (name.trim().length < 3) {
      return 'Username must be at least 3 characters';
    }
    if (name.trim().length > 20) {
      return 'Username must be no more than 20 characters';
    }
    if (!/^[a-zA-Z0-9_-]+$/.test(name.trim())) {
      return 'Username can only contain letters, numbers, underscore and dash';
    }
    return null;
  };

  const generateSessionId = (): string => {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  };

  const handleLogin = () => {
    const trimmedUsername = username.trim();
    const validationError = validateUsername(trimmedUsername);

    if (validationError) {
      setError(validationError);
      return;
    }

    setIsLoading(true);
    setError(null);

    // Create temporary user data for the callback
    // The actual login will be handled by the parent component
    const userData: UserData = {
      userId: `temp_${Date.now()}`,
      username: trimmedUsername,
      sessionId: generateSessionId(),
      loginTime: new Date().toISOString()
    };

    onUserLogin(userData);
    setIsLoading(false);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleLogin();
    }
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      backgroundColor: '#f8fafc',
      padding: '20px'
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '12px',
        padding: '40px',
        boxShadow: '0 10px 25px rgba(0, 0, 0, 0.1)',
        width: '100%',
        maxWidth: '400px',
        textAlign: 'center'
      }}>
        {/* Header */}
        <div style={{ marginBottom: '30px' }}>
          <div style={{
            width: '60px',
            height: '60px',
            backgroundColor: '#3b82f6',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 16px'
          }}>
            <User size={30} color="white" />
          </div>
          <h2 style={{
            margin: 0,
            fontSize: '24px',
            fontWeight: '600',
            color: '#1f2937',
            marginBottom: '8px'
          }}>
            Welcome to Power Prediction Experiment
          </h2>
          <p style={{
            margin: 0,
            fontSize: '14px',
            color: '#6b7280',
            lineHeight: '1.5'
          }}>
            Please enter your username to begin the experiment
          </p>
        </div>

        {/* Input Section */}
        <div style={{ marginBottom: '24px' }}>
          <label style={{
            display: 'block',
            fontSize: '14px',
            fontWeight: '500',
            color: '#374151',
            marginBottom: '8px',
            textAlign: 'left'
          }}>
            Username
          </label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Enter your username"
            disabled={isLoading}
            style={{
              width: '100%',
              padding: '12px 16px',
              fontSize: '16px',
              border: error ? '2px solid #ef4444' : '2px solid #e5e7eb',
              borderRadius: '8px',
              outline: 'none',
              transition: 'border-color 0.2s',
              backgroundColor: isLoading ? '#f9fafb' : 'white',
              boxSizing: 'border-box'
            }}
            onFocus={(e) => {
              if (!error) {
                e.target.style.borderColor = '#3b82f6';
              }
            }}
            onBlur={(e) => {
              if (!error) {
                e.target.style.borderColor = '#e5e7eb';
              }
            }}
          />
          
          {error && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              marginTop: '8px',
              color: '#ef4444',
              fontSize: '12px'
            }}>
              <AlertCircle size={14} />
              <span>{error}</span>
            </div>
          )}
        </div>

        {/* Login Button */}
        <button
          onClick={handleLogin}
          disabled={isLoading || !username.trim()}
          style={{
            width: '100%',
            padding: '12px 24px',
            fontSize: '16px',
            fontWeight: '600',
            color: 'white',
            backgroundColor: isLoading || !username.trim() ? '#9ca3af' : '#3b82f6',
            border: 'none',
            borderRadius: '8px',
            cursor: isLoading || !username.trim() ? 'not-allowed' : 'pointer',
            transition: 'all 0.2s',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px'
          }}
          onMouseEnter={(e) => {
            if (!isLoading && username.trim()) {
              e.currentTarget.style.backgroundColor = '#2563eb';
            }
          }}
          onMouseLeave={(e) => {
            if (!isLoading && username.trim()) {
              e.currentTarget.style.backgroundColor = '#3b82f6';
            }
          }}
        >
          {isLoading ? (
            <>
              <div style={{
                width: '16px',
                height: '16px',
                border: '2px solid transparent',
                borderTop: '2px solid white',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite'
              }} />
              <span>Logging in...</span>
            </>
          ) : (
            <>
              <span>Start Experiment</span>
              <ArrowRight size={16} />
            </>
          )}
        </button>

        {/* Instructions */}
        <div style={{
          marginTop: '24px',
          padding: '16px',
          backgroundColor: '#f0f9ff',
          borderRadius: '8px',
          border: '1px solid #bae6fd'
        }}>
          <p style={{
            margin: 0,
            fontSize: '12px',
            color: '#0369a1',
            lineHeight: '1.4'
          }}>
            <strong>Instructions:</strong><br />
            • Use a unique username for identification<br />
            • Your experiment data will be saved automatically<br />
            • You can complete the experiment at any time
          </p>
        </div>
      </div>

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

export default UserLogin;
