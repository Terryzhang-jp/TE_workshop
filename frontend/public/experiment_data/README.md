# Experiment Data Collection

## Overview
This directory contains all data files used in the AI-Human Collaborative Power Consumption Prediction Experiment. The data is organized by frontend module and stored in standardized JSON/CSV formats with comprehensive English documentation.

## Directory Structure

```
experiment_data/
├── contextual_information/
│   ├── context_data.json          # Historical scenarios and background context
│   └── README.md                   # Contextual information documentation
├── data_analysis/
│   ├── power_consumption_data.csv  # Hourly time series data (English columns)
│   ├── data_statistics.json       # Statistical summary and metadata
│   └── README.md                   # Data analysis documentation
├── model_interpretability/
│   ├── shap_analysis.json         # SHAP feature importance and insights
│   ├── lime_analysis.json         # LIME local explanations
│   └── README.md                   # Model interpretability documentation
├── user_prediction/
│   ├── baseline_predictions.json  # AI baseline predictions with confidence intervals
│   └── README.md                   # User prediction documentation
└── README.md                       # This overview document
```

## Data Module Descriptions

### 1. Contextual Information
**Purpose**: Provides experimental background and historical context for decision-making.

**Key Data**:
- 7 historical power demand scenarios (June 24-30, 2022)
- Temperature-demand relationships during extreme heat
- System stress indicators and emergency protocols
- Educational context for understanding power grid dynamics

**Frontend Integration**: Used by `ContextInformation.tsx` component to display scenario cards and background information.

### 2. Data Analysis Information
**Purpose**: Contains the actual time series data used for analysis and visualization.

**Key Data**:
- 528 hourly observations (Dec 17, 2021 - Jan 7, 2022)
- Power consumption predictions and actual values
- Temperature forecasts for the analysis period
- Statistical summaries and data quality metrics

**Frontend Integration**: Used by `DataAnalysis.tsx` component for interactive time series visualization and filtering.

### 3. Model Interpretability
**Purpose**: Provides AI model explanation data for understanding prediction rationale.

**Key Data**:
- SHAP feature importance rankings and dependence patterns
- LIME local explanations for specific prediction instances
- Model insights and interpretation guidelines
- Technical details about explainability methods

**Frontend Integration**: Used by `ModelInterpretability.tsx` component for SHAP/LIME visualizations and feature analysis.

### 4. User Prediction
**Purpose**: Contains AI baseline predictions that users can interactively adjust.

**Key Data**:
- 24 hourly baseline predictions for January 7, 2022
- 95% confidence intervals for each prediction
- Consumption period classifications and context
- Daily cycle patterns and statistical analysis

**Frontend Integration**: Used by `UserPrediction.tsx` component for interactive prediction adjustment interface.

## Data Standards and Quality

### Format Standardization
- **JSON Files**: Structured with metadata, main data, and usage instructions
- **CSV Files**: English column headers with consistent data types
- **Documentation**: Comprehensive README files for each module
- **Encoding**: UTF-8 encoding for all text files

### Data Quality Assurance
- **Consistency**: Uniform data structures across modules
- **Completeness**: All required fields populated with valid data
- **Accuracy**: Data matches frontend display exactly
- **Traceability**: Clear links between data files and frontend components

### Metadata Standards
Each JSON file includes:
- **Title and Description**: Clear identification of data purpose
- **Source Information**: Origin and methodology of data collection
- **Usage Instructions**: Guidelines for participants and researchers
- **Technical Specifications**: Implementation details and constraints

## Research Applications

### Data Analysis Capabilities
- **Pattern Recognition**: Temporal and seasonal consumption patterns
- **Model Validation**: Comparison of AI predictions with actual outcomes
- **Human-AI Interaction**: Analysis of user adjustment behaviors
- **Decision Quality**: Assessment of expert modifications to AI predictions

### Experimental Design Support
- **Baseline Establishment**: Consistent starting point for all participants
- **Context Provision**: Rich background information for informed decisions
- **Interaction Tracking**: Structured data for behavioral analysis
- **Performance Measurement**: Quantitative metrics for prediction quality

### Academic Research Value
- **Explainable AI**: Real-world application of SHAP and LIME methods
- **Human-Computer Interaction**: Interface design for expert decision support
- **Energy Systems**: Power consumption prediction and forecasting
- **Decision Science**: Expert judgment in AI-assisted environments

## Technical Specifications

### File Formats
- **JSON**: Primary format for structured data with metadata
- **CSV**: Time series data for analysis and visualization
- **Markdown**: Documentation and usage instructions
- **UTF-8**: Character encoding for international compatibility

### Data Types
- **Numerical**: Power consumption (MW), temperature (°C), confidence intervals
- **Temporal**: Timestamps, hours, dates in ISO format
- **Categorical**: Period types, consumption contexts, feature names
- **Textual**: Descriptions, explanations, usage instructions

### Frontend Compatibility
- **React Integration**: Direct compatibility with TypeScript interfaces
- **Chart Libraries**: Optimized for Recharts visualization components
- **State Management**: Supports real-time updates and user interactions
- **Performance**: Efficient loading and processing for smooth user experience

## Usage Guidelines

### For Experiment Participants
1. **Data Familiarization**: Review README files to understand data context
2. **Module Integration**: Understand how data relates across different interface sections
3. **Decision Context**: Use provided context and explanations for informed adjustments
4. **Quality Awareness**: Consider data limitations when making predictions

### For Researchers
1. **Data Validation**: Verify data accuracy and consistency before analysis
2. **Methodology Understanding**: Review technical specifications and limitations
3. **Interaction Analysis**: Use structured data for behavioral pattern analysis
4. **Result Interpretation**: Consider data constraints when drawing conclusions

### For Developers
1. **Interface Integration**: Use provided data structures for frontend development
2. **Type Safety**: Implement TypeScript interfaces based on JSON schemas
3. **Performance Optimization**: Consider data size and loading patterns
4. **Error Handling**: Implement robust error handling for data loading failures

## Data Limitations and Considerations

### Temporal Scope
- **Winter Focus**: Data primarily from winter period (limited seasonal variation)
- **Short Duration**: 3-week analysis period may not capture long-term patterns
- **Single Year**: 2021-2022 data may not represent multi-year trends

### Geographic Scope
- **Regional System**: Data from specific power grid region
- **Limited Generalizability**: May not apply to other geographic areas
- **System-Specific**: Reflects particular grid characteristics and load patterns

### Model Constraints
- **XGBoost Limitations**: Tree-based model constraints on feature relationships
- **Feature Selection**: Limited to four primary features
- **Training Data**: Model performance bounded by historical data quality

## Maintenance and Updates

### Version Control
- **Data Versioning**: Track changes to data files with clear version history
- **Documentation Updates**: Maintain current README files with any data modifications
- **Frontend Synchronization**: Ensure data changes are reflected in interface components

### Quality Monitoring
- **Regular Validation**: Periodic checks of data integrity and consistency
- **User Feedback**: Incorporate participant feedback on data quality issues
- **Performance Monitoring**: Track data loading and processing performance

## Contact and Support
For questions about this data collection, please refer to:
- Main experiment documentation: `experiment_documentation_en.json`
- Individual module README files for specific data questions
- Frontend component source code for implementation details

## Last Updated
January 7, 2024

---

**Note**: This data collection is designed specifically for the AI-Human Collaborative Power Consumption Prediction Experiment and should be used in conjunction with the complete experimental framework.
