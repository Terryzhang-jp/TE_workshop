# Data Analysis Information

## Overview
This directory contains the power consumption and weather data used in the Data Analysis Information module of the experiment. The data represents 3 weeks of hourly observations during winter extreme cold conditions.

## Files Description

### `power_consumption_data.csv`
**Purpose**: Complete hourly time series data for power consumption and temperature analysis.

**Columns**:
- `timestamp`: Date and time in YYYY-MM-DD HH:MM:SS format
- `predicted_power`: AI model predicted power consumption (MW)
- `actual_power`: Actual recorded power consumption (MW) - available for training period only
- `predicted_temperature`: Weather forecast temperature (°C)

**Data Range**: December 17, 2021 00:00:00 to January 7, 2022 23:00:00 (528 records)

### `data_statistics.json`
**Purpose**: Statistical summary and metadata for the dataset.

**Structure**:
- `metadata`: Dataset description and characteristics
- `data_summary`: Statistical measures for each variable (min, max, mean, std)

## Data Characteristics

### Time Period
- **Start**: December 17, 2021
- **End**: January 7, 2022
- **Duration**: 22 days (3 weeks + 1 day)
- **Frequency**: Hourly observations
- **Total Records**: 528

### Power Consumption
- **Predicted Power Range**: 2,611 - 5,313 MW
- **Actual Power Range**: 2,610 - 4,417 MW (training data only)
- **Peak Demand Pattern**: Typically occurs during morning (7-9 AM) and evening (6-8 PM) hours
- **Weekend vs Weekday**: Lower consumption patterns on weekends

### Temperature Data
- **Range**: 2.77°C to 14.62°C
- **Season**: Winter conditions with limited temperature variation
- **Weather Pattern**: Extreme cold period with relatively stable temperatures
- **Impact**: Limited temperature variation affects feature importance in model analysis

## Frontend Integration
This data is used by the `DataAnalysis.tsx` component to provide:

### Electricity View
- Time series visualization of predicted vs actual power consumption
- Interactive date range filtering
- Dynamic Y-axis scaling with ±5% padding
- Statistical overlays and trend analysis

### Temperature View  
- Temperature time series visualization
- Correlation analysis with power consumption
- Weather pattern identification
- Seasonal context for predictions

## Data Quality Notes

### Completeness
- **Predicted Power**: 100% complete (528/528 records)
- **Actual Power**: Partial (training period only)
- **Temperature**: 100% complete (528/528 records)
- **Timestamps**: Continuous hourly sequence with no gaps

### Accuracy
- Power data based on actual grid measurements
- Temperature data from weather forecast services
- Timestamps in local time zone
- Units standardized (MW for power, °C for temperature)

### Limitations
- **Seasonal Bias**: Winter-only data limits temperature variation
- **Geographic Scope**: Single regional grid system
- **Prediction Period**: Limited to 3-week historical window
- **Weather Dependency**: Forecast accuracy affects temperature reliability

## Research Applications

### Pattern Analysis
- Daily consumption cycles (morning/evening peaks)
- Weekly patterns (weekday vs weekend differences)
- Temperature-demand correlation analysis
- Extreme weather impact assessment

### Model Training Context
- Training data: Periods with actual power measurements
- Prediction target: January 7, 2022 (winter extreme cold day)
- Feature relationships: Temperature, time-based patterns
- Validation approach: Time series cross-validation

### Decision Support
- Historical context for prediction adjustments
- Baseline patterns for comparison
- Extreme condition precedents
- System stress indicators

## Usage Instructions

### For Participants
1. Use the data to understand normal vs extreme consumption patterns
2. Identify temperature-power relationships for decision-making
3. Consider time-of-day and day-of-week effects in adjustments
4. Reference historical extremes when making predictions

### For Researchers
1. Data represents realistic power system conditions
2. Temperature-power correlations reflect actual grid behavior
3. Time series structure suitable for forecasting analysis
4. Extreme weather conditions provide stress-test scenarios

## Data Processing Notes
- Original data in Chinese converted to English column names
- No data cleaning or preprocessing applied beyond translation
- Maintains original temporal resolution and value precision
- Statistical summaries computed from complete dataset

## Last Updated
January 7, 2024

## Related Files
- Original data: `backend/data/worst_day_1_2022_01_07_winter_extreme_cold.csv`
- Frontend component: `frontend/src/components/DataAnalysis.tsx`
- Experiment documentation: `frontend/public/experiment_documentation_en.json`
