import { useState, useEffect, forwardRef, useImperativeHandle } from 'react';
import { useUser } from '../context/UserContext';
import type { PredictionResult, Decision, UserAdjustment } from '../types/index.js';

interface DecisionMakingProps {
  className?: string;
  predictions?: PredictionResult[];
  onAdjustmentApplied?: (adjustedPredictions: PredictionResult[]) => void;
  onDecisionStatusChange?: (hasActiveDecision: boolean) => void;
  onCompleteExperiment?: () => void;
  currentPredictionData?: any[]; // 添加当前预测数据
}

const DecisionMaking = forwardRef<any, DecisionMakingProps>(({
  onDecisionStatusChange,
  onCompleteExperiment,
  currentPredictionData = []
}, ref) => {
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [activeDecision, setActiveDecision] = useState<Decision | null>(null);
  const [showNewDecisionForm, setShowNewDecisionForm] = useState(false);
  const [newDecisionLabel, setNewDecisionLabel] = useState('');
  const [newDecisionReason, setNewDecisionReason] = useState('');
  const loading = false;
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // 使用UserContext
  const { addDecision, addDecisionWithPredictionData, updateDecision, addAdjustment, addInteraction } = useUser();



  // Notify parent component of decision status changes
  useEffect(() => {
    onDecisionStatusChange?.(activeDecision !== null);
  }, [activeDecision, onDecisionStatusChange]);

  // Methods exposed to parent component
  useImperativeHandle(ref, () => ({
    addAdjustment: (hour: number, originalValue: number, adjustedValue: number) => {
      if (activeDecision) {
        const newAdjustment: UserAdjustment = {
          id: `adjustment_${Date.now()}_${hour}`,
          hour,
          originalValue,
          adjustedValue,
          timestamp: new Date().toISOString(),
          decisionId: activeDecision.id
        };

        const updatedDecisions = decisions.map(d =>
          d.id === activeDecision.id
            ? {
                ...d,
                adjustments: [...d.adjustments.filter(adj => adj.hour !== hour), newAdjustment]
              }
            : d
        );

        setDecisions(updatedDecisions);
        setActiveDecision(prev => prev ? {
          ...prev,
          adjustments: [...prev.adjustments.filter(adj => adj.hour !== hour), newAdjustment]
        } : null);

        // 记录到UserContext
        addAdjustment(newAdjustment);
        addInteraction({
          id: `interaction_${Date.now()}`,
          type: 'decision_action',
          component: 'DecisionMaking',
          action: 'add_adjustment',
          timestamp: new Date().toISOString(),
          metadata: {
            decisionId: activeDecision.id,
            hour,
            originalValue,
            adjustedValue,
            adjustmentChange: adjustedValue - originalValue
          }
        });
      }
    }
  }), [activeDecision, decisions]);

  // Create new decision
  const createNewDecision = () => {
    if (!newDecisionLabel.trim() || !newDecisionReason.trim()) {
      setError('Please fill in decision title and reason');
      return;
    }

    if (newDecisionLabel.trim().length < 10) {
      setError('Decision title must be at least 10 characters');
      return;
    }

    if (newDecisionReason.trim().length < 10) {
      setError('Decision reason must be at least 10 characters');
      return;
    }

    const newDecision: Decision = {
      id: `decision_${Date.now()}`,
      label: newDecisionLabel.trim(),
      reason: newDecisionReason.trim(),
      status: 'active',
      adjustments: [],
      createdAt: new Date().toISOString()
    };

    // Set previous decisions to completed status
    const updatedDecisions = decisions.map(d => ({ ...d, status: 'completed' as const }));

    setDecisions([...updatedDecisions, newDecision]);
    setActiveDecision(newDecision);

    // 记录到UserContext，包含当前预测数据
    addDecisionWithPredictionData(newDecision, currentPredictionData);
    addInteraction({
      id: `interaction_${Date.now()}`,
      type: 'decision_action',
      component: 'DecisionMaking',
      action: 'create_decision',
      timestamp: new Date().toISOString(),
      metadata: {
        decisionId: newDecision.id,
        label: newDecision.label,
        predictionDataPoints: currentPredictionData.length
      }
    });

    setNewDecisionLabel('');
    setNewDecisionReason('');
    setShowNewDecisionForm(false);
    setSuccess('Decision created successfully, you can now make prediction adjustments');
    setError(null);
  };



  // Complete current decision
  const completeCurrentDecision = () => {
    if (!activeDecision) return;

    const updatedDecisions = decisions.map(d =>
      d.id === activeDecision.id
        ? { ...d, status: 'completed' as const }
        : d
    );

    setDecisions(updatedDecisions);

    // 更新UserContext中的决策状态
    updateDecision(activeDecision.id, {
      status: 'completed',
      completedAt: new Date().toISOString()
    });
    addInteraction({
      id: `interaction_${Date.now()}`,
      type: 'decision_action',
      component: 'DecisionMaking',
      action: 'complete_decision',
      timestamp: new Date().toISOString(),
      metadata: {
        decisionId: activeDecision.id,
        adjustmentCount: activeDecision.adjustments.length
      }
    });

    setActiveDecision(null);
    setSuccess('Decision completed');
    setError(null);
  };

  // Cancel creating decision
  const cancelNewDecision = () => {
    setShowNewDecisionForm(false);
    setNewDecisionLabel('');
    setNewDecisionReason('');
    setError(null);
  };

  // Calculate adjustment statistics
  const getAdjustmentStats = () => {
    if (!activeDecision) return { adjustedCount: 0, totalChange: 0 };

    const adjustedCount = activeDecision.adjustments.length;
    const totalChange = activeDecision.adjustments.reduce((sum, adj) =>
      sum + (adj.adjustedValue - adj.originalValue), 0
    );

    return { adjustedCount, totalChange };
  };

  const { adjustedCount, totalChange } = getAdjustmentStats();





  return (
    <div className="module-box decision-making-scroll" style={{
      maxHeight: '100%',
      overflowY: 'auto',
      display: 'flex',
      flexDirection: 'column'
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '16px'
      }}>
        <div className="module-title" style={{ margin: 0 }}>Decision-Making Area</div>

        {/* Complete Experiment Button */}
        <button
          onClick={() => {
            console.log('Complete Experiment button clicked');
            if (onCompleteExperiment) {
              onCompleteExperiment();
            } else {
              console.log('onCompleteExperiment is not defined');
            }
          }}
          style={{
            padding: '8px 16px',
            fontSize: '12px',
            fontWeight: '600',
            color: 'white',
            backgroundColor: '#dc2626',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            transition: 'all 0.2s',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            whiteSpace: 'nowrap'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = '#b91c1c';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = '#dc2626';
          }}
          title="Complete and submit your experiment"
        >
          <span>🏁</span>
          Complete Experiment
        </button>
      </div>

      {/* Current decision status display */}
      {activeDecision ? (
        <div style={{
          marginBottom: '16px',
          padding: '12px',
          backgroundColor: '#f8f9fa',
          borderRadius: '6px',
          border: '1px solid #e9ecef'
        }}>
          <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#333', marginBottom: '6px' }}>
            Current Decision: {activeDecision.label}
          </div>
          <div style={{ fontSize: '12px', color: '#666', marginBottom: '8px' }}>
            Reason: {activeDecision.reason}
          </div>
          <div style={{ fontSize: '11px', color: '#888' }}>
            Created: {new Date(activeDecision.createdAt).toLocaleString()}
          </div>
        </div>
      ) : (
        <div style={{
          marginBottom: '16px',
          padding: '12px',
          backgroundColor: '#fff3cd',
          borderRadius: '6px',
          border: '1px solid #ffeaa7',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '13px', color: '#856404' }}>
            Please add and activate a decision first to make prediction adjustments
          </div>
        </div>
      )}

      {/* Decision action buttons */}
      <div style={{
        display: 'flex',
        gap: '8px',
        marginBottom: '16px',
        flexWrap: 'wrap'
      }}>
        <button
          onClick={() => setShowNewDecisionForm(true)}
          disabled={loading || showNewDecisionForm}
          style={{
            flex: 1,
            fontSize: '12px',
            padding: '8px 12px',
            backgroundColor: showNewDecisionForm ? '#6c757d' : '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: showNewDecisionForm ? 'not-allowed' : 'pointer',
            fontWeight: 'bold'
          }}
        >
          New Decision
        </button>

        {activeDecision && (
          <button
            onClick={completeCurrentDecision}
            disabled={loading}
            style={{
              flex: 1,
              fontSize: '12px',
              padding: '8px 12px',
              backgroundColor: loading ? '#6c757d' : '#28a745',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontWeight: 'bold'
            }}
          >
            Complete Current Decision
          </button>
        )}
      </div>

      {/* New decision form */}
      {showNewDecisionForm && (
        <div style={{
          marginBottom: '16px',
          padding: '12px',
          backgroundColor: '#f8f9fa',
          borderRadius: '6px',
          border: '1px solid #dee2e6'
        }}>
          <div style={{ fontSize: '13px', fontWeight: 'bold', marginBottom: '8px', color: '#333' }}>
            Create New Decision
          </div>

          <div style={{ marginBottom: '8px' }}>
            <label style={{ fontSize: '11px', color: '#666', display: 'block', marginBottom: '4px' }}>
              Decision Title * (at least 10 characters)
            </label>
            <input
              type="text"
              value={newDecisionLabel}
              onChange={(e) => setNewDecisionLabel(e.target.value)}
              placeholder="e.g.: Adjust tomorrow's morning peak power forecast"
              style={{
                width: '100%',
                fontSize: '11px',
                padding: '6px',
                border: `1px solid ${newDecisionLabel.length < 10 && newDecisionLabel.length > 0 ? '#dc3545' : '#ced4da'}`,
                borderRadius: '3px',
                boxSizing: 'border-box'
              }}
            />
            <div style={{ fontSize: '10px', color: newDecisionLabel.length < 10 ? '#dc3545' : '#666', marginTop: '2px' }}>
              {newDecisionLabel.length}/10 characters {newDecisionLabel.length < 10 && newDecisionLabel.length > 0 && '(need more characters)'}
            </div>
          </div>

          <div style={{ marginBottom: '12px' }}>
            <label style={{ fontSize: '11px', color: '#666', display: 'block', marginBottom: '4px' }}>
              Decision Reason * (at least 10 characters)
            </label>
            <textarea
              value={newDecisionReason}
              onChange={(e) => setNewDecisionReason(e.target.value)}
              placeholder="Please explain the reason and basis for adjustment, e.g.: Extreme cold weather forecast tomorrow, heating demand will surge..."
              rows={3}
              style={{
                width: '100%',
                fontSize: '11px',
                padding: '6px',
                border: `1px solid ${newDecisionReason.length < 10 && newDecisionReason.length > 0 ? '#dc3545' : '#ced4da'}`,
                borderRadius: '3px',
                resize: 'vertical',
                boxSizing: 'border-box'
              }}
            />
            <div style={{ fontSize: '10px', color: newDecisionReason.length < 10 ? '#dc3545' : '#666', marginTop: '2px' }}>
              {newDecisionReason.length}/10 characters {newDecisionReason.length < 10 && newDecisionReason.length > 0 && '(need more characters)'}
            </div>
          </div>

          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              onClick={createNewDecision}
              disabled={!newDecisionLabel.trim() || !newDecisionReason.trim()}
              style={{
                flex: 1,
                fontSize: '11px',
                padding: '6px 12px',
                backgroundColor: (!newDecisionLabel.trim() || !newDecisionReason.trim()) ? '#6c757d' : '#007bff',
                color: 'white',
                border: 'none',
                borderRadius: '3px',
                cursor: (!newDecisionLabel.trim() || !newDecisionReason.trim()) ? 'not-allowed' : 'pointer'
              }}
            >
              Create Decision
            </button>
            <button
              onClick={cancelNewDecision}
              style={{
                flex: 1,
                fontSize: '11px',
                padding: '6px 12px',
                backgroundColor: '#6c757d',
                color: 'white',
                border: 'none',
                borderRadius: '3px',
                cursor: 'pointer'
              }}
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Adjustment statistics */}
      {activeDecision && (
        <div style={{
          marginBottom: '16px',
          padding: '10px',
          backgroundColor: '#e7f3ff',
          borderRadius: '6px',
          border: '1px solid #b3d9ff'
        }}>
          <div style={{ fontSize: '12px', color: '#0066cc', marginBottom: '4px' }}>
            Adjustment Stats: {adjustedCount} time periods adjusted
          </div>
          <div style={{ fontSize: '12px', color: '#0066cc' }}>
            Impact Range: Total change {totalChange > 0 ? '+' : ''}{totalChange.toFixed(0)} MW
          </div>
        </div>
      )}



      {/* Status message display */}
      {error && (
        <div style={{
          marginTop: '8px',
          padding: '8px',
          backgroundColor: '#f8d7da',
          color: '#721c24',
          borderRadius: '4px',
          fontSize: '11px',
          border: '1px solid #f5c6cb'
        }}>
          {error}
        </div>
      )}

      {success && (
        <div style={{
          marginTop: '8px',
          padding: '8px',
          backgroundColor: '#d4edda',
          color: '#155724',
          borderRadius: '4px',
          fontSize: '11px',
          border: '1px solid #c3e6cb'
        }}>
          {success}
        </div>
      )}

      {/* Decision history */}
      {decisions.length > 0 && (
        <div style={{
          marginTop: '16px',
          paddingTop: '12px',
          borderTop: '1px solid #dee2e6'
        }}>
          <div style={{ fontSize: '12px', fontWeight: 'bold', marginBottom: '8px', color: '#495057' }}>
            Decision History
          </div>
          <div className="decision-making-scroll" style={{
            maxHeight: '200px',
            overflowY: 'auto',
            paddingRight: '4px',
            scrollbarWidth: 'thin',
            scrollbarColor: '#cbd5e0 #f7fafc'
          }}>
            {decisions.map((decision) => (
              <div
                key={decision.id}
                style={{
                  fontSize: '10px',
                  padding: '6px',
                  marginBottom: '4px',
                  backgroundColor: decision.status === 'active' ? '#e7f3ff' : '#f8f9fa',
                  borderRadius: '3px',
                  border: `1px solid ${decision.status === 'active' ? '#b3d9ff' : '#e9ecef'}`
                }}
              >
                <div style={{ fontWeight: 'bold', color: '#333', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span>
                    {decision.label}
                    <span style={{
                      marginLeft: '6px',
                      color: decision.status === 'active' ? '#007bff' : '#28a745',
                      fontSize: '9px'
                    }}>
                      [{decision.status === 'active' ? 'In Progress' : 'Completed'}]
                    </span>
                  </span>

                </div>
                <div style={{ color: '#666', marginTop: '2px' }}>
                  {decision.reason}
                </div>
                <div style={{ color: '#888', marginTop: '2px' }}>
                  <span>Adjustments: {decision.adjustments.length} time periods</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 自定义滚动条样式 */}
      <style>{`
        .decision-making-scroll::-webkit-scrollbar {
          width: 6px;
        }
        .decision-making-scroll::-webkit-scrollbar-track {
          background: #f1f1f1;
          border-radius: 3px;
        }
        .decision-making-scroll::-webkit-scrollbar-thumb {
          background: #cbd5e0;
          border-radius: 3px;
        }
        .decision-making-scroll::-webkit-scrollbar-thumb:hover {
          background: #a0aec0;
        }
      `}</style>
    </div>
  );
});

DecisionMaking.displayName = 'DecisionMaking';

export default DecisionMaking;
