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
from research_scraper import update_research_papers # Import the function

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

# --- Load unique categorical values from the dataset (New) ---
try:
    df_full = pd.read_csv("final_depression_dataset_1.csv")
    unique_cities = sorted(df_full['City'].dropna().unique().tolist())
    # Get unique degrees for students only from the dataset
    unique_student_degrees = sorted(df_full[df_full['Working Professional or Student'] == 'Student']['Degree'].dropna().unique().tolist())
    unique_professions = sorted(df_full[df_full['Working Professional or Student'] == 'Working Professional']['Profession'].dropna().unique().tolist())
    # Get all unique degrees from the entire dataset for filtering professional degrees later
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
    "DOCTOR": ["MBBS", "MD", "MS"],
    "ENGINEER": ["B.Tech", "M.Tech", "BE", "ME"],
    "TEACHER": ["B.Ed", "M.Ed", "B.A", "M.A", "Any Bachelor's Degree", "Any Master's Degree", "PhD"],
    "LAWYER": ["LLB", "LLM"],
    "ARCHITECT": ["B.Arch", "M.Arch"],
    "ARTIST": ["BFA", "MFA"],
    "ACCOUNTANT": ["B.Com", "M.Com", "CA"],
    "SOFTWARE DEVELOPER": ["B.Tech", "M.Tech", "BCA", "MCA"],
    "NURSE": ["B.Sc Nursing", "M.Sc Nursing"],
    "JOURNALIST": ["BJMC", "MJMC"],
    "SCIENTIST": ["B.Sc", "M.Sc", "PhD"],
    "ENTREPRENEUR": ["BBA", "MBA"],
    "CONSULTANT": ["MBA", "B.Com", "B.Tech"],
    "MANAGER": ["BBA", "MBA", "M.Com"],
    "DESIGNER": ["B.Des", "M.Des", "BFA"],
    "RESEARCHER": ["M.Sc", "PhD"],
    "POLICE OFFICER": ["B.A", "B.Sc"],
    "ELECTRICIAN": ["Diploma in Electrical Engineering", "ITI Electrician"],
    "MECHANIC": ["Diploma in Mechanical Engineering", "ITI Mechanic"],
    "PLUMBER": ["ITI Plumber"],
    "CARPENTER": ["ITI Carpenter"],
    "CHEF": ["BHM", "Diploma in Culinary Arts"],
    "PILOT": ["B.Sc Aviation", "Commercial Pilot License"],
    "GRAPHIC DESIGNER": ["B.Des", "BFA", "Diploma in Graphic Design"],
    "CONTENT WRITER": ["B.A", "M.A", "BJMC"],
    "HR MANAGER": ["BBA", "MBA", "PGDM in HR"],
    "CUSTOMER SUPPORT": ["Any Bachelor's Degree"],
    "SALES EXECUTIVE": ["Any Bachelor's Degree"],
    "MARKETING MANAGER": ["BBA", "MBA", "BMS"],
    "FINANCIAL ADVISOR": ["B.Com", "MBA Finance", "CFA"],
    "BANKER": ["B.Com", "BBA", "MBA Finance"],
    "CIVIL SERVANT": ["Any Bachelor's Degree"],
    "PHARMACIST": ["B.Pharm", "M.Pharm"],
    "VETERINARIAN": ["BVSc & AH", "MVSc"],
    "PHOTOGRAPHER": ["BFA Photography", "Diploma in Photography"],
    "CHARTED ACCOUNTANT": ["CA"],
    "ACTOR": ["B.A Theatre", "Diploma in Acting"],
    "DANCER": ["B.A Dance", "Diploma in Dance"],
    "MUSICIAN": ["B.A Music", "Diploma in Music"],
    "SPORTSPERSON": ["B.P.Ed", "M.P.Ed"],
    "FASHION DESIGNER": ["B.Des Fashion", "NIFT Diploma"],
    "INTERIOR DESIGNER": ["B.Des Interior", "Diploma in Interior Design"],
    "SOCIAL WORKER": ["BSW", "MSW"],
    "COUNSELOR": ["B.A Psychology", "M.A Psychology"],
    "PHYSIOTHERAPIST": ["BPT", "MPT"],
    "OPTOMETRIST": ["B.Optom", "M.Optom"],
    "DENTIST": ["BDS", "MDS"],
    "AYURVEDIC DOCTOR": ["BAMS", "MD Ayurveda"],
    "HOMOEOPATHIC DOCTOR": ["BHMS", "MD Homoeopathy"],
    "PARAMEDIC": ["B.Sc Paramedical Technology", "Diploma in Paramedical Science"],
    "YOGA INSTRUCTOR": ["Diploma in Yoga", "B.A Yoga"],
    "LIBRARIAN": ["BLIS", "MLIS"],
    "STATISTICIAN": ["B.Sc Statistics", "M.Sc Statistics"],
    "ECONOMIST": ["B.A Economics", "M.A Economics"],
    "HISTORIAN": ["B.A History", "M.A History"],
    "ANTHROPOLOGIST": ["B.A Anthropology", "M.A Anthropology"],
    "SOCIOLOGIST": ["B.A Sociology", "M.A Sociology"],
    "GEOGRAPHER": ["B.Sc Geography", "M.Sc Geography"],
    "GEOLOGIST": ["B.Sc Geology", "M.Sc Geology"],
    "ENVIRONMENTAL SCIENTIST": ["B.Sc Environmental Science", "M.Sc Environmental Science"],
    "AGRICULTURIST": ["B.Sc Agriculture", "M.Sc Agriculture"],
    "FOOD SCIENTIST": ["B.Tech Food Technology", "M.Tech Food Technology"],
    "DAIRY TECHNOLOGIST": ["B.Tech Dairy Technology", "M.Tech Dairy Technology"],
    "SUGAR TECHNOLOGIST": ["B.Tech Sugar Technology", "M.Tech Sugar Technology"],
    "LEATHER TECHNOLOGIST": ["B.Tech Leather Technology", "M.Tech Leather Technology"]
}

