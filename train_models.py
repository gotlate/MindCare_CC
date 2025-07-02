import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix, roc_curve, auc
from sklearn.ensemble import RandomForestClassifier
import joblib
import os
import json
import numpy as np
import matplotlib.pyplot as plt

# --- Data Loading and Preprocessing ---
print("Loading and preprocessing data...")
df = pd.read_csv("final_depression_dataset_1.csv")

# Separate the dataset
students_df = df[df['Working Professional or Student'] == "Student"].copy()
professionals_df = df[df['Working Professional or Student'] == "Working Professional"].copy()

# Drop unnecessary columns
students_df = students_df.drop(columns=["Work Pressure", "Profession", "Job Satisfaction"])
professionals_df = professionals_df.drop(columns=["Academic Pressure", "CGPA", "Study Satisfaction"])

# Drop rows with missing values (initial clean-up)
students_df = students_df.dropna()
professionals_df = professionals_df.dropna()

# --- Feature Engineering and Encoding ---

binary_columns = ['Gender', 'Have you ever had suicidal thoughts ?', 'Family History of Mental Illness']
# Update one_hot_cols to include the previously misidentified ordinal columns
one_hot_cols_students = ['City', 'Dietary Habits', 'Sleep Duration', 'Degree', 'Academic Pressure', 'Study Satisfaction', 'Financial Stress']
one_hot_cols_professionals = ['City', 'Dietary Habits', 'Sleep Duration', 'Degree', 'Profession', 'Work Pressure', 'Job Satisfaction', 'Financial Stress']

label_encoder = LabelEncoder()

# Process Students Data
for col in binary_columns:
    students_df[col] = label_encoder.fit_transform(students_df[col])
students_df = pd.get_dummies(students_df, columns=one_hot_cols_students)

# Process Professionals Data
for col in binary_columns:
    professionals_df[col] = label_encoder.fit_transform(professionals_df[col])
professionals_df = pd.get_dummies(professionals_df, columns=one_hot_cols_professionals)

# --- Prepare Data for Modeling ---
X_students = students_df.drop(columns=["Depression", "Working Professional or Student", "Name"])
y_students = label_encoder.fit_transform(students_df["Depression"])

X_professionals = professionals_df.drop(columns=["Depression", "Working Professional or Student", "Name"])
y_professionals = label_encoder.fit_transform(professionals_df["Depression"])

# --- Model Training and Evaluation ---

# Define the parameter grid from application.py
param_grid = {
    'n_estimators': [10,20,30,40,50],  
    'max_depth': [5,10],      
    'min_samples_split': [2,3,4]
}

# --- Student Model ---
print("--- Training and Evaluating Student Model (Random Forest with GridSearchCV) ---")
X_train_stu, X_test_stu, y_train_stu, y_test_stu = train_test_split(X_students, y_students, test_size=0.2, random_state=42, stratify=y_students)

rf_stu = RandomForestClassifier(class_weight='balanced', random_state=42)
grid_search_stu = GridSearchCV(estimator=rf_stu, param_grid=param_grid, cv=5, scoring='roc_auc', n_jobs=-1, verbose=1)
grid_search_stu.fit(X_train_stu, y_train_stu)
best_model_students = grid_search_stu.best_estimator_
y_pred_stu = best_model_students.predict(X_test_stu)
y_pred_proba_stu = best_model_students.predict_proba(X_test_stu)[:, 1]

print("Best Student Model Parameters:")
print(grid_search_stu.best_params_)
print("Student Model Performance Metrics:")
print(f"Accuracy: {accuracy_score(y_test_stu, y_pred_stu):.4f}")
fpr_stu, tpr_stu, _ = roc_curve(y_test_stu, y_pred_proba_stu)
roc_auc_stu = auc(fpr_stu, tpr_stu)
print(f"AUC Score: {roc_auc_stu:.4f}")
print("Confusion Matrix:", confusion_matrix(y_test_stu, y_pred_stu))
print("Classification Report:", classification_report(y_test_stu, y_pred_stu))

# Plot and save ROC curve for Student Model
plt.figure()
plt.plot(fpr_stu, tpr_stu, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc_stu:.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve - Student Model')
plt.legend(loc="lower right")
plt.savefig('student_model_roc_curve.png')
print("Student model ROC curve saved to student_model_roc_curve.png")
plt.clf()

# --- Professional Model ---
print("--- Training and Evaluating Professional Model (Random Forest with GridSearchCV) ---")
X_train_pro, X_test_pro, y_train_pro, y_test_pro = train_test_split(X_professionals, y_professionals, test_size=0.2, random_state=42, stratify=y_professionals)

rf_pro = RandomForestClassifier(class_weight='balanced', random_state=42)
grid_search_pro = GridSearchCV(estimator=rf_pro, param_grid=param_grid, cv=5, scoring='roc_auc', n_jobs=-1, verbose=1)
grid_search_pro.fit(X_train_pro, y_train_pro)
best_model_professionals = grid_search_pro.best_estimator_
y_pred_proba_pro = best_model_professionals.predict_proba(X_test_pro)[:, 1]

# Apply a threshold of 0.6 for professional model predictions
y_pred_pro = (y_pred_proba_pro >= 0.445).astype(int)

print("Best Professional Model Parameters:")
print(grid_search_pro.best_params_)
print("Professional Model Performance Metrics (Threshold = 0.6):")
print(f"Accuracy: {accuracy_score(y_test_pro, y_pred_pro):.4f}")
fpr_pro, tpr_pro, _ = roc_curve(y_test_pro, y_pred_proba_pro)
roc_auc_pro = auc(fpr_pro, tpr_pro)
print(f"AUC Score: {roc_auc_pro:.4f}")
print("Confusion Matrix:", confusion_matrix(y_test_pro, y_pred_pro))
print("Classification Report:", classification_report(y_test_pro, y_pred_pro))

# Plot and save ROC curve for Professional Model
plt.figure()
plt.plot(fpr_pro, tpr_pro, color='darkgreen', lw=2, label=f'ROC curve (area = {roc_auc_pro:.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve - Professional Model')
plt.legend(loc="lower right")
plt.savefig('professional_model_roc_curve.png')
print("Professional model ROC curve saved to professional_model_roc_curve.png")
plt.clf()

# --- Save Models and Columns ---
models_dir = 'models'
if not os.path.exists(models_dir):
    os.makedirs(models_dir)

joblib.dump(best_model_students, os.path.join(models_dir, 'best_model_students.pkl'))
joblib.dump(best_model_professionals, os.path.join(models_dir, 'best_model_professionals.pkl'))
print(f"Models saved successfully in '{models_dir}' directory.")

# Save the column lists for student and professional models separately
with open(os.path.join(models_dir, 'student_columns.json'), 'w') as f:
    json.dump(X_train_stu.columns.tolist(), f)
with open(os.path.join(models_dir, 'professional_columns.json'), 'w') as f:
    json.dump(X_train_pro.columns.tolist(), f)
print(f"Column lists saved successfully in '{models_dir}' directory.")