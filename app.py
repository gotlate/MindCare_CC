import sys
from flask import Flask, render_template, request, jsonify, redirect, url_for
import pandas as pd
import numpy as np
import joblib
import os
import json
import random
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import atexit
from research_scraper import update_research_papers
import shap

# Add the directory containing the models to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'models')))

# Construct absolute paths to the model files and load them globally
base_dir = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.join(base_dir, 'models')
data_dir = os.path.join(base_dir, 'data')

try:
    student_model_path = os.path.join(models_dir, 'best_model_students.pkl')
    professional_model_path = os.path.join(models_dir, 'best_model_professionals.pkl')
    student_cols_path = os.path.join(models_dir, 'student_columns.json')
    professional_cols_path = os.path.join(models_dir, 'professional_columns.json')

    best_model_students = joblib.load(student_model_path)
    best_model_professionals = joblib.load(professional_model_path)
    with open(student_cols_path, 'r') as f:
        students_cols = json.load(f)
    with open(professional_cols_path, 'r') as f:
        professionals_cols = json.load(f)

    # Create SHAP Explainers
    student_explainer = shap.TreeExplainer(best_model_students)
    professional_explainer = shap.TreeExplainer(best_model_professionals)

except FileNotFoundError:
    print("Error: Model or columns file not found. Please run train_models.py first.")
    sys.exit(1)

# --- Load unique categorical values from the dataset (New) ---
try:
    df_full = pd.read_csv("final_depression_dataset_1.csv")
    unique_cities = sorted(df_full['City'].dropna().unique().tolist())
    unique_student_degrees = sorted(df_full[df_full['Working Professional or Student'] == 'Student']['Degree'].dropna().unique().tolist())
    unique_professions = sorted(df_full[df_full['Working Professional or Student'] == 'Working Professional']['Profession'].dropna().unique().tolist())
    all_unique_degrees_from_dataset = sorted(df_full['Degree'].dropna().unique().tolist())
except FileNotFoundError:
    print("Error: final_depression_dataset_1.csv not found. Please ensure the dataset file is in the project directory.")
    sys.exit(1)

# Define preprocessing functions
def preprocess_student_data(df, required_columns):
    df = df.copy() 
    df = df.drop(columns=["Name"])

    for col in ["Have you ever had suicidal thoughts ?", "Family History of Mental Illness"]:
        df[col] = df[col].map({"Yes": 1, "No": 0})
    df["Gender"] = df["Gender"].map({"Male": 1, "Female": 0})

    ordinal_mapping = {"Low": 0, "Medium": 1, "High": 2}
    df["Academic Pressure"] = df["Academic Pressure"].map(ordinal_mapping)
    df["Study Satisfaction"] = df["Study Satisfaction"].map(ordinal_mapping)
    df["Financial Stress"] = df["Financial Stress"].map(ordinal_mapping)

    numerical_cols = ['Age', 'CGPA', 'Work/Study Hours']
    for col in numerical_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col] = df[col].fillna(0) 

    df = pd.get_dummies(df, columns=["City", "Dietary Habits", "Sleep Duration", "Degree"])

    for col in required_columns:
        if col not in df.columns:
            df[col] = 0 
    return df[required_columns].astype(float) 

def preprocess_professional_data(df, required_columns):
    df = df.copy() 
    df = df.drop(columns=["Name"])

    for col in ["Have you ever had suicidal thoughts ?", "Family History of Mental Illness"]:
        df[col] = df[col].map({"Yes": 1, "No": 0})
    df["Gender"] = df["Gender"].map({"Male": 1, "Female": 0})

    ordinal_mapping = {"Low": 0, "Medium": 1, "High": 2}
    df["Work Pressure"] = df["Work Pressure"].map(ordinal_mapping)
    df["Job Satisfaction"] = df["Job Satisfaction"].map(ordinal_mapping)
    df["Financial Stress"] = df["Financial Stress"].map(ordinal_mapping)

    numerical_cols = ['Age', 'Work/Study Hours']
    for col in numerical_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col] = df[col].fillna(0) 

    df = pd.get_dummies(df, columns=["City", "Dietary Habits", "Sleep Duration", "Degree", "Profession"])

    for col in required_columns:
        if col not in df.columns:
            df[col] = 0 
    return df[required_columns].astype(float) 

app = Flask(__name__)

