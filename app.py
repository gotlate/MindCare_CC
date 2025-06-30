import sys
from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import joblib
import os
import json
from nicegui import ui, app

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
    # Filter degrees from the map to only include those present in the dataset
    possible_degrees = degree_map.get(profession, ["Other / Not Applicable", "Any Bachelor's Degree", "Any Master's Degree", "PhD"])
    # Ensure returned degrees are actually in the dataset's unique degrees
    filtered_degrees = [d for d in possible_degrees if d in all_unique_degrees_from_dataset]
    if not filtered_degrees:
        # Fallback if no specific degree matches dataset degrees for the profession
        filtered_degrees = ["Other / Not Applicable"]
    return jsonify({'degrees': filtered_degrees})

# Existing prediction endpoints (keep these as they are)
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


# --- NiceGUI implementation --- #

@ui.page('/')
def index():
    with ui.column(width='100%', class_name='container'):
        ui.html('''
            <div class="hero-section">
                <div class="logo"></div>
                <h1 class="main-title">MindCare</h1>
                <p class="tagline">Your first step towards a healthier, happier mind.</p>
            </div>
        ''')
        with ui.row():
            ui.button('Student', on_click=lambda: ui.open('/student_form'), color='primary')
            ui.button('Working Professional', on_click=lambda: ui.open('/professional_form'), color='primary')


@ui.page('/student_form')
def student_form():
    student_data = {}

    with ui.column(width='100%', class_name='container'):
        ui.label('Student Mental Health Prediction').classes('h2')
        with ui.form() as form:
            ui.input('Name', required=True, on_change=lambda e: student_data.update({'Name': e.value})).props('pattern=[A-Za-z\s]+ oninput=this.value = this.value.toUpperCase()')
            ui.select(unique_cities, label='City', on_change=lambda e: student_data.update({'City': e.value})).props('required')
            ui.select(['Male', 'Female'], label='Gender', on_change=lambda e: student_data.update({'Gender': e.value})).props('required')
            ui.number('Age', required=True, on_change=lambda e: student_data.update({'Age': int(e.value or 0)})).props('min=15 max=65')
            ui.select(['Low', 'Medium', 'High'], label='Academic Pressure', on_change=lambda e: student_data.update({'Academic Pressure': e.value})).props('required')
            ui.select(['Yes', 'No'], label='Have you ever had suicidal thoughts ?', on_change=lambda e: student_data.update({'Have you ever had suicidal thoughts ?': e.value})).props('required')
            ui.select(['Yes', 'No'], label='Family History of Mental Illness', on_change=lambda e: student_data.update({'Family History of Mental Illness': e.value})).props('required')
            ui.select(['Low', 'Medium', 'High'], label='Study Satisfaction', on_change=lambda e: student_data.update({'Study Satisfaction': e.value})).props('required')
            ui.select(['Healthy', 'Average', 'Poor'], label='Dietary Habits', on_change=lambda e: student_data.update({'Dietary Habits': e.value})).props('required')
            ui.select(['Below 5 hours', '5-8 hours', 'More than 8 hours'], label='Sleep Duration', on_change=lambda e: student_data.update({'Sleep Duration': e.value})).props('required')
            ui.select(unique_student_degrees, label='Degree', on_change=lambda e: student_data.update({'Degree': e.value})).props('required')
            ui.input('CGPA', required=True, on_change=lambda e: student_data.update({'CGPA': e.value})).props('pattern=^([0-9](\.\d{1,2})?|10(\.0{1,2})?)$ placeholder="e.g., 8.5, 9.0, 7"')
            ui.number('Work/Study Hours', required=True, on_change=lambda e: student_data.update({'Work/Study Hours': int(e.value or 0)})).props('min=0 max=20')
            ui.select(['Low', 'Medium', 'High'], label='Financial Stress', on_change=lambda e: student_data.update({'Financial Stress': e.value})).props('required')

        prediction_result = ui.label()

        async def predict():
            # Basic client-side validation (can be improved)
            if not all(student_data.values()):
                prediction_result.text = 'Please fill in all fields.'
                return

            try:
                response = await ui.run_javascript(f'''
                    fetch('/predict/student', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json'
                        }},
                        body: JSON.stringify({student_data})
                    }})
                    .then(response => response.json())
                    .then(data => data.prediction)
                ''', respond=False)
                #The above javascript  sends the data to flask endpoint, and recieves the prediction
                #It then displays it without refreshing the page
                prediction = await ui.promise(response)

                prediction_result.text = f'Prediction Risk Score: {prediction:.2f} / 10'
            except Exception as e:
                prediction_result.text = f'Error: {str(e)}'

        ui.button('Predict Student Mental Health', on_click=predict, color='primary')
        ui.button('Back to Home', on_click=lambda: ui.open('/'))


