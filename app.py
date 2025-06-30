import sys
from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import joblib
import os
import json
import pickle

# Add the directory containing the models to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'models')))

# Load the trained models and required data

print(f"Current working directory: {os.getcwd()}")
print(f"__file__ in app.py: {__file__}")
print(f"os.path.dirname(__file__): {os.path.dirname(__file__)}")
print(f"os.path.abspath(__file__): {os.path.abspath(__file__)}")
print(f"os.path.dirname(os.path.abspath(__file__)): {os.path.dirname(os.path.abspath(__file__))}")
base_dir = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.join(base_dir, 'models')

try:
    # Construct absolute paths to the model files
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
    # Load the trained models and column lists
    try:
        # Construct absolute paths to the model files (redundant if loaded globally, but keeping for clarity in this route)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        models_dir = os.path.join(base_dir, 'models')
        student_model = joblib.load(os.path.join(models_dir, 'best_model_students.pkl'))
        professional_model = joblib.load(os.path.join(models_dir, 'best_model_professionals.pkl'))
        
        with open(os.path.join(models_dir, 'student_columns.json'), 'r') as f:
            student_columns = json.load(f)
        with open(os.path.join(models_dir, 'professional_columns.json'), 'r') as f:
            professional_columns = json.load(f)
    except FileNotFoundError:
        return jsonify({'error': 'Model or columns file not found. Please run train_models.py first.'}), 500

    # Add this print statement to check received data
    print('Data received in backend:', data)

    data = request.get_json()
    user_type = data['user_type']
    user_data = data['user_data']

    # Convert user data to DataFrame
    user_df = pd.DataFrame([user_data])

    if user_type == 'student':
        # Preprocess student data
        # Assuming you have a preprocess_student_data function
        processed_data = preprocess_student_data(user_df, student_columns)
        prediction = student_model.predict(processed_data)
    elif user_type == 'professional':
        # Preprocess professional data
        # Assuming you have a preprocess_professional_data function
        processed_data = preprocess_professional_data(user_df, professional_columns)
        prediction = professional_model.predict(processed_data)
    else:
        return jsonify({'error': 'Invalid user type'}), 400

    # Assuming your models predict a single value (0 or 1 for binary classification)
    # Adjust this based on your model's output
    prediction_result = int(prediction[0])

    return jsonify({'prediction': prediction_result})


if __name__ == '__main__':
    app.run(debug=True)