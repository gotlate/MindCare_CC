import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from PIL import Image
import base64
from sklearn.model_selection import train_test_split,GridSearchCV

df = pd.read_csv("final_depression_dataset_1.csv")

# Separate the dataset into students and professionals
students_df = df[df['Working Professional or Student'] == "Student"].copy()
professionals_df = df[df['Working Professional or Student'] == "Working Professional"].copy()

# Drop unnecessary columns
students_df = students_df.drop(columns=["Work Pressure", "Profession", "Job Satisfaction"])
professionals_df = professionals_df.drop(columns=["Academic Pressure", "CGPA", "Study Satisfaction"])

# Drop rows with missing values
students_df = students_df.dropna()
professionals_df = professionals_df.dropna()

# Define columns and encoding details
students_columns = ['Name', 'Gender', 'Age', 'City', 'Academic Pressure', 'Have you ever had suicidal thoughts ?', 
                    'Family History of Mental Illness', 'Study Satisfaction', 'Dietary Habits', 'Sleep Duration', 
                    'Degree', 'CGPA', 'Work/Study Hours', 'Financial Stress']
prof_columns = ['Name', 'Gender', 'Age', 'City', 'Work Pressure', 'Have you ever had suicidal thoughts ?', 
                'Family History of Mental Illness', 'Job Satisfaction', 'Dietary Habits', 'Sleep Duration', 
                'Degree', 'Work/Study Hours', 'Financial Stress', 'Profession']

binary_columns_students = ['Gender', 'Have you ever had suicidal thoughts ?', 'Family History of Mental Illness']
non_binary_columns_students = ['City', 'Dietary Habits', 'Sleep Duration', 'Degree']
binary_columns_professionals = ['Gender', 'Have you ever had suicidal thoughts ?', 'Family History of Mental Illness']
non_binary_columns_professionals = ['City', 'Dietary Habits', 'Sleep Duration', 'Degree', 'Profession']

# Label encoding for binary columns and one-hot encoding for non-binary columns

label_encoder = LabelEncoder()
for col in binary_columns_students:
    students_df[col] = label_encoder.fit_transform(students_df[col])
students_df = pd.get_dummies(students_df, columns=non_binary_columns_students)

for col in binary_columns_professionals:
    professionals_df[col] = label_encoder.fit_transform(professionals_df[col])
professionals_df = pd.get_dummies(professionals_df, columns=non_binary_columns_professionals)


X_students = students_df.drop(columns=["Depression", "Working Professional or Student", "Name"])
y_students = label_encoder.fit_transform(students_df["Depression"])
X_professionals = professionals_df.drop(columns=["Depression", "Working Professional or Student", "Name"])
y_professionals = label_encoder.fit_transform(professionals_df["Depression"])

# Split the data into training and test sets for both categories
X_train_students, X_test_students, y_train_students, y_test_students = train_test_split(
    X_students, y_students, test_size=0.2, random_state=42
)
X_train_pro, X_test_pro, y_train_pro, y_test_pro = train_test_split(
    X_professionals, y_professionals, test_size=0.3, random_state=42
)

# Define a parameter grid for grid search
param_grid = {
    'n_estimators': [10,20,30,40,50],  
    'max_depth': [5,10],      
    'min_samples_split': [2,3,4]
}
# Grid search with class weights for students
grid_search_stu = GridSearchCV(RandomForestClassifier(class_weight='balanced', random_state=42), param_grid, cv=5)
grid_search_stu.fit(X_train_students, y_train_students)
best_model_students = grid_search_stu.best_estimator_

grid_search_pro = GridSearchCV(RandomForestClassifier(class_weight='balanced', random_state=42), param_grid, cv=5)
grid_search_pro.fit(X_train_pro, y_train_pro)
best_model_professionals = grid_search_pro.best_estimator_

