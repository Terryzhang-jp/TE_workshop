import React, { useState, useEffect } from 'react';

interface ExperimentDocumentation {
  experiment_metadata: {
    title: string;
    version: string;
    date_created: string;
    experiment_type: string;
    domain: string;
    estimated_duration: string;
  };
  experiment_overview: {
    purpose: string;
    research_questions: string[];
    target_participants: string;
    study_significance: string;
  };
  background_and_limitations: {
    data_scope: {
      description: string;
      critical_limitations: Array<{
        type: string;
        details: string;
        impact: string;
      }>;
    };
  };
  user_responsibilities: {
    primary_tasks: Array<{
      task: string;
      description: string;
      importance: string;
      time_allocation: string;
    }>;
    behavioral_expectations: string[];
    ethical_considerations: string[];
  };
  system_components: {
    [key: string]: {
      purpose: string;
      content: string[];
      user_interaction?: string[] | string;
      design_rationale: string;
    };
  };
  disclaimer: {
    experimental_nature: string;
    data_limitations: string;
    model_accuracy: string;
    user_responsibility: string;
  };
}

interface ExperimentCoverProps {
  onStartExperiment: () => void;
  onUserReady?: (showLogin: boolean) => void;
}

const ExperimentCover: React.FC<ExperimentCoverProps> = ({ onStartExperiment, onUserReady }) => {
  const [documentation, setDocumentation] = useState<ExperimentDocumentation | null>(null);
  const [activeSection, setActiveSection] = useState<string>('overview');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadDocumentation = async () => {
      try {
        const response = await fetch('/experiment_documentation_en.json');
        if (!response.ok) {
          throw new Error('Failed to load experiment documentation');
        }
        const data = await response.json();
        setDocumentation(data);
      } catch (err) {
        setError('Failed to load experiment documentation');
        console.error('Error loading documentation:', err);
      } finally {
        setLoading(false);
      }
    };

    loadDocumentation();
  }, []);

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        fontSize: '18px',
        color: '#666'
      }}>
        Loading experiment documentation...
      </div>
    );
  }

  if (error || !documentation) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        fontSize: '18px',
        color: '#dc3545'
      }}>
        Error: {error || 'Documentation not available'}
      </div>
    );
  }

  const sections = [
    { id: 'overview', label: 'Overview', icon: '📋' },
    { id: 'limitations', label: 'Data Limitations', icon: '⚠️' },
    { id: 'responsibilities', label: 'Your Role', icon: '👤' },
    { id: 'components', label: 'System Components', icon: '🔧' },
    { id: 'disclaimer', label: 'Important Notes', icon: '📝' }
  ];

  const renderOverview = () => (
    <div className="section-content">
      <h2>Experiment Overview</h2>
      <div className="info-card">
        <h3>Purpose</h3>
        <p>{documentation.experiment_overview.purpose}</p>
      </div>
      
      <div className="info-card">
        <h3>Research Questions</h3>
        <ul>
          {documentation.experiment_overview.research_questions.map((question, index) => (
            <li key={index}>{question}</li>
          ))}
        </ul>
      </div>

      <div className="info-card">
        <h3>Study Significance</h3>
        <p>{documentation.experiment_overview.study_significance}</p>
      </div>

      <div className="metadata-grid">
        <div className="metadata-item">
          <strong>Duration:</strong> {documentation.experiment_metadata.estimated_duration}
        </div>
        <div className="metadata-item">
          <strong>Domain:</strong> {documentation.experiment_metadata.domain}
        </div>
        <div className="metadata-item">
          <strong>Target Participants:</strong> {documentation.experiment_overview.target_participants}
        </div>
      </div>
    </div>
  );

  const renderLimitations = () => (
    <div className="section-content">
      <h2>Critical Data Limitations</h2>
      <div className="warning-banner">
        <strong>Important:</strong> {documentation.background_and_limitations.data_scope.description}
      </div>
      
      {documentation.background_and_limitations.data_scope.critical_limitations.map((limitation, index) => (
        <div key={index} className="limitation-card">
          <h3>{limitation.type}</h3>
          <p><strong>Details:</strong> {limitation.details}</p>
          <p><strong>Impact:</strong> {limitation.impact}</p>
        </div>
      ))}
    </div>
  );

  const renderResponsibilities = () => (
    <div className="section-content">
      <h2>Your Responsibilities</h2>
      
      <div className="info-card">
        <h3>Primary Tasks</h3>
        {documentation.user_responsibilities.primary_tasks.map((task, index) => (
          <div key={index} className="task-item">
            <h4>{task.task}</h4>
            <p>{task.description}</p>
            <div className="task-meta">
              <span><strong>Time:</strong> {task.time_allocation}</span>
              <span><strong>Importance:</strong> {task.importance}</span>
            </div>
          </div>
        ))}
      </div>

      <div className="info-card">
        <h3>Behavioral Expectations</h3>
        <ul>
          {documentation.user_responsibilities.behavioral_expectations.map((expectation, index) => (
            <li key={index}>{expectation}</li>
          ))}
        </ul>
      </div>

      <div className="info-card">
        <h3>Ethical Considerations</h3>
        <ul>
          {documentation.user_responsibilities.ethical_considerations.map((consideration, index) => (
            <li key={index}>{consideration}</li>
          ))}
        </ul>
      </div>
    </div>
  );

  const renderComponents = () => (
    <div className="section-content">
      <h2>System Components</h2>
      {Object.entries(documentation.system_components).map(([key, component]) => (
        <div key={key} className="component-card">
          <h3>{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</h3>
          <p><strong>Purpose:</strong> {component.purpose}</p>
          <p><strong>Design Rationale:</strong> {component.design_rationale}</p>
          
          <div className="component-details">
            <div>
              <strong>Content:</strong>
              <ul>
                {component.content.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>
            </div>
            
            {component.user_interaction && (
              <div>
                <strong>User Interactions:</strong>
                {Array.isArray(component.user_interaction) ? (
                  <ul>
                    {component.user_interaction.map((interaction, index) => (
                      <li key={index}>{interaction}</li>
                    ))}
                  </ul>
                ) : (
                  <p>{component.user_interaction}</p>
                )}
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );

  const renderDisclaimer = () => (
    <div className="section-content">
      <h2>Important Disclaimers</h2>
      
      <div className="disclaimer-card experimental">
        <h3>Experimental Nature</h3>
        <p>{documentation.disclaimer.experimental_nature}</p>
      </div>

      <div className="disclaimer-card limitations">
        <h3>Data Limitations</h3>
        <p>{documentation.disclaimer.data_limitations}</p>
      </div>

      <div className="disclaimer-card accuracy">
        <h3>Model Accuracy</h3>
        <p>{documentation.disclaimer.model_accuracy}</p>
      </div>

      <div className="disclaimer-card responsibility">
        <h3>User Responsibility</h3>
        <p>{documentation.disclaimer.user_responsibility}</p>
      </div>
    </div>
  );

  const renderContent = () => {
    switch (activeSection) {
      case 'overview': return renderOverview();
      case 'limitations': return renderLimitations();
      case 'responsibilities': return renderResponsibilities();
      case 'components': return renderComponents();
      case 'disclaimer': return renderDisclaimer();
      default: return renderOverview();
    }
  };

  return (
    <div className="experiment-cover">
      <div className="cover-header">
        <h1>{documentation.experiment_metadata.title}</h1>
        <div className="header-meta">
          <span>Version {documentation.experiment_metadata.version}</span>
          <span>{documentation.experiment_metadata.experiment_type}</span>
          <span>Created: {documentation.experiment_metadata.date_created}</span>
        </div>
      </div>

      <div className="cover-body">
        <div className="sidebar">
          <nav className="section-nav">
            {sections.map(section => (
              <button
                key={section.id}
                className={`nav-item ${activeSection === section.id ? 'active' : ''}`}
                onClick={() => setActiveSection(section.id)}
              >
                <span className="nav-icon">{section.icon}</span>
                <span className="nav-label">{section.label}</span>
              </button>
            ))}
          </nav>
        </div>

        <div className="main-content">
          {renderContent()}
        </div>
      </div>

      <div className="cover-footer">
        <div className="footer-info">
          <p>Please read all sections carefully before proceeding to the experiment.</p>
          <p>Estimated time: <strong>{documentation.experiment_metadata.estimated_duration}</strong></p>
        </div>
        
        <button
          className="start-experiment-btn"
          onClick={() => onUserReady?.(true)}
        >
          Proceed to User Login
        </button>
      </div>
    </div>
  );
};

export default ExperimentCover;
