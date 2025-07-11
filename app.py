import sys
from flask import Flask, render_template, request, jsonify, redirect, url_for
import pandas as pd
import numpy as np
import joblib
import os
import json
import shap

# Add the directory containing the models to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'models')))

# List of features to exclude from the risk factor breakdown presented to the user
# These are typically non-actionable demographic features.
excluded_features_from_breakdown = ['Age', 'Gender']

# Construct absolute paths to the model files and load them globally
base_dir = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.join(base_dir, 'models')
data_dir = os.path.join(base_dir, 'data')

# --- GLOBAL MODEL AND DATA LOADING WITH ERROR HANDLING ---
try:
    print("Attempting to load models, scalers, and column files...")
    student_model_path = os.path.join(models_dir, 'best_model_students.pkl')
    professional_model_path = os.path.join(models_dir, 'best_model_professionals.pkl')
    student_cols_path = os.path.join(models_dir, 'student_columns.json')
    professional_cols_path = os.path.join(models_dir, 'professional_columns.json')
    student_scaler_path = os.path.join(models_dir, 'student_scaler.pkl')
    professional_scaler_path = os.path.join(models_dir, 'professional_scaler.pkl')

    best_model_students = joblib.load(student_model_path)
    best_model_professionals = joblib.load(professional_model_path)
    student_scaler = joblib.load(student_scaler_path)
    professional_scaler = joblib.load(professional_scaler_path)
    with open(student_cols_path, 'r') as f:
        students_cols = json.load(f)
    with open(professional_cols_path, 'r') as f:
        professionals_cols = json.load(f)

    # Create SHAP Explainers
    student_explainer = shap.TreeExplainer(best_model_students)
    professional_explainer = shap.TreeExplainer(best_model_professionals)
    print("Models, scalers, and column files loaded successfully.")

except FileNotFoundError as e:
    print(f"CRITICAL ERROR: Model or columns file not found at startup: {e}")
    print("Please ensure 'train_models.py' has been run and all model/scaler/json files are in the 'models/' directory and correctly committed to Git.")
    sys.exit(1) # Exit application if critical files are missing
except Exception as e:
    print(f"CRITICAL ERROR: An unexpected error occurred during model loading: {e}")
    sys.exit(1)

# --- Load unique categorical values from the dataset ---
try:
    print("Attempting to load main dataset (final_depression_dataset_1.csv)...")
    df_full_path = os.path.join(base_dir, "final_depression_dataset_1.csv")
    df_full = pd.read_csv(df_full_path)
    print("Main dataset loaded successfully.")

    unique_cities = sorted(df_full['City'].dropna().unique().tolist())
    unique_student_degrees = sorted(df_full[df_full['Working Professional or Student'] == 'Student']['Degree'].dropna().unique().tolist())
    unique_professions = sorted(df_full[df_full['Working Professional or Student'] == 'Working Professional']['Profession'].dropna().unique().tolist())
    all_unique_degrees_from_dataset = sorted(df_full['Degree'].dropna().unique().tolist())
    print("Unique categorical values extracted.")

except FileNotFoundError as e:
    print(f"CRITICAL ERROR: final_depression_dataset_1.csv not found at startup: {e}")
    print("Please ensure 'final_depression_dataset_1.csv' is in the project root and correctly committed to Git.")
    sys.exit(1) # Exit application if critical dataset is missing
