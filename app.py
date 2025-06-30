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

# --- Degree Mapping (New) ---
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
    "FOOD SCIENTIST": ["B.Sc Food Technology", "M.Sc Food Technology"],
    "NUTRITIONIST": ["B.Sc Nutrition", "M.Sc Nutrition"],
    "DIETITIAN": ["B.Sc Dietetics", "M.Sc Dietetics"],
    "SPORTS SCIENTIST": ["B.Sc Sports Science", "M.Sc Sports Science"],
    "FORENSIC SCIENTIST": ["B.Sc Forensic Science", "M.Sc Forensic Science"],
    "ARCHAEOLOGIST": ["B.A Archaeology", "M.A Archaeology"],
    "CURATOR": ["M.A Museology"],
    "CONSERVATIONIST": ["M.Sc Conservation"],
    "URBAN PLANNER": ["B.Plan", "M.Plan"],
    "LANDSCAPE ARCHITECT": ["B.L.Arch", "M.L.Arch"],
    "TOUR GUIDE": ["Diploma in Tourism", "B.A Tourism"],
    "HOTEL MANAGER": ["BHM", "Diploma in Hotel Management"],
    "EVENT MANAGER": ["BBA Event Management", "Diploma in Event Management"],
    "PUBLIC RELATIONS OFFICER": ["Bachelors in Mass Communication", "PG Diploma in PR"],
    "ADVERTISING PROFESSIONAL": ["Bachelors in Advertising", "PG Diploma in Advertising"],
    "FILMMAKER": ["B.A Film Studies", "Diploma in Filmmaking"],
    "PHOTOGRAPHER": ["BFA Photography", "Diploma in Photography"],
    "EDITOR": ["B.A English", "Diploma in Editing"],
    "TRANSLATOR": ["B.A Linguistics", "Diploma in Translation"],
    "TECHNICAL WRITER": ["B.Tech", "B.Sc", "B.A English"],
    "WEB DEVELOPER": ["B.Tech CS", "BCA", "MCA", "Diploma in Web Development"],
    "DATA SCIENTIST": ["B.Tech CS", "M.Sc Data Science", "B.Sc Statistics"],
    "CYBERSECURITY ANALYST": ["B.Tech CS", "M.Tech Cybersecurity", "B.Sc IT"],
    "CLOUD ENGINEER": ["B.Tech CS", "M.Tech Cloud Computing"],
    "NETWORK ENGINEER": ["B.Tech ECE", "CCNA", "CCNP"],
    "ROBOTICS ENGINEER": ["B.Tech Robotics", "M.Tech Robotics"],
    "AEROSPACE ENGINEER": ["B.Tech Aerospace", "M.Tech Aerospace"],
    "MARINE ENGINEER": ["B.Tech Marine", "ME Marine"],
    "BIOTECHNOLOGIST": ["B.Tech Biotechnology", "M.Tech Biotechnology"],
    "GENETICIST": ["B.Sc Genetics", "M.Sc Genetics", "PhD Genetics"],
    "MICROBIOLOGIST": ["B.Sc Microbiology", "M.Sc Microbiology"],
    "BIOCHEMIST": ["B.Sc Biochemistry", "M.Sc Biochemistry"],
    "ZOOLOGIST": ["B.Sc Zoology", "M.Sc Zoology"],
    "BOTANIST": ["B.Sc Botany", "M.Sc Botany"],
    "ECOLOGIST": ["B.Sc Ecology", "M.Sc Ecology"],
    "METEOROLOGIST": ["B.Sc Meteorology", "M.Sc Meteorology"],
    "OCEANOGRAPHER": ["B.Sc Oceanography", "M.Sc Oceanography"],
    "ASTRONOMER": ["B.Sc Astronomy", "M.Sc Astronomy", "PhD Astronomy"],
    "PHYSICIST": ["B.Sc Physics", "M.Sc Physics", "PhD Physics"],
    "CHEMIST": ["B.Sc Chemistry", "M.Sc Chemistry", "PhD Chemistry"],
    "MATHEMATICIAN": ["B.Sc Mathematics", "M.Sc Mathematics", "PhD Mathematics"],
    "GEOPHYSICIST": ["B.Sc Geophysics", "M.Sc Geophysics"],
    "CARTOGRAPHER": ["B.Sc Cartography", "M.Sc Cartography"],
    "GEOMATICS ENGINEER": ["B.Tech Geomatics", "M.Tech Geomatics"],
    "MINING ENGINEER": ["B.Tech Mining", "M.Tech Mining"],
    "PETROLEUM ENGINEER": ["B.Tech Petroleum", "M.Tech Petroleum"],
    "CERAMIC ENGINEER": ["B.Tech Ceramic", "M.Tech Ceramic"],
    "TEXTILE ENGINEER": ["B.Tech Textile", "M.Tech Textile"],
    "PLASTIC ENGINEER": ["B.Tech Plastic", "M.Tech Plastic"],
    "FOOD TECHNOLOGIST": ["B.Tech Food Technology", "M.Tech Food Technology"],
    "DAIRY TECHNOLOGIST": ["B.Tech Dairy Technology", "M.Tech Dairy Technology"],
    "SUGAR TECHNOLOGIST": ["B.Tech Sugar Technology", "M.Tech Sugar Technology"],
    "LEATHER TECHNOLOGIST": ["B.Tech Leather Technology", "M.Tech Leather Technology"]
}

@app.route('/get_degrees', methods=['GET'])
def get_degrees():
    profession = request.args.get('profession', '').upper()
    degrees = degree_map.get(profession, ["Other / Not Applicable", "Any Bachelor's Degree", "Any Master's Degree", "PhD"])
    return jsonify({'degrees': degrees})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict/student', methods=['POST'])
def predict_student():
    data = request.get_json()
    print('Student data received in backend:', data)
    user_df = pd.DataFrame([data])
    processed_data = preprocess_student_data(user_df, students_cols)
    risk_score = best_model_students.predict_proba(processed_data)[:, 1] * 10
    prediction_result = float(risk_score[0]) 
    return jsonify({'prediction': prediction_result})

@app.route('/predict/professional', methods=['POST'])
def predict_professional():
    data = request.get_json()
    print('Professional data received in backend:', data)
    user_df = pd.DataFrame([data])
    processed_data = preprocess_professional_data(user_df, professionals_cols)
    risk_score = best_model_professionals.predict_proba(processed_data)[:, 1] * 10
    prediction_result = float(risk_score[0]) 
    return jsonify({'prediction': prediction_result})


if __name__ == '__main__':
    app.run(debug=True)