# Model Interpretability Data

## Overview
This directory contains the model interpretability analysis data used in the Model Interpretability module. The data includes SHAP (SHapley Additive exPlanations) and LIME (Local Interpretable Model-agnostic Explanations) analysis results for the XGBoost power consumption prediction model.

## Files Description

### `shap_analysis.json`
**Purpose**: Global feature importance analysis using SHAP TreeExplainer.

**Key Components**:
- Feature importance rankings with percentages
- Feature dependence patterns and insights
- Model performance context and limitations
- Usage instructions for participants and researchers

### `lime_analysis.json`
**Purpose**: Local explanations for individual prediction instances using LIME.

**Key Components**:
- Instance-specific explanations for different hours
- Feature contribution patterns and ranges
- Comparison with SHAP analysis
- Technical implementation details

## Model Interpretability Analysis

### SHAP Analysis Results

#### Feature Importance Ranking
1. **Hour (44.6%)** - Most influential feature
   - Captures daily consumption cycles
   - Clear morning (7-9 AM) and evening (6-8 PM) peaks
   - SHAP value range: [-800, 1200] MW

2. **Day_of_Week (31.0%)** - Second most important
   - Distinguishes weekday vs weekend patterns
   - Weekdays show higher consumption
   - SHAP value range: [-400, 600] MW

3. **Week_of_Month (21.1%)** - Third in importance
   - Captures monthly consumption cycles
   - Gradual variation across weeks
   - SHAP value range: [-300, 400] MW

4. **Temperature (3.4%)** - Least important
   - Limited impact due to winter-only data
   - Constrained temperature range (2.8°C to 14.6°C)
   - SHAP value range: [-16, 194] MW

#### Key Insights
- Temporal features dominate prediction importance
- Temperature impact is constrained by seasonal data limitations
- Clear daily and weekly consumption patterns captured
- Model relies heavily on time-based features

### LIME Analysis Results

#### Local Explanation Examples
- **Midnight (Hour 0)**: Strong negative hour contribution (-580 MW)
- **Morning Peak (Hour 8)**: Strong positive hour contribution (+650 MW)
- **Afternoon (Hour 14)**: Moderate positive contribution (+220 MW)
- **Evening Peak (Hour 19)**: Strong positive contribution (+580 MW)

#### Feature Contribution Patterns
- **Hour**: Dominant feature with largest contribution magnitudes
- **Day_of_Week**: Consistent weekday/weekend differentiation
- **Temperature**: Small but consistently positive contributions
- **Week_of_Month**: Moderate monthly cycle adjustments

## Frontend Integration
This data is used by the `ModelInterpretability.tsx` component to provide:

### SHAP Visualizations
- Feature importance bar charts
- Feature dependence plots for each feature
- Global model behavior understanding
- Feature interaction analysis

### LIME Visualizations
- Local explanation charts for specific hours
- Feature contribution breakdowns
- Instance-specific model behavior
- Prediction reasoning for individual cases

## Methodological Details

### SHAP Implementation
- **Method**: TreeExplainer (exact SHAP values for tree models)
- **Background Data**: Complete training set
- **Computation**: Mean absolute SHAP values for importance ranking
- **Interpretation**: Additive feature contributions to predictions

### LIME Implementation
- **Method**: Tabular explainer with local linear approximation
- **Perturbation**: Gaussian noise for continuous, discrete sampling for categorical
- **Local Model**: Linear regression on perturbed samples
- **Scope**: Instance-specific explanations around prediction points

## Data Quality and Limitations

### Strengths
- **Exact SHAP Values**: TreeExplainer provides mathematically exact attributions
- **Comprehensive Coverage**: Analysis covers all model features
- **Multiple Methods**: SHAP and LIME provide complementary perspectives
- **Realistic Scenarios**: Based on actual power system prediction task

### Limitations
- **Seasonal Bias**: Winter-only data limits temperature importance assessment
- **Geographic Scope**: Single regional grid system
- **Feature Interactions**: Limited analysis of complex feature interactions
- **Temporal Scope**: Short-term prediction focus (24-hour horizon)

## Research Applications

### Model Understanding
- Feature importance hierarchy in power consumption prediction
- Temporal pattern recognition in energy demand
- Impact of weather vs time-based features
- Model behavior under extreme conditions

### Decision Support
- Evidence-based prediction adjustment guidance
- Feature-specific adjustment recommendations
- Understanding of model confidence and limitations
- Validation of domain expert intuitions

### Methodological Insights
- Comparison of global vs local explanation methods
- Effectiveness of tree-based model interpretability
- Feature engineering validation for time series prediction
- Explainable AI in critical infrastructure applications

## Usage Instructions

### For Experiment Participants
1. **Review Feature Rankings**: Understand which features drive predictions
2. **Analyze Dependence Patterns**: See how features relate to predictions
3. **Use Local Explanations**: Understand specific hour predictions
4. **Consider Limitations**: Account for temperature data constraints

### For Researchers
1. **Validate Methods**: Verify SHAP and LIME implementation correctness
2. **Analyze Patterns**: Study temporal feature importance in energy prediction
3. **Compare Approaches**: Contrast global vs local explanation insights
4. **Assess Generalizability**: Consider applicability to other domains

## Technical Specifications

### SHAP Configuration
- TreeExplainer for XGBoost model
- Complete training set as background
- Mean absolute values for importance ranking
- Feature dependence analysis across value ranges

### LIME Configuration
- Tabular explainer with 1000 perturbation samples
- Euclidean distance metric
- Auto kernel width selection
- Linear regression local model

## Related Files
- Model training: `backend/calculate_shap_data.py`
- Frontend component: `frontend/src/components/ModelInterpretability.tsx`
- Original SHAP data: `backend/shap_data_complete.json`
- Experiment documentation: `frontend/public/experiment_documentation_en.json`

## Last Updated
January 7, 2024