except pd.errors.EmptyDataError as e:
    print(f"CRITICAL ERROR: final_depression_dataset_1.csv is empty or malformed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"CRITICAL ERROR: An unexpected error occurred during dataset loading or unique value extraction: {e}")
    sys.exit(1)

# Define preprocessing functions
def preprocess_student_data(df, required_columns, scaler):
    df = df.copy()
    if "Name" in df.columns:
        df = df.drop(columns=["Name"])

    numerical_cols = ['Age', 'CGPA', 'Work/Study Hours']

    # Correctly handle binary features to align with training script
    for col in ["Have you ever had suicidal thoughts ?", "Family History of Mental Illness"]:
        if col in df.columns:
            df[col] = df[col].map({"Yes": 1, "No": 0})
    if "Gender" in df.columns:
        df["Gender"] = df["Gender"].map({"Male": 1, "Female": 0})

    # Convert all other relevant categorical columns to one-hot encoding
    categorical_to_encode = [col for col in ["City", "Dietary Habits", "Sleep Duration", "Degree", "Academic Pressure", "Study Satisfaction", "Financial Stress"] if col in df.columns]
    df_encoded = pd.get_dummies(df, columns=categorical_to_encode, drop_first=False)

    # Align columns before scaling
    for col in required_columns:
        if col not in df_encoded.columns:
            df_encoded[col] = 0
    df_aligned = df_encoded[required_columns]

    # Clip Age
    df_aligned['Age'] = df_aligned['Age'].clip(15, 65)

    # Scale numerical features
    df_aligned[numerical_cols] = scaler.transform(df_aligned[numerical_cols])

    return df_aligned.astype(float)

def preprocess_professional_data(df, required_columns, scaler):
    df = df.copy()
    if "Name" in df.columns:
        df = df.drop(columns=["Name"])

    numerical_cols = ['Age', 'Work/Study Hours']

    # Correctly handle binary features
    for col in ["Have you ever had suicidal thoughts ?", "Family History of Mental Illness"]:
        if col in df.columns:
            df[col] = df[col].map({"Yes": 1, "No": 0})
    if "Gender" in df.columns:
        df["Gender"] = df["Gender"].map({"Male": 1, "Female": 0})

    # Convert all other relevant categorical columns to one-hot encoding
    categorical_to_encode = [col for col in ["City", "Dietary Habits", "Sleep Duration", "Degree", "Profession", "Work Pressure", "Job Satisfaction", "Financial Stress"] if col in df.columns]
    df_encoded = pd.get_dummies(df, columns=categorical_to_encode, drop_first=False)

    # Align columns before scaling
    for col in required_columns:
        if col not in df_encoded.columns:
            df_encoded[col] = 0
    df_aligned = df_encoded[required_columns]

    # Clip Age
    df_aligned['Age'] = df_aligned['Age'].clip(15, 65)

    # Scale numerical features
    df_aligned[numerical_cols] = scaler.transform(df_aligned[numerical_cols])

    return df_aligned.astype(float)


app = Flask(__name__)

# --- Corrected Degree Mapping ---
# The keys of this map now correspond to the actual values in the dataset's 'Profession' column.
degree_map = {
    'Accountant': ['B.Com', 'M.Com', 'CA'],
    'Architect': ['B.Arch', 'M.Arch'],
    'Business Analyst': ['BBA', 'MBA', 'B.Tech'],
    'Chef': ['BHM', 'Diploma in Culinary Arts'],
    'Civil Engineer': ['B.Tech', 'M.Tech', 'BE', 'ME'],
    'Consultant': ['MBA', 'B.Com', 'B.Tech'],
    'Content Writer': ['B.A', 'M.A', 'BJMC'],
    'Customer Support': ["Any Bachelor's Degree"],
    'Data Scientist': ['B.Tech', 'M.Tech', 'M.Sc'],
    'Digital Marketer': ['BBA', 'MBA', 'BMS'],
    'Doctor': ['MBBS', 'MD', 'MS'],
    'Educational Consultant': ['B.Ed', 'M.Ed', 'PhD'],
    'Engineer': ['B.Tech', 'M.Tech', 'BE', 'ME'],
    'Entrepreneur': ['BBA', 'MBA'],
    'Financial Analyst': ['B.Com', 'MBA Finance', 'CFA'],
    'Graphic Designer': ['B.Des', 'BFA', 'Diploma in Graphic Design'],
    'HR Manager': ['BBA', 'MBA', 'PGDM in HR'],
    'Investment Banker': ['MBA Finance', 'CFA'],
    'Judge': ['LLB', 'LLM'],
    'Lawyer': ['LLB', 'LLM'],
    'Manager': ['BBA', 'MBA', 'M.Com'],
    'Marketing Manager': ['BBA', 'MBA', 'BMS'],
    'Mechanical Engineer': ['B.Tech', 'M.Tech', 'BE', 'ME'],
    'Pharmacist': ['B.Pharm', 'M.Pharm'],
    'Pilot': ['B.Sc Aviation', 'Commercial Pilot License'],
    'Research Analyst': ['M.Sc', 'PhD', 'B.A', 'B.Sc'],
    'Researcher': ['M.Sc', 'PhD'],
    'Sales Executive': ["Any Bachelor's Degree"],
    'Software Engineer': ['B.Tech', 'M.Tech', 'BCA', 'MCA'],
    'Teacher': ['B.Ed', 'M.Ed', 'B.A', 'M.A', 'PhD'],
    'Travel Consultant': ['Diploma in Travel and Tourism', 'B.A'],
    'UX/UI Designer': ['B.Des', 'M.Des']
}
# --- End of Corrected Map ---

# --- Resource Loading Functions ---
def load_resources(resource_type):
    file_path = os.path.join(data_dir, f'{resource_type}_resources.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"Support & Awareness Platforms": [], "Research & Studies": [], "Suggestions": []}

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
    # The 'unique_professions' list is the source of truth for the dropdown
    return render_template('professional_form.html', unique_cities=unique_cities, unique_professions=unique_professions)

@app.route('/student_resources')
def student_resources_page():
    resources = load_resources('student')
    return render_template('student_resources.html', resources=resources)

@app.route('/professional_resources')
def professional_resources_page():
    resources = load_resources('professional')
    return render_template('professional_resources.html', resources=resources)

@app.route('/get_suggestions/<user_type>', methods=['GET'])
def get_suggestions(user_type):
    # Ensure user_type is valid to prevent path traversal or unexpected file access
    if user_type not in ['student', 'professional']:
        return jsonify({'error': 'Invalid user type'}), 400
    
    resources = load_resources(user_type)
    suggestions = resources.get("Suggestions", [])
    
    # Shuffle suggestions randomly
    import random
    random.shuffle(suggestions)
    
    # Limit to 10 suggestions
    suggestions = suggestions[:10]
    
    return jsonify(suggestions)

@app.route('/get_degrees', methods=['GET'])
def get_degrees():
    # This now performs a direct, case-sensitive lookup
    profession = request.args.get('profession', '')
    possible_degrees = degree_map.get(profession, ["Other / Not Applicable", "Any Bachelor's Degree", "Any Master's Degree", "PhD"])
    
    # Filter against the degrees that are actually in the dataset
    filtered_degrees = [d for d in possible_degrees if d in all_unique_degrees_from_dataset]
    
    if not filtered_degrees:
        # Fallback if no specific degree matches dataset degrees for the profession
        filtered_degrees = ["Other / Not Applicable"]
    return jsonify({'degrees': filtered_degrees})

def get_final_contributions(shap_values_instance, model_columns, user_input_data):
    """Gets SHAP contributions for only the specific user-selected values."""
    raw_contributions = {feature: float(value) for feature, value in zip(model_columns, shap_values_instance)}
    
    final_contributions = {}
    for feature, value in user_input_data.items():
        # Skip features that are in the exclusion list
        if feature in excluded_features_from_breakdown:
            continue

        # Handle numerical features and binary features directly
        if feature in raw_contributions:
            final_contributions[feature] = raw_contributions[feature]
        # Handle one-hot encoded categorical features
        else:
            # Iterate through raw_contributions to find matching one-hot encoded columns
            for one_hot_col in raw_contributions.keys():
                if one_hot_col.startswith(f"{feature}_"):
                    # Check if the one-hot encoded column corresponds to the user's selected value
                    if one_hot_col == f"{feature}_{value}":
                        final_contributions[feature] = raw_contributions[one_hot_col]
                        break # Found the specific one-hot feature, move to next user input feature

    # Scale the contributions to a percentage, only considering the included features
    total_abs_shap = sum(abs(v) for v in final_contributions.values())
    if total_abs_shap > 0:
        signed_percentages = {k: (v / total_abs_shap) * 100 for k, v in final_contributions.items()}
    else:
        signed_percentages = {k: 0 for k in final_contributions.keys()}
        
    return signed_percentages

@app.route('/predict/student', methods=['POST'])
def predict_student():
    data = request.get_json()
    try:
        user_df = pd.DataFrame([data], index=[0])
        processed_data = preprocess_student_data(user_df.copy(), students_cols, student_scaler)
        if processed_data.empty or processed_data.shape[1] != len(students_cols):
            return jsonify({'error': 'Error processing input data: Feature shape mismatch.'}), 400
    except Exception as e:
        return jsonify({'error': f'Error during data preprocessing: {str(e)}'}), 400

    risk_score = best_model_students.predict_proba(processed_data)[:, 1] * 10
    risk_score = round(float(risk_score[0]), 2)

    shap_values = student_explainer.shap_values(processed_data)
    if isinstance(shap_values, list):
        shap_values_instance = shap_values[1][0]
    else:
        shap_values_instance = shap_values[0]

    feature_contributions = get_final_contributions(shap_values_instance, students_cols, data)

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
    try:
        user_df = pd.DataFrame([data], index=[0])
        processed_data = preprocess_professional_data(user_df.copy(), professionals_cols, professional_scaler)
        if processed_data.empty or processed_data.shape[1] != len(professionals_cols):
             return jsonify({'error': 'Error processing input data: Feature shape mismatch.'}), 400
    except Exception as e:
        return jsonify({'error': f'Error during data preprocessing: {str(e)}'}), 400


    risk_score = best_model_professionals.predict_proba(processed_data)[:, 1] * 10
    risk_score = round(float(risk_score[0]), 2)

    shap_values = professional_explainer.shap_values(processed_data)
    if isinstance(shap_values, list):
        shap_values_instance = shap_values[1][0]
    else:
        shap_values_instance = shap_values[0]
        
    feature_contributions = get_final_contributions(shap_values_instance, professionals_cols, data)

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
    app.run(debug=True)