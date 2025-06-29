import sys
from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import joblib
import os

# Add the directory containing the models to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'models')))

# Load the trained models and required data
try:
    # Construct absolute paths to the model files
    base_dir = os.path.dirname(os.path.abspath(__file__))
    best_model_students = joblib.load(os.path.join(base_dir, 'models', 'best_model_students.pkl'))
    best_model_professionals = joblib.load(os.path.join(base_dir, 'models', 'best_model_professionals.pkl'))
    students_cols = joblib.load(os.path.join(base_dir, 'models', 'students_cols.pkl'))
    professionals_cols = joblib.load(os.path.join(base_dir, 'models', 'professionals_cols.pkl'))
except FileNotFoundError:
    print("Error: Model or columns file not found. Please run train_models.py first.")
    sys.exit(1)

# Define preprocessing functions (assuming they are the same as in your original application.py)
def preprocess_student_data(df, required_columns):
    df = df.drop(columns=["Name"])
    for col in ["Have you ever had suicidal thoughts ?", "Family History of Mental Illness"]:
        df[col] = df[col].map({"Yes": 1, "No": 0})
    df["Gender"] = df["Gender"].map({"Male": 1, "Female": 0})
    df = pd.get_dummies(df, columns=["City", "Dietary Habits", "Sleep Duration", "Degree"])
    for col in required_columns:
        if col not in df.columns:
            df[col] = 0
    return df[required_columns]

def preprocess_professional_data(df, required_columns):
    df = df.drop(columns=["Name"])
    for col in ["Have you ever had suicidal thoughts ?", "Family History of Mental Illness"]:
        df[col] = df[col].map({"Yes": 1, "No": 0})
    df["Gender"] = df["Gender"].map({"Male": 1, "Female": 0})
    df = pd.get_dummies(df, columns=["City", "Dietary Habits", "Sleep Duration", "Degree", "Profession"])
    for col in required_columns:
        if col not in df.columns:
            df[col] = 0
    return df[required_columns]

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    user_type = data.get('user_type')
    user_data = data.get('user_data')

    input_df = pd.DataFrame([user_data])

    if user_type == 'student':
        processed_data = preprocess_student_data(input_df, students_cols)
        risk_score = best_model_students.predict_proba(processed_data)[:, 1][0] * 10
    elif user_type == 'professional':
        processed_data = preprocess_professional_data(input_df, professionals_cols)
        risk_score = best_model_professionals.predict_proba(processed_data)[:, 1][0] * 10
    else:
        return jsonify({'error': 'Invalid user type'}), 400

    return jsonify({'prediction': risk_score})

if __name__ == '__main__':
    app.run(debug=True)