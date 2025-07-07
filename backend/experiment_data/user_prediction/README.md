# User Prediction Data

## Overview
This directory contains the baseline AI predictions used in the User Prediction module. This data represents the initial AI model output that participants can interactively adjust through the drag-and-drop interface.

## Files Description

### `baseline_predictions.json`
**Purpose**: AI baseline predictions for January 7, 2022 hourly power consumption with confidence intervals.

**Key Components**:
- 24 hourly predictions with confidence intervals
- Consumption context and period classifications
- Daily cycle patterns and statistics
- Usage instructions for participants and researchers

## Prediction Data Structure

### Hourly Predictions
Each hour includes:
- **Predicted Power**: AI model forecast in megawatts (MW)
- **Confidence Interval**: 95% prediction interval bounds
- **Time Label**: Hour in 24-hour format (00:00 - 23:00)
- **Period Type**: Classification of consumption period
- **Consumption Context**: Explanation of expected activity level

### Daily Consumption Patterns

#### Consumption Periods
1. **Overnight Low (00:00-03:00)**
   - Average: 2,589 MW
   - Minimum daily consumption with base load only
   - Narrow confidence intervals (300 MW width)

2. **Morning Ramp (04:00-07:00)**
   - Average: 3,800 MW
   - Rapid increase as economic activity begins
   - Moderate confidence intervals (350-400 MW width)

3. **Morning Peak (08:00-10:00)**
   - Average: 4,704 MW
   - Peak business and industrial activity
   - Wide confidence intervals (450 MW width)

4. **Midday High (11:00-13:00)**
   - Average: 4,786 MW
   - Sustained high consumption throughout midday
   - Maximum daily consumption period

5. **Afternoon High (14:00-17:00)**
   - Average: 4,698 MW
   - Continued high consumption with gradual decline
   - Sustained business activity

6. **Evening Transition (18:00-19:00)**
   - Average: 4,428 MW
   - Shift from commercial to residential peak
   - Mixed consumption patterns

7. **Evening Decline (20:00-21:00)**
   - Average: 3,809 MW
   - Rapid decline as activity winds down
   - Primarily residential consumption

8. **Night Transition (22:00-23:00)**
   - Average: 3,259 MW
   - Transition to overnight low consumption
   - Preparing for overnight minimum

## Statistical Summary

### Daily Cycle Characteristics
- **Minimum Consumption**: 2,583 MW at 00:00
- **Maximum Consumption**: 4,790 MW at 11:00
- **Peak-to-Valley Ratio**: 1.85
- **Total Daily Variation**: 2,207 MW
- **Average Daily Consumption**: 3,987 MW

### Confidence Interval Analysis
- **Average Interval Width**: 390 MW
- **Narrowest Intervals**: 300 MW (overnight hours)
- **Widest Intervals**: 450 MW (peak consumption hours)
- **Confidence Level**: 95% prediction intervals

## Frontend Integration
This data is used by the `UserPrediction.tsx` component to provide:

### Interactive Visualization
- Line chart with AI baseline (dashed gray line)
- User-adjustable prediction curve (solid red line)
- Confidence interval shading
- Real-time drag-and-drop adjustment capability

### User Interaction Features
- **Point Selection**: Click to select specific hours for adjustment
- **Drag Adjustment**: Drag points vertically to modify predictions
- **Visual Feedback**: Immediate response to user modifications
- **Baseline Comparison**: Constant reference to original AI predictions

### Decision Context Integration
- **Permission Control**: Requires active decision in Decision-Making Area
- **Adjustment Tracking**: Records all modifications with timestamps
- **Statistical Updates**: Real-time calculation of adjustment impacts
- **Reset Capability**: Option to return to original AI baseline

## Model Context

### AI Model Source
- **Algorithm**: XGBoost Regressor
- **Training Data**: Historical winter power consumption (Dec 2021 - Jan 2022)
- **Features**: Temperature, Hour, Day_of_Week, Week_of_Month
- **Target**: January 7, 2022 (Friday) winter extreme cold day

### Prediction Methodology
- **Time Series Approach**: Hourly forecasting with temporal features
- **Weather Integration**: Temperature-based demand adjustments
- **Uncertainty Quantification**: Bootstrap-based confidence intervals
- **Validation**: Time series cross-validation on historical data

## Research Applications

### Human-AI Collaboration
- **Baseline Establishment**: AI provides initial prediction framework
- **Expert Adjustment**: Human experts modify based on domain knowledge
- **Comparative Analysis**: Track differences between AI and human predictions
- **Decision Documentation**: Link adjustments to explicit reasoning

### Interaction Analysis
- **Adjustment Patterns**: Which hours are most frequently modified
- **Magnitude Analysis**: Size and direction of typical adjustments
- **Confidence Relationship**: How confidence intervals influence adjustments
- **Time Allocation**: How long users spend on different time periods

### Prediction Quality
- **Baseline Accuracy**: AI model performance on historical data
- **Human Enhancement**: Whether expert adjustments improve accuracy
- **Uncertainty Calibration**: Relationship between confidence and actual errors
- **Domain Knowledge Integration**: How expert insights complement AI predictions

## Usage Guidelines

### For Experiment Participants
1. **Understand Baseline**: Review AI predictions and confidence intervals
2. **Consider Context**: Use consumption period classifications for guidance
3. **Make Informed Adjustments**: Base modifications on domain knowledge
4. **Document Reasoning**: Provide clear rationale for each adjustment

### For Researchers
1. **Baseline Validation**: Verify AI model predictions are reasonable
2. **Interaction Tracking**: Monitor user adjustment patterns and behaviors
3. **Performance Analysis**: Compare human-adjusted vs AI-only predictions
4. **Method Evaluation**: Assess effectiveness of interactive prediction interface

## Data Quality Notes

### Strengths
- **Realistic Predictions**: Based on actual power system modeling
- **Comprehensive Coverage**: Complete 24-hour prediction cycle
- **Uncertainty Quantification**: Confidence intervals reflect model uncertainty
- **Contextual Information**: Rich metadata for each prediction hour

### Limitations
- **Single Day Focus**: Predictions for one specific date only
- **Winter Bias**: Based on winter-only training data
- **Regional Scope**: Specific to one power grid system
- **Model Constraints**: Limited by XGBoost model capabilities

## Technical Specifications

### Data Format
- **JSON Structure**: Hierarchical organization with metadata
- **Numerical Precision**: Power values in whole megawatts
- **Time Format**: 24-hour clock with hour labels
- **Confidence Intervals**: Lower and upper bounds with interval width

### Frontend Compatibility
- **Chart Integration**: Direct compatibility with Recharts visualization
- **State Management**: Supports React state updates for real-time interaction
- **Type Safety**: TypeScript interfaces for data structure validation
- **Performance**: Optimized for smooth drag-and-drop interactions

## Related Files
- Frontend component: `frontend/src/components/UserPrediction.tsx`
- Decision integration: `frontend/src/components/DecisionMaking.tsx`
- Model training: `backend/calculate_shap_data.py`
- Experiment documentation: `frontend/public/experiment_documentation_en.json`

## Last Updated
January 7, 2024
