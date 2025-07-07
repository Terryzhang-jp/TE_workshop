import React, { useState } from 'react';
import { User, ArrowRight, AlertCircle } from 'lucide-react';
import ApiService from '../services/api';

interface UserLoginProps {
  onLoginSuccess: (userSession: any) => void;
}

const UserLogin: React.FC<UserLoginProps> = ({ onLoginSuccess }) => {
  const [username, setUsername] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!username.trim()) {
      setError('请输入用户名');
      return;
    }

    if (username.trim().length < 2) {
      setError('用户名至少需要2个字符');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // 调用后端API创建用户会话
      const userSession = await ApiService.userLogin(username.trim());
      onLoginSuccess(userSession);
    } catch (err) {
      setError('登录失败，请重试');
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px'
    }}>
      <div style={{
        background: 'white',
        borderRadius: '16px',
        padding: '48px',
        boxShadow: '0 20px 40px rgba(0, 0, 0, 0.1)',
        maxWidth: '480px',
        width: '100%'
      }}>
        {/* 标题区域 */}
        <div style={{
          textAlign: 'center',
          marginBottom: '32px'
        }}>
          <div style={{
            width: '80px',
            height: '80px',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 24px'
          }}>
            <User size={40} color="white" />
          </div>
          
          <h1 style={{
            fontSize: '28px',
            fontWeight: '700',
            color: '#1a202c',
            marginBottom: '8px'
          }}>
            Welcome to Power Prediction Experiment
          </h1>
          
          <p style={{
            fontSize: '16px',
            color: '#718096',
            lineHeight: '1.5'
          }}>
            Please enter your username to begin the experiment session
          </p>
        </div>

        {/* 登录表单 */}
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '24px' }}>
            <label style={{
              display: 'block',
              fontSize: '14px',
              fontWeight: '600',
              color: '#374151',
              marginBottom: '8px'
            }}>
              Username
            </label>
            
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your username"
              disabled={loading}
              style={{
                width: '100%',
                padding: '12px 16px',
                border: '2px solid #e2e8f0',
                borderRadius: '8px',
                fontSize: '16px',
                transition: 'border-color 0.2s',
                outline: 'none',
                backgroundColor: loading ? '#f7fafc' : 'white'
              }}
              onFocus={(e) => {
                e.target.style.borderColor = '#667eea';
              }}
              onBlur={(e) => {
                e.target.style.borderColor = '#e2e8f0';
              }}
            />
          </div>

          {/* 错误信息 */}
          {error && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '12px 16px',
              background: '#fed7d7',
              border: '1px solid #fc8181',
              borderRadius: '8px',
              marginBottom: '24px'
            }}>
              <AlertCircle size={16} color="#e53e3e" />
              <span style={{
                fontSize: '14px',
                color: '#e53e3e'
              }}>
                {error}
              </span>
            </div>
          )}

          {/* 提交按钮 */}
          <button
            type="submit"
            disabled={loading || !username.trim()}
            style={{
              width: '100%',
              padding: '14px 24px',
              background: loading || !username.trim() 
                ? '#a0aec0' 
                : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '16px',
              fontWeight: '600',
              cursor: loading || !username.trim() ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              transition: 'all 0.2s'
            }}
          >
            {loading ? (
              <>
                <div style={{
                  width: '16px',
                  height: '16px',
                  border: '2px solid transparent',
                  borderTop: '2px solid white',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite'
                }} />
                Creating Session...
              </>
            ) : (
              <>
                Start Experiment
                <ArrowRight size={16} />
              </>
            )}
          </button>
        </form>

        {/* 说明文字 */}
        <div style={{
          marginTop: '32px',
          padding: '16px',
          background: '#f7fafc',
          borderRadius: '8px',
          border: '1px solid #e2e8f0'
        }}>
          <h3 style={{
            fontSize: '14px',
            fontWeight: '600',
            color: '#374151',
            marginBottom: '8px'
          }}>
            Important Notes:
          </h3>
          <ul style={{
            fontSize: '13px',
            color: '#718096',
            lineHeight: '1.5',
            paddingLeft: '16px',
            margin: 0
          }}>
            <li>Your username will be used to identify your experiment session</li>
            <li>All your decisions and adjustments will be recorded</li>
            <li>You can complete the experiment at any time using the "Complete Experiment" button</li>
            <li>Your results will be saved for analysis</li>
          </ul>
        </div>
      </div>

      {/* CSS动画 */}
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