@ui.page('/professional_form')
def professional_form():
    professional_data = {}

    with ui.column(width='100%', class_name='container'):
        ui.label('Working Professional Mental Health Prediction').classes('h2')
        with ui.form() as form:
            ui.input('Name', required=True, on_change=lambda e: professional_data.update({'Name': e.value})).props('pattern=[A-Za-z\s]+ oninput=this.value = this.value.toUpperCase()')
            ui.select(unique_cities, label='City', on_change=lambda e: professional_data.update({'City': e.value})).props('required')
            ui.select(['Male', 'Female'], label='Gender', on_change=lambda e: professional_data.update({'Gender': e.value})).props('required')
            ui.number('Age', required=True, on_change=lambda e: professional_data.update({'Age': int(e.value or 0)})).props('min=15 max=65')
            ui.select(['Low', 'Medium', 'High'], label='Work Pressure', on_change=lambda e: professional_data.update({'Work Pressure': e.value})).props('required')
            ui.select(['Yes', 'No'], label='Have you ever had suicidal thoughts ?', on_change=lambda e: professional_data.update({'Have you ever had suicidal thoughts ?': e.value})).props('required')
            ui.select(['Yes', 'No'], label='Family History of Mental Illness', on_change=lambda e: professional_data.update({'Family History of Mental Illness': e.value})).props('required')
            ui.select(['Low', 'Medium', 'High'], label='Job Satisfaction', on_change=lambda e: professional_data.update({'Job Satisfaction': e.value})).props('required')
            ui.select(['Healthy', 'Average', 'Poor'], label='Dietary Habits', on_change=lambda e: professional_data.update({'Dietary Habits': e.value})).props('required')
            ui.select(['Below 5 hours', '5-8 hours', 'More than 8 hours'], label='Sleep Duration', on_change=lambda e: professional_data.update({'Sleep Duration': e.value})).props('required')
            ui.select(unique_professions, label='Profession', on_change=lambda e: professional_data.update({'Profession': e.value})).props('required')

            #This will generate the degrees based on what the profession is, so this part does need to stay
            async def update_degrees(profession):
                response = await ui.run_javascript(f'''
                    fetch('/get_degrees?profession={profession}', {{
                        method: 'GET',
                        headers: {{
                            'Content-Type': 'application/json'
                        }}
                    }})
                    .then(response => response.json())
                    .then(data => data.degrees)
                ''', respond=False)
                degrees = await ui.promise(response)
                degree_select.options = degrees
                professional_data['Degree'] = degrees[0] if degrees else None  # set the first degree if available

            profession_select = ui.select(unique_professions, label='Profession', on_change=lambda e: (
                professional_data.update({'Profession': e.value}),
                update_degrees(e.value)
            )).props('required')

            degree_select = ui.select([], label='Degree', on_change=lambda e: professional_data.update({'Degree': e.value})).props('required')

            ui.number('Work/Study Hours', required=True, on_change=lambda e: professional_data.update({'Work/Study Hours': int(e.value or 0)})).props('min=0 max=20')
            ui.select(['Low', 'Medium', 'High'], label='Financial Stress', on_change=lambda e: professional_data.update({'Financial Stress': e.value})).props('required')

        prediction_result = ui.label()

        async def predict():
            if not all(professional_data.values()):
                prediction_result.text = 'Please fill in all fields.'
                return

            try:
                response = await ui.run_javascript(f'''
                    fetch('/predict/professional', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json'
                        }},
                        body: JSON.stringify({professional_data})
                    }})
                    .then(response => response.json())
                    .then(data => data.prediction)
                ''', respond=False)

                prediction = await ui.promise(response)

                prediction_result.text = f'Prediction Risk Score: {prediction:.2f} / 10'
            except Exception as e:
                prediction_result.text = f'Error: {str(e)}'

        ui.button('Predict Professional Mental Health', on_click=predict, color='primary')
        ui.button('Back to Home', on_click=lambda: ui.open('/'))


# Replace Flask's run with NiceGUI's
#if __name__ in {'__main__', '__mp_main__'} or '--multiprocessing-fork' in sys.argv:
 #   ui.run(port=5000, reload=False)




with app.app_context():
    if __name__ == '__main__':
        ui.run(port=5000, reload=False)

#if __name__ == '__main__':
 #   app.run(debug=True)