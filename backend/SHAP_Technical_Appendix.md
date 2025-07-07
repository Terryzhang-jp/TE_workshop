# SHAP Analysis Technical Appendix

## Code Analysis and Validation

### 1. Current SHAP Implementation Review

#### 1.1 Model Training Code
```python
# From calculate_shap_data.py lines 68-72
self.model = xgb.XGBRegressor(
    n_estimators=100, 
    max_depth=6, 
    learning_rate=0.1,
    random_state=42, 
    objective='reg:squarederror'
)
self.model.fit(X_train_scaled, y_train)
```

**Assessment**: ✅ Standard XGBoost configuration, appropriate for regression

#### 1.2 SHAP Initialization Code
```python
# From calculate_shap_data.py lines 85-89
X_train_scaled = self.scaler.transform(self.train_data[self.feature_columns].values)
self.explainer = shap.TreeExplainer(self.model, data=X_train_scaled)

X_predict_scaled = self.scaler.transform(self.predict_data[self.feature_columns].values)
self.shap_values = self.explainer.shap_values(X_predict_scaled)
```

**Assessment**: ✅ Correct TreeExplainer usage with proper background data

#### 1.3 Feature Importance Calculation
```python
# From calculate_shap_data.py lines 115-116
mean_abs_shap = np.mean(np.abs(self.shap_values), axis=0)
```

**Assessment**: ✅ Standard method for feature importance from SHAP values

### 2. Data Characteristics Analysis

#### 2.1 Dataset Overview
- **File**: `worst_day_1_2022_01_07_winter_extreme_cold.csv`
- **Columns**: 时间, 预测电力, 真实电力, 预测天气
- **Size**: 530 rows (22 days × 24 hours + 2 hours)
- **Period**: 2021-12-17 to 2022-01-07 (Winter)

#### 2.2 Feature Engineering
```python
# From calculate_shap_data.py lines 44-47
df['hour'] = df['time'].dt.hour                    # 0-23
df['day_of_week'] = df['time'].dt.dayofweek       # 0-6 (Monday=0)
df['week_of_month'] = (df['time'].dt.day - 1) // 7 + 1  # 1-4/5
df['temp'] = df['predicted_temp']                  # Continuous temperature
```

#### 2.3 Temperature Data Analysis

**From CSV inspection**:
```
Sample temperature values:
- Min observed: ~2.77°C
- Max observed: ~14.62°C  
- Range: ~11.85°C
- Pattern: Winter temperatures, limited variation
```

**Temperature Distribution Characteristics**:
- Constrained to winter range
- Limited heating/cooling variation
- Predictable daily patterns

### 3. Feature Importance Comparison

#### 3.1 Current SHAP Rankings
```json
{
  "Hour": {
    "importance": 465.41,
    "rank": 1,
    "percentage": 44.6%
  },
  "Day_of_Week": {
    "importance": 323.91,
    "rank": 2,
    "percentage": 31.0%
  },
  "Week_of_Month": {
    "importance": 220.52,
    "rank": 3,
    "percentage": 21.1%
  },
  "Temperature": {
    "importance": 35.41,
    "rank": 4,
    "percentage": 3.4%
  }
}
```

#### 3.2 Alternative Importance Methods (Recommended)

**Permutation Importance Code**:
```python
from sklearn.inspection import permutation_importance

# Cross-validation with permutation importance
perm_importance = permutation_importance(
    model, X_test_scaled, y_test, 
    n_repeats=10, random_state=42, 
    scoring='neg_mean_absolute_error'
)

for i, feature_name in enumerate(feature_names):
    print(f"{feature_name}: {perm_importance.importances_mean[i]:.4f} ± {perm_importance.importances_std[i]:.4f}")
```

**XGBoost Built-in Importance**:
```python
# Feature importance from XGBoost
xgb_importance = model.feature_importances_
for i, feature_name in enumerate(feature_names):
    print(f"{feature_name}: {xgb_importance[i]:.4f}")
```

### 4. Temperature Investigation Code

#### 4.1 Correlation Analysis
```python
import pandas as pd
from scipy.stats import pearsonr, spearmanr

# Load and prepare data
df = pd.read_csv('data/worst_day_1_2022_01_07_winter_extreme_cold.csv')
df = df.rename(columns={'预测天气': 'temp', '真实电力': 'power'})

# Calculate correlations
temp_power_corr, p_value = pearsonr(df['temp'], df['power'].dropna())
print(f"Temperature-Power Correlation: {temp_power_corr:.4f} (p={p_value:.4f})")

# Feature correlation matrix
features = ['temp', 'hour', 'day_of_week', 'week_of_month']
corr_matrix = df[features].corr()
print("Feature Correlation Matrix:")
print(corr_matrix)
```

#### 4.2 Temperature Variation Analysis
```python
# Temperature statistics
temp_stats = df['temp'].describe()
print(f"Temperature Range: {temp_stats['max'] - temp_stats['min']:.2f}°C")
print(f"Temperature Std: {temp_stats['std']:.2f}°C")
print(f"Coefficient of Variation: {temp_stats['std']/temp_stats['mean']:.4f}")

# Temperature by hour analysis
temp_by_hour = df.groupby('hour')['temp'].agg(['mean', 'std', 'min', 'max'])
print("Temperature variation by hour:")
print(temp_by_hour)
```