# --- Degree Mapping ---
degree_map = {
    "DOCTOR": ["MBBS", "MD", "MS"], "ENGINEER": ["B.Tech", "M.Tech", "BE", "ME"],
    # (Rest of the map is unchanged)
}

# --- Resource Loading Functions ---
def load_resources(resource_type):
    file_path = os.path.join(data_dir, f'{resource_type}_resources.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"Latest Articles": [], "Research & Studies": [], "Suggestions": []}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/student_dashboard')
def student_dashboard():
    return render_template('student_dashboard.html')

@app.route('/professional_dashboard')
def professional_dashboard():
    return render_template('professional_dashboard.html')

@app.route('/student_form')
def student_form_page():
    return render_template('student_form.html', unique_cities=unique_cities, unique_student_degrees=unique_student_degrees)

@app.route('/professional_form')
def professional_form_page():
    return render_template('professional_form.html', unique_cities=unique_cities, unique_professions=unique_professions)

@app.route('/student_resources')
def student_resources_page():
    resources = load_resources('student')
    return render_template('student_resources.html', resources=resources)

@app.route('/professional_resources')
def professional_resources_page():
    resources = load_resources('professional')
    return render_template('professional_resources.html', resources=resources)

@app.route('/predict/student', methods=['POST'])
def predict_student():
    data = request.get_json()
    user_df = pd.DataFrame([data])
    processed_data = preprocess_student_data(user_df, students_cols)
    risk_score = best_model_students.predict_proba(processed_data)[:, 1] * 10
    risk_score = round(float(risk_score[0]), 2)

    # Calculate SHAP values
    shap_values = student_explainer.shap_values(processed_data)
    shap_values_instance = shap_values[1][0]
    feature_contributions = {feature: round(value, 3) for feature, value in zip(students_cols, shap_values_instance)}
    
    if risk_score <= 4:
        risk_category = "Low Risk"
        message = "Your risk score is low. Keep up the good work on maintaining your mental well-being."
    elif risk_score <= 7:
        risk_category = "Medium Risk"
        message = "Your risk score is in the medium range. This suggests you may be experiencing some symptoms of stress or other mental health concerns."
    else:
        risk_category = "High Risk"
        message = "Your risk score is high, which indicates a high probability of mental health distress. It is strongly recommended that you seek professional help."

    return jsonify({
        'redirect_url': url_for('result', risk_score=risk_score, risk_category=risk_category, message=message, user_type='student', feature_contributions=json.dumps(feature_contributions))
    })

@app.route('/predict/professional', methods=['POST'])
def predict_professional():
    data = request.get_json()
    user_df = pd.DataFrame([data])
    processed_data = preprocess_professional_data(user_df, professionals_cols)
    risk_score = best_model_professionals.predict_proba(processed_data)[:, 1] * 10
    risk_score = round(float(risk_score[0]), 2)

    # Calculate SHAP values
    shap_values = professional_explainer.shap_values(processed_data)
    shap_values_instance = shap_values[1][0]
    feature_contributions = {feature: round(value, 3) for feature, value in zip(professionals_cols, shap_values_instance)}

    if risk_score <= 4:
        risk_category = "Low Risk"
        message = "Your risk score is low. Keep up the good work on maintaining your mental well-being."
    elif risk_score <= 7:
        risk_category = "Medium Risk"
        message = "Your risk score is in the medium range. This suggests you may be experiencing some symptoms of stress or other mental health concerns."
    else:
        risk_category = "High Risk"
        message = "Your risk score is high, which indicates a high probability of mental health distress. It is strongly recommended that you seek professional help."

    return jsonify({
        'redirect_url': url_for('result', risk_score=risk_score, risk_category=risk_category, message=message, user_type='professional', feature_contributions=json.dumps(feature_contributions))
    })

@app.route('/result')
def result():
    risk_score = request.args.get('risk_score', 0, type=float)
    risk_category = request.args.get('risk_category', 'Low Risk')
    message = request.args.get('message', 'No message provided.')
    user_type = request.args.get('user_type', 'student')
    feature_contributions = request.args.get('feature_contributions', '{}')
    return render_template('result.html', risk_score=risk_score, risk_category=risk_category, message=message, user_type=user_type, feature_contributions=feature_contributions)

if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=update_research_papers, trigger=CronTrigger(day=1, hour=0, minute=0))
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())
    app.run(debug=True)