# # Train the models
# X_students = students_df.drop(columns=["Depression", "Working Professional or Student", "Name"])
# y_students = label_encoder.fit_transform(students_df["Depression"])
# best_model_students = RandomForestClassifier(class_weight='balanced', random_state=42).fit(X_students, y_students)

# X_professionals = professionals_df.drop(columns=["Depression", "Working Professional or Student", "Name"])
# y_professionals = label_encoder.fit_transform(professionals_df["Depression"])
# best_model_professionals = RandomForestClassifier(class_weight='balanced', random_state=42).fit(X_professionals, y_professionals)

# Define the Streamlit app
def main():
    st.set_page_config(page_title="MindCare", page_icon=":brain:", layout="wide")

    tab1, tab2, tab3, tab4 = st.tabs(["Introduction", "Student Page", "Working Professional Page","Articles"])

    # Introduction Page
    with tab1:

        st.markdown(
            """
            <style>
            .main {
                background-color: black; 
            }
            
            .flex-container {
                display: flex;
                flex-direction: row;
                align-items: center;
                justify-content: space-between;
                margin: 20px 0;
            }

            .flex-container img {
                max-width: 45%; /* Adjust to fit half of the container */
                border-radius: 15px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }

            .flex-container .text-content {
                max-width: 50%; /* Adjust width as needed */
                margin-left: 20px;
                font-size: 18px; /* Increased font size */
                line-height: 1.8;
            }

            h1 {
                text-align: center;
                font-weight: bold;
                color: #FFFFFF;
                font-size: 5rem;
            }

            h2 {
                text-align: center;
                font-weight: bold;
                color: #FFFFFF;
                font-size: 40px;
            }

            h3 {
                text-align: center;
                font-weight: bold;
                color: #FFFFFF;
                font-size: 32px;
            }

            .section-header {
                font-size: 30px; /* Increased size for section headers */
                font-weight: bold;
                color: #FFFFFF;
                text-align: center;
            }

            .section-text {
                font-size: 30px; /* Increased size for regular text */
                color: #FFFFFF;
            }

            .text-content p{
                font-size: 25px; /* Increased size for regular text */
                color: #FFFFFF;
            }
            

            </style>
            """,
            unsafe_allow_html=True
        )

        st.title("MindCare")
        st.subheader("Mental Health Prediction Platform")

        # Function to load image
        def get_image_base64(image_path):
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()

       
        image_path = "mental_health_image.jpg"
        image_base64 = get_image_base64(image_path)
        st.markdown(
            f"""
            <div class="flex-container">
                <img src="data:image/jpeg;base64,{image_base64}" alt="Mental Health Image"/>
                <div class="text-content">
                    <p>Welcome to MindCare. </p>
                    <p>This application is designed to 
                    predict the risk of depression among working professionals and students.
                    By providing personalized assessments, we aim to promote mental health awareness and encourage 
                    proactive support.</p>
                </div>
                <br/><br/>
            </div>
            
            """,
            unsafe_allow_html=True
        )

        st.markdown('<div class="section-header"><br/> Navigate to Different Sections: <br/><br/></div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="section-text">
            -Professionals' Mental Health Prediction: Analyze how work-related factors such as job satisfaction, work pressure, and financial stress contribute to mental health status.<br/>
            -Students' Mental Health Prediction: Examine the influence of academic pressure, CGPA, and study satisfaction on mental health.<br/>
            -Insights and Resources: Access articles, tips, and resources for maintaining mental well-being.<br/>
            </div>
            <br/><br/>
            """,
            unsafe_allow_html=True
        )

        
        st.markdown('<div class="section-header">How to Use This Platform:</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="section-text">
            1. Navigate to the Professionals or Students page using the sidebar.<br>
            2. Enter the required information for analysis.<br>
            3. View the prediction and gain insights into your mental health status.
            <br/><br/>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown('<div class="section-text">Your well-being matters! Stay informed and take steps toward a healthier mind.</div>', unsafe_allow_html=True)

        st.write("---")
        st.markdown(
            '<div class="section-text">For any assistance or further information, contact us at: <a href="mailto:support@mentalhealthplatform.com">support@mentalhealthplatform.com</a></div>',
            unsafe_allow_html=True
        )

    # Student Page
    with tab2:
        st.header("Student Mental Health Prediction")
        student_data = {}
        for feature in students_columns:
            if feature == "Name":
                student_data[feature] = st.text_input("Name",key="student_name")
            elif feature == "City":
                student_data[feature] = st.text_input("City",key="student_city")
            elif feature == "CGPA":
                student_data[feature] = st.text_input("CGPA")
            elif feature == "Age":
                student_data[feature] = st.text_input("Age",key="student_age")
            else:
                student_data[feature] = st.selectbox(feature, df[feature].unique(),key="student"+feature)

        if st.button("Predict", key="student_predict"):
            student_df = pd.DataFrame([student_data])
            student_df = preprocess_student_data(student_df, X_students.columns)
            risk_score = best_model_students.predict_proba(student_df)[:, 1] * 10
            show_prediction_page(risk_score[0])

    # Working Professional Page
    with tab3:
        st.header("Professional Mental Health Prediction")
        professional_data = {}
        for feature in prof_columns:
            if feature == "Name":
                professional_data[feature] = st.text_input("Name",key="professional_name")
            elif feature == "City":
                professional_data[feature] = st.text_input("City",key="professional_city")
            elif feature == "Age":
                professional_data[feature] = st.text_input("Age",key="professional_age")
            elif feature == "Profession":
                professional_data[feature] = st.text_input("Profession")    
            else:
                professional_data[feature] = st.selectbox(feature, df[feature].unique(),key="professional"+feature)

        if st.button("Predict", key="professional_predict"):
            professional_df = pd.DataFrame([professional_data])
            professional_df = preprocess_professional_data(professional_df, X_professionals.columns)
            risk_score = best_model_professionals.predict_proba(professional_df)[:, 1] * 10
            show_prediction_page(risk_score[0])
    with tab4:
        st.title("Mental Health Resources")
        st.write("Explore helpful articles and resources on mental health:")

    # Section 1: Articles on Stress Management
        with st.expander("🌱 Articles on Stress Management"):
            st.markdown("""
            <div class="link-section">
                <p><a href="https://www.verywellmind.com/tips-to-reduce-stress-3145195" target="_blank">10 Practical Ways to Reduce Stress</a></p>
                <p><a href="https://www.helpguide.org/articles/stress/stress-management.htm" target="_blank">Stress Management: How to Reduce, Prevent, and Cope with Stress</a></p>
                <p><a href="https://www.mindful.org/meditation/mindfulness-getting-started/" target="_blank">Mindfulness Practices for Beginners</a></p>
            </div>
            """, unsafe_allow_html=True)

    # Section 2: Mental Health Awareness
        with st.expander("💡 Mental Health Awareness"):
            st.markdown("""
            <div class="link-section">
                <p><a href="https://www.mentalhealth.org.uk/publications/how-to-mental-health" target="_blank">A Guide to Understanding Mental Health</a></p>
                <p><a href="https://www.nami.org/About-Mental-Illness/Common-with-Mental-Illness/Anxiety-Disorders" target="_blank">Understanding Anxiety Disorders</a></p>
                <p><a href="https://www.cdc.gov/mentalhealth/learn/index.htm" target="_blank">CDC's Mental Health Basics</a></p>
            </div>
            """, unsafe_allow_html=True)

    # Section 3: Work-Life Balance
        with st.expander("⚖️ Work-Life Balance Tips"):
            st.markdown("""
            <div class="link-section">
                <p><a href="https://www.psychologytoday.com/us/basics/burnout" target="_blank">Understanding and Avoiding Burnout</a></p>
                <p><a href="https://www.themuse.com/advice/10-tips-for-managing-your-worklife-balance" target="_blank">10 Tips for Managing Your Work-Life Balance</a></p>
                <p><a href="https://www.healthline.com/health/work-life-balance" target="_blank">How to Improve Work-Life Balance</a></p>
            </div>
            """, unsafe_allow_html=True)

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

def show_prediction_page(risk_score):
    pulse_css = f"""
    <style>
    .pulse {{
        font-size: 36px;
        font-weight: bold;
        color: white;
        display: inline-block;
        padding: 10px 20px;
        border-radius: 50px;
        display: flex;
        justify-content: center;
        align-items: center;
        animation: pulse-animation {1.5 - 0.1 * risk_score}s infinite;
    }}

    .low-risk {{
        background-color: #32CD32; /* Green */
        box-shadow: 0 0 20px #32CD32;
    }}

    .moderate-risk {{
        background-color: #FFA500; /* Orange */
        box-shadow: 0 0 20px #FFA500;
    }}

    .high-risk {{
        background-color: #FF4500; /* Red */
        box-shadow: 0 0 20px #FF4500;
    }}

    /* Pulse animation */
    @keyframes pulse-animation {{
        0% {{ transform: scale(1); }}
        50% {{ transform: scale(1.1); }}
        100% {{ transform: scale(1); }}
    }}
    </style>
    """

    if risk_score < 4:
        risk_class = "low-risk"
    elif 4 <= risk_score <= 7:
        risk_class = "moderate-risk"
    else:
        risk_class = "high-risk"

    st.markdown(pulse_css, unsafe_allow_html=True)
    st.markdown(
        f"<div class='pulse {risk_class}'>Risk Score: {risk_score:.2f}</div>",
        unsafe_allow_html=True
    )

    if risk_score >= 8:
        st.markdown(
            """
            <style>
            .custom-text {
            margin-top: 2rem; /* Adjust the margin as needed */
            margin-bottom: 2rem;
            font-size: 30px;
            color: white;
            text-align: center;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        st.write('<p class="custom-text">Your risk of depression is high. Please consider seeking professional help.</p>', unsafe_allow_html=True)

    elif risk_score >= 4:
        st.markdown(
            """
            <style>
            .custom-text {
            margin-top: 2rem; /* Adjust the margin as needed */
            margin-bottom: 2rem;
            font-size: 30px;
            color: white;
            text-align: center;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        st.write('<p class="custom-text"> Your risk of depression is moderate. It is a good idea to monitor your mental health.</p>', unsafe_allow_html=True)
    else:
        st.markdown(
            """
            <style>
            .custom-text {
            margin-top: 2rem; /* Adjust the margin as needed */
            margin-bottom: 2rem;
            font-size: 30px;
            color: white;
            text-align: center;
            }
            </style>
            """,
            unsafe_allow_html=True
        )


        st.write('<p class="custom-text"> Your risk of depression is low. Keep up the good work! </p>', unsafe_allow_html=True)
        # st.title(f"{user_type} Mental Health Prediction Result")

    if risk_score >= 7:
        risk_category = "High Risk"
        color = "red"
        message = "It is highly recommended to seek professional mental health assistance."
    elif 4 <= risk_score < 7:
        risk_category = "Medium Risk"
        color = "orange"
        message = "Please monitor your mental health closely and consider talking to someone you trust."
    else:
        risk_category = "Low Risk"
        color = "green"
        message = "You are currently at a low risk of mental health issues. Maintain a healthy lifestyle."


    st.markdown(f"### {risk_category}: {risk_score:.1f}", unsafe_allow_html=True)
    
    st.progress(risk_score / 10) 

    # st.write(message)
    
    # # Additional styling for visual emphasis
    # st.markdown(
    #     f"<div style='text-align: center; color: {color}; font-size: 1.5rem;'>"
    #     f"{risk_category} Level - {risk_score:.1f}/10"
    #     f"</div>",
    #     unsafe_allow_html=True
    # )

if __name__ == "__main__":
    main()