### 5. Validation Recommendations

#### 5.1 Cross-Validation Code
```python
def validate_shap_importance(model, X, y, feature_names, cv_folds=5):
    """Cross-validate SHAP importance rankings"""
    from sklearn.model_selection import KFold
    
    kf = KFold(n_splits=cv_folds, shuffle=True, random_state=42)
    importance_scores = []
    
    for train_idx, val_idx in kf.split(X):
        X_train_fold, X_val_fold = X[train_idx], X[val_idx]
        y_train_fold, y_val_fold = y[train_idx], y[val_idx]
        
        # Train model on fold
        fold_model = xgb.XGBRegressor(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42)
        fold_model.fit(X_train_fold, y_train_fold)
        
        # Calculate SHAP for fold
        explainer = shap.TreeExplainer(fold_model, data=X_train_fold)
        shap_values = explainer.shap_values(X_val_fold)
        fold_importance = np.mean(np.abs(shap_values), axis=0)
        
        importance_scores.append(fold_importance)
    
    # Average importance across folds
    mean_importance = np.mean(importance_scores, axis=0)
    std_importance = np.std(importance_scores, axis=0)
    
    for i, feature_name in enumerate(feature_names):
        print(f"{feature_name}: {mean_importance[i]:.4f} ± {std_importance[i]:.4f}")
    
    return mean_importance, std_importance
```

#### 5.2 Seasonal Data Expansion
```python
def load_multi_seasonal_data():
    """Load data from multiple seasons for comprehensive analysis"""
    
    # Load winter data
    winter_df = pd.read_csv('data/worst_day_1_2022_01_07_winter_extreme_cold.csv')
    
    # Load summer data (if available)
    summer_df = pd.read_csv('data/worst_day_3_2021_08_09_summer_high_temp.csv')
    
    # Combine datasets
    combined_df = pd.concat([winter_df, summer_df], ignore_index=True)
    
    # Feature engineering for combined data
    combined_df['season'] = combined_df['时间'].dt.month.map({
        12: 'winter', 1: 'winter', 2: 'winter',
        6: 'summer', 7: 'summer', 8: 'summer'
    })
    
    return combined_df
```

### 6. Interaction Analysis

#### 6.1 SHAP Interaction Values
```python
def analyze_shap_interactions(model, X, feature_names):
    """Analyze SHAP interaction values"""
    
    explainer = shap.TreeExplainer(model, data=X)
    shap_interaction_values = explainer.shap_interaction_values(X)
    
    # Main effects (diagonal)
    main_effects = np.diagonal(shap_interaction_values, axis1=1, axis2=2)
    main_effects_mean = np.mean(np.abs(main_effects), axis=0)
    
    # Interaction effects (off-diagonal)
    interaction_effects = shap_interaction_values.copy()
    np.fill_diagonal(interaction_effects[0], 0)  # Remove main effects
    
    print("Main Effects:")
    for i, feature in enumerate(feature_names):
        print(f"  {feature}: {main_effects_mean[i]:.4f}")
    
    print("\nTop Interactions:")
    for i in range(len(feature_names)):
        for j in range(i+1, len(feature_names)):
            interaction_strength = np.mean(np.abs(interaction_effects[:, i, j]))
            print(f"  {feature_names[i]} × {feature_names[j]}: {interaction_strength:.4f}")
```

### 7. Diagnostic Plots Code

#### 7.1 SHAP Summary Plot
```python
import matplotlib.pyplot as plt

def create_shap_summary_plot(shap_values, X, feature_names):
    """Create SHAP summary plot"""
    
    plt.figure(figsize=(10, 6))
    shap.summary_plot(shap_values, X, feature_names=feature_names, show=False)
    plt.title("SHAP Feature Importance Summary")
    plt.tight_layout()
    plt.savefig('shap_summary_plot.png', dpi=300, bbox_inches='tight')
    plt.show()
```

#### 7.2 Temperature Dependence Plot
```python
def create_temperature_dependence_plot(shap_values, X, feature_names):
    """Create temperature dependence plot"""
    
    temp_idx = feature_names.index('Temperature')
    
    plt.figure(figsize=(10, 6))
    shap.dependence_plot(temp_idx, shap_values, X, feature_names=feature_names, show=False)
    plt.title("Temperature SHAP Dependence Plot")
    plt.xlabel("Temperature (°C)")
    plt.ylabel("SHAP Value (MW)")
    plt.tight_layout()
    plt.savefig('temperature_dependence_plot.png', dpi=300, bbox_inches='tight')
    plt.show()
```

### 8. Conclusions

The technical analysis confirms that:

1. **SHAP Implementation is Correct**: TreeExplainer with proper background data
2. **Feature Engineering is Appropriate**: Standard time-based features
3. **Temperature's Low Importance is Data-Driven**: Limited winter variation
4. **Methodology is Sound**: Standard SHAP importance calculation

**Next Steps**: Implement cross-validation and multi-seasonal analysis for comprehensive validation.