# --- Resource Loading Functions ---
def load_resources(resource_type):
    file_path = os.path.join(data_dir, f'{resource_type}_resources.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"Error: Could not load or decode JSON from {file_path}.")
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

@app.route('/get_suggestions/<user_type>')
def get_suggestions(user_type):
    if user_type not in ['student', 'professional']:
        return jsonify({"error": "Invalid user type"}), 400
    
    resources = load_resources(user_type)
    suggestions = resources.get("Suggestions", [])
    
    if len(suggestions) < 5:
        return jsonify(suggestions)
        
    random_suggestions = random.sample(suggestions, 5)
    return jsonify(random_suggestions)

@app.route('/get_degrees', methods=['GET'])
def get_degrees():
    profession = request.args.get('profession', '').upper()
    # Filter degrees from the map to only include those present in the dataset
    possible_degrees = degree_map.get(profession, ["Other / Not Applicable", "Any Bachelor's Degree", "Any Master's Degree", "PhD"])
    # Ensure returned degrees are actually in the dataset's unique degrees
    filtered_degrees = [d for d in possible_degrees if d in all_unique_degrees_from_dataset]
    if not filtered_degrees:
        # Fallback if no specific degree matches dataset degrees for the profession
        filtered_degrees = ["Other / Not Applicable"]
    return jsonify({'degrees': filtered_degrees})

@app.route('/predict/student', methods=['POST'])
def predict_student():
    data = request.get_json()
    user_df = pd.DataFrame([data])
    processed_data = preprocess_student_data(user_df, students_cols)
    risk_score = best_model_students.predict_proba(processed_data)[:, 1] * 10
    risk_score = round(float(risk_score[0]), 2)

    if risk_score <= 4:
        risk_category = "Low Risk"
        message = "Your risk score is low. Keep up the good work on maintaining your mental well-being. It's still important to be mindful of your stress levels and practice self-care."
    elif risk_score <= 7:
        risk_category = "Medium Risk"
        message = "Your risk score is in the medium range. This suggests you may be experiencing some symptoms of stress or other mental health concerns. It would be beneficial to explore resources and consider talking to a professional."
    else:
        risk_category = "High Risk"
        message = "Your risk score is high, which indicates a high probability of mental health distress. It is strongly recommended that you seek professional help. There are resources available to support you."

    return jsonify({
        'redirect_url': url_for('result', risk_score=risk_score, risk_category=risk_category, message=message, user_type='student')
    })

@app.route('/predict/professional', methods=['POST'])
def predict_professional():
    data = request.get_json()
    user_df = pd.DataFrame([data])
    processed_data = preprocess_professional_data(user_df, professionals_cols)
    risk_score = best_model_professionals.predict_proba(processed_data)[:, 1] * 10
    risk_score = round(float(risk_score[0]), 2)

    if risk_score <= 4:
        risk_category = "Low Risk"
        message = "Your risk score is low. Keep up the good work on maintaining your mental well-being. It's still important to be mindful of your stress levels and practice self-care."
    elif risk_score <= 7:
        risk_category = "Medium Risk"
        message = "Your risk score is in the medium range. This suggests you may be experiencing some symptoms of stress or other mental health concerns. It would be beneficial to explore resources and consider talking to a professional."
    else:
        risk_category = "High Risk"
        message = "Your risk score is high, which indicates a high probability of mental health distress. It is strongly recommended that you seek professional help. There are resources available to support you."

    return jsonify({
        'redirect_url': url_for('result', risk_score=risk_score, risk_category=risk_category, message=message, user_type='professional')
    })


@app.route('/result')
def result():
    risk_score = request.args.get('risk_score', 0, type=float)
    risk_category = request.args.get('risk_category', 'Low Risk')
    message = request.args.get('message', 'No message provided.')
    user_type = request.args.get('user_type', 'student') # Default to student
    return render_template('result.html', risk_score=risk_score, risk_category=risk_category, message=message, user_type=user_type)


if __name__ == '__main__':
    # Initialize and start the scheduler
    scheduler = BackgroundScheduler()
    # Schedule update_research_papers to run monthly at midnight on the first day of the month
    scheduler.add_job(func=update_research_papers, trigger=CronTrigger(day=1, hour=0, minute=0))
    scheduler.start()

    # Shut down the scheduler when the app exits
    atexit.register(lambda: scheduler.shutdown())
    
    app.run(debug=True)
