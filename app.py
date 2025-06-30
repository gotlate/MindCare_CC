import sys
from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import joblib
import os
import json

# Add the directory containing the models to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'models')))

# Construct absolute paths to the model files and load them globally
base_dir = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.join(base_dir, 'models')

try:
    student_model_path = os.path.join(models_dir, 'best_model_students.pkl')
    professional_model_path = os.path.join(models_dir, 'best_model_professionals.pkl')
    student_cols_path = os.path.join(models_dir, 'student_columns.json')
    professional_cols_path = os.path.join(models_dir, 'professional_columns.json')

    print(f"Looking for student model at: {student_model_path}")
    print(f"Looking for professional model at: {professional_model_path}")
    print(f"Looking for student columns at: {student_cols_path}")
    print(f"Looking for professional columns at: {professional_cols_path}")

    best_model_students = joblib.load(student_model_path)
    best_model_professionals = joblib.load(professional_model_path)
    with open(student_cols_path, 'r') as f:
        students_cols = json.load(f)
    with open(professional_cols_path, 'r') as f:
        professionals_cols = json.load(f)
except FileNotFoundError:
    print("Error: Model or columns file not found. Please run train_models.py first.")
    sys.exit(1)

# Define preprocessing functions (assuming they are the same as in your original application.py)
def preprocess_student_data(df, required_columns):
    df = df.copy() # Work on a copy to avoid SettingWithCopyWarning
    df = df.drop(columns=["Name"])

    # Map binary columns
    for col in ["Have you ever had suicidal thoughts ?", "Family History of Mental Illness"]:
        df[col] = df[col].map({"Yes": 1, "No": 0})
    df["Gender"] = df["Gender"].map({"Male": 1, "Female": 0})

    # Map ordinal categorical columns
    ordinal_mapping = {"Low": 0, "Medium": 1, "High": 2}
    df["Academic Pressure"] = df["Academic Pressure"].map(ordinal_mapping)
    df["Study Satisfaction"] = df["Study Satisfaction"].map(ordinal_mapping)
    df["Financial Stress"] = df["Financial Stress"].map(ordinal_mapping)

    # Convert numerical columns to numeric type
    numerical_cols = ['Age', 'CGPA', 'Work/Study Hours']
    for col in numerical_cols:
        # Ensure column exists before attempting conversion
        if col in df.columns:
            # Convert to numeric, coercing errors (non-numeric values become NaN)
            df[col] = pd.to_numeric(df[col], errors='coerce')
            # Fill NaN if any, perhaps with mean or median, or 0 if it's acceptable
            df[col] = df[col].fillna(0) # For simplicity, fill with 0

    # One-hot encode non-binary and non-ordinal columns
    df = pd.get_dummies(df, columns=["City", "Dietary Habits", "Sleep Duration", "Degree"])

    # Ensure all required columns are present and in the correct order
    for col in required_columns:
        if col not in df.columns:
            df[col] = 0 # Add missing columns with a default value (e.g., 0)
    return df[required_columns].astype(float) # Ensure all columns are float before passing to model

def preprocess_professional_data(df, required_columns):
    df = df.copy() # Work on a copy
    df = df.drop(columns=["Name"])

    # Map binary columns
    for col in ["Have you ever had suicidal thoughts ?", "Family History of Mental Illness"]:
        df[col] = df[col].map({"Yes": 1, "No": 0})
    df["Gender"] = df["Gender"].map({"Male": 1, "Female": 0})

    # Map ordinal categorical columns
    ordinal_mapping = {"Low": 0, "Medium": 1, "High": 2}
    df["Work Pressure"] = df["Work Pressure"].map(ordinal_mapping)
    df["Job Satisfaction"] = df["Job Satisfaction"].map(ordinal_mapping)
    df["Financial Stress"] = df["Financial Stress"].map(ordinal_mapping)

    # Convert numerical columns to numeric type
    numerical_cols = ['Age', 'Work/Study Hours']
    for col in numerical_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col] = df[col].fillna(0) # For simplicity, fill with 0

    # One-hot encode non-binary and non-ordinal columns
    df = pd.get_dummies(df, columns=["City", "Dietary Habits", "Sleep Duration", "Degree", "Profession"])

    # Ensure all required columns are present and in the correct order
    for col in required_columns:
        if col not in df.columns:
            df[col] = 0 # Add missing columns with a default value (e.g., 0)
    return df[required_columns].astype(float) # Ensure all columns are float before passing to model

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict/student', methods=['POST'])
def predict_student():
    data = request.get_json()
    print('Student data received in backend:', data)
    user_df = pd.DataFrame([data])
    processed_data = preprocess_student_data(user_df, students_cols)
    # Use predict_proba to get the probability of the positive class (index 1)
    risk_score = best_model_students.predict_proba(processed_data)[:, 1] * 10
    prediction_result = float(round(risk_score[0],1)) # Return as float for more precision
    return jsonify({'prediction': prediction_result})

@app.route('/predict/professional', methods=['POST'])
def predict_professional():
    data = request.get_json()
    print('Professional data received in backend:', data)
    user_df = pd.DataFrame([data])
    processed_data = preprocess_professional_data(user_df, professionals_cols)
    # Use predict_proba to get the probability of the positive class (index 1)
    risk_score = best_model_professionals.predict_proba(processed_data)[:, 1] * 10
    prediction_result = float(round(risk_score[0],1)) # Return as float for more precision
    return jsonify({'prediction': prediction_result})


if __name__ == '__main__':
    app.run(debug=True)