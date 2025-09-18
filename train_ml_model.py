#!/usr/bin/env python3
"""
Train ML Model for Predictive Maintenance
=========================================

This script trains a machine learning model to predict equipment failure risk
based on train operational metrics like speed, fuel efficiency, temperature, etc.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import joblib
import os
from datetime import datetime, timedelta
import json

def generate_synthetic_training_data(n_samples=5000):
    """Generate synthetic training data for predictive maintenance"""
    print(f"🔄 Generating {n_samples} synthetic training samples...")
    
    np.random.seed(42)  # For reproducible results
    
    # Generate base features
    data = {
        'speed': np.random.normal(80, 25, n_samples),  # km/h
        'fuel_efficiency': np.random.normal(75, 15, n_samples),  # %
        'engine_temperature': np.random.normal(85, 12, n_samples),  # °C
        'brake_wear': np.random.uniform(0, 100, n_samples),  # %
        'vibration_level': np.random.exponential(2, n_samples),  # units
        'operating_hours': np.random.uniform(100, 8760, n_samples),  # hours in year
        'distance_traveled': np.random.uniform(10000, 500000, n_samples),  # km
        'load_factor': np.random.uniform(0.3, 1.0, n_samples),  # capacity utilization
        'weather_severity': np.random.randint(1, 6, n_samples),  # 1-5 scale
        'track_condition': np.random.uniform(0.5, 1.0, n_samples),  # quality score
        'maintenance_days_since': np.random.uniform(1, 180, n_samples),  # days
    }
    
    df = pd.DataFrame(data)
    
    # Ensure realistic bounds
    df['speed'] = np.clip(df['speed'], 20, 160)
    df['fuel_efficiency'] = np.clip(df['fuel_efficiency'], 30, 95)
    df['engine_temperature'] = np.clip(df['engine_temperature'], 60, 120)
    
    # Generate failure risk based on realistic relationships
    risk_score = (
        (df['brake_wear'] / 100) * 0.25 +  # Higher brake wear = higher risk
        (df['vibration_level'] / 10) * 0.2 +  # Higher vibration = higher risk
        (df['engine_temperature'] - 85) / 35 * 0.15 +  # Temperature deviation
        (df['maintenance_days_since'] / 180) * 0.2 +  # Time since maintenance
        (1 - df['fuel_efficiency'] / 100) * 0.1 +  # Lower efficiency = higher risk
        (df['operating_hours'] / 8760) * 0.05 +  # More hours = slight risk increase
        (6 - df['weather_severity']) / 5 * 0.05  # Worse weather = higher risk
    )
    
    # Add some noise and ensure 0-1 bounds
    risk_score += np.random.normal(0, 0.1, n_samples)
    df['failure_risk'] = np.clip(risk_score, 0, 1)
    
    # Create binary failure prediction (for classification)
    df['needs_maintenance'] = (df['failure_risk'] > 0.7).astype(int)
    
    # Create categorical risk levels
    df['risk_level'] = pd.cut(df['failure_risk'], 
                             bins=[0, 0.3, 0.6, 0.8, 1.0], 
                             labels=['Low', 'Medium', 'High', 'Critical'])
    
    print("✅ Synthetic training data generated successfully")
    return df

def train_maintenance_models(df):
    """Train both classification and regression models"""
    print("🤖 Training machine learning models...")
    
    # Prepare features (exclude target variables)
    feature_cols = ['speed', 'fuel_efficiency', 'engine_temperature', 'brake_wear',
                   'vibration_level', 'operating_hours', 'distance_traveled', 
                   'load_factor', 'weather_severity', 'track_condition', 'maintenance_days_since']
    
    X = df[feature_cols]
    
    # Train Classification Model (Binary: Needs Maintenance?)
    print("  📊 Training classification model (needs maintenance)...")
    y_class = df['needs_maintenance']
    
    X_train_class, X_test_class, y_train_class, y_test_class = train_test_split(
        X, y_class, test_size=0.2, random_state=42, stratify=y_class
    )
    
    # Scale features
    scaler_class = StandardScaler()
    X_train_class_scaled = scaler_class.fit_transform(X_train_class)
    X_test_class_scaled = scaler_class.transform(X_test_class)
    
    # Train Random Forest Classifier
    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        class_weight='balanced'
    )
    clf.fit(X_train_class_scaled, y_train_class)
    
    # Evaluate classification model
    y_pred_class = clf.predict(X_test_class_scaled)
    print("  📈 Classification Model Performance:")
    print(classification_report(y_test_class, y_pred_class, target_names=['No Maintenance', 'Needs Maintenance']))
    
    # Train Regression Model (Risk Score 0-1)
    print("  📊 Training regression model (failure risk score)...")
    y_reg = df['failure_risk']
    
    X_train_reg, X_test_reg, y_train_reg, y_test_reg = train_test_split(
        X, y_reg, test_size=0.2, random_state=42
    )
    
    # Scale features for regression
    scaler_reg = StandardScaler()
    X_train_reg_scaled = scaler_reg.fit_transform(X_train_reg)
    X_test_reg_scaled = scaler_reg.transform(X_test_reg)
    
    # Train Gradient Boosting Regressor
    reg = GradientBoostingRegressor(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=6,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42
    )
    reg.fit(X_train_reg_scaled, y_train_reg)
    
    # Evaluate regression model
    y_pred_reg = reg.predict(X_test_reg_scaled)
    mse = mean_squared_error(y_test_reg, y_pred_reg)
    r2 = r2_score(y_test_reg, y_pred_reg)
    print(f"  📈 Regression Model Performance:")
    print(f"    Mean Squared Error: {mse:.4f}")
    print(f"    R² Score: {r2:.4f}")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance_class': clf.feature_importances_,
        'importance_reg': reg.feature_importances_
    }).sort_values('importance_reg', ascending=False)
    
    print("  🎯 Top 5 Most Important Features:")
    for _, row in feature_importance.head().iterrows():
        print(f"    {row['feature']}: {row['importance_reg']:.3f} (regression), {row['importance_class']:.3f} (classification)")
    
    # Calculate accuracy metrics
    classifier_accuracy = clf.score(X_test_class_scaled, y_test_class) * 100
    regressor_r2_percent = r2 * 100  # Convert R² to percentage
    
    return clf, reg, scaler_class, scaler_reg, feature_cols, feature_importance, classifier_accuracy, regressor_r2_percent

def save_models(clf, reg, scaler_class, scaler_reg, feature_cols, feature_importance, classifier_accuracy, regressor_r2):
    """Save trained models and metadata"""
    print("💾 Saving trained models...")
    
    # Create models directory
    os.makedirs('models', exist_ok=True)
    
    # Save models
    joblib.dump(clf, 'models/maintenance_classifier.joblib')
    joblib.dump(reg, 'models/failure_risk_regressor.joblib')
    joblib.dump(scaler_class, 'models/scaler_classifier.joblib')
    joblib.dump(scaler_reg, 'models/scaler_regressor.joblib')
    
    # Save metadata
    metadata = {
        'model_version': '1.0',
        'trained_at': datetime.now().isoformat(),
        'feature_columns': feature_cols,
        'model_types': {
            'classifier': 'RandomForestClassifier',
            'regressor': 'GradientBoostingRegressor'
        },
        'model_performance': {
            'classifier_accuracy': round(classifier_accuracy, 1),
            'regressor_r2_score': round(regressor_r2, 1),
            'training_samples': 4000
        },
        'feature_importance': feature_importance.to_dict('records')
    }
    
    with open('models/model_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("✅ Models saved successfully:")
    print("  📁 models/maintenance_classifier.joblib")
    print("  📁 models/failure_risk_regressor.joblib")
    print("  📁 models/scaler_classifier.joblib")
    print("  📁 models/scaler_regressor.joblib")
    print("  📁 models/model_metadata.json")

def main():
    """Main training pipeline"""
    print("🚂 Railway Predictive Maintenance ML Model Training")
    print("=" * 55)
    
    # Generate training data
    df = generate_synthetic_training_data(5000)
    
    # Train models
    clf, reg, scaler_class, scaler_reg, feature_cols, feature_importance, classifier_accuracy, regressor_r2 = train_maintenance_models(df)
    
    # Save models
    save_models(clf, reg, scaler_class, scaler_reg, feature_cols, feature_importance, classifier_accuracy, regressor_r2)
    
    print("\n🎉 Model training completed successfully!")
    print("\nNext steps:")
    print("  1. Models are saved in the 'models/' directory")
    print("  2. The main application will automatically load these models")
    print("  3. Run the application to see ML-powered predictions in action")

if __name__ == "__main__":
    main()
