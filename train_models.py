import pandas as pd
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix, roc_curve, auc
import xgboost as xgb
import joblib
import os
import json
import numpy as np
import matplotlib.pyplot as plt
from imblearn.over_sampling import SMOTE
from sklearn.impute import SimpleImputer

# --- Data Loading and Preprocessing ---
print("Loading and preprocessing data...")
df = pd.read_csv("final_depression_dataset_1.csv")

# Separate the dataset
students_df = df[df['Working Professional or Student'] == "Student"].copy()
professionals_df = df[df['Working Professional or Student'] == "Working Professional"].copy()

# Drop unnecessary columns
students_df = students_df.drop(columns=["Work Pressure", "Profession", "Job Satisfaction"])
professionals_df = professionals_df.drop(columns=["Academic Pressure", "CGPA", "Study Satisfaction"])

# Drop rows with missing values
students_df = students_df.dropna()
professionals_df = professionals_df.dropna()

# --- Feature Engineering and Encoding ---

# Define mappings and columns
binary_columns = ['Gender', 'Have you ever had suicidal thoughts ?', 'Family History of Mental Illness']
ordinal_mapping = {"Low": 0, "Medium": 1, "High": 2}
ordinal_cols_students = ["Academic Pressure", "Study Satisfaction", "Financial Stress"]
ordinal_cols_professionals = ["Work Pressure", "Job Satisfaction", "Financial Stress"]
one_hot_cols_students = ['City', 'Dietary Habits', 'Sleep Duration', 'Degree']
one_hot_cols_professionals = ['City', 'Dietary Habits', 'Sleep Duration', 'Degree', 'Profession']

label_encoder = LabelEncoder()

# Process Students Data
for col in binary_columns:
    students_df[col] = label_encoder.fit_transform(students_df[col])
for col in ordinal_cols_students:
    students_df[col] = students_df[col].map(ordinal_mapping)
students_df = pd.get_dummies(students_df, columns=one_hot_cols_students, drop_first=True)

# Process Professionals Data
for col in binary_columns:
    professionals_df[col] = label_encoder.fit_transform(professionals_df[col])
for col in ordinal_cols_professionals:
    professionals_df[col] = professionals_df[col].map(ordinal_mapping)
professionals_df = pd.get_dummies(professionals_df, columns=one_hot_cols_professionals, drop_first=True)

# --- Prepare Data for Modeling ---
X_students = students_df.drop(columns=["Depression", "Working Professional or Student", "Name"])
y_students = label_encoder.fit_transform(students_df["Depression"])

X_professionals = professionals_df.drop(columns=["Depression", "Working Professional or Student", "Name"])
y_professionals = label_encoder.fit_transform(professionals_df["Depression"])

# Align columns after one-hot encoding to ensure consistency
student_cols = X_students.columns.tolist()
professional_cols = X_professionals.columns.tolist()

all_cols = sorted(list(set(student_cols + professional_cols)))

X_students = X_students.reindex(columns=all_cols, fill_value=0)
X_professionals = X_professionals.reindex(columns=all_cols, fill_value=0)

# --- Model Training and Evaluation ---

# Define XGBoost parameter grid (Original, smaller grid for faster search)
param_grid_xgb = {
    'n_estimators': [100, 200, 300, 500],
    'max_depth': [3, 5, 7, 9],
    'learning_rate': [0.01, 0.05, 0.1],
    'subsample': [0.7, 0.8, 0.9, 1.0],
    'colsample_bytree': [0.7, 0.8, 0.9, 1.0],
    'gamma': [0, 0.1, 0.2]
}

# --- Student Model ---
print("--- Training and Evaluating Student Model (XGBoost) ---")
X_train_stu, X_test_stu, y_train_stu, y_test_stu = train_test_split(X_students, y_students, test_size=0.2, random_state=42, stratify=y_students)

# Impute missing values for student data
print("Imputing missing values for student data...")
imputer_stu = SimpleImputer(strategy='median')
X_train_stu = imputer_stu.fit_transform(X_train_stu)
X_test_stu = imputer_stu.transform(X_test_stu)

xgb_stu = xgb.XGBClassifier(eval_metric='logloss', random_state=42)
random_search_stu = RandomizedSearchCV(estimator=xgb_stu, param_distributions=param_grid_xgb, n_iter=100, cv=5, scoring='roc_auc', n_jobs=-1, verbose=1, random_state=42)
random_search_stu.fit(X_train_stu, y_train_stu)
best_model_students = random_search_stu.best_estimator_
y_pred_stu = best_model_students.predict(X_test_stu)
y_pred_proba_stu = best_model_students.predict_proba(X_test_stu)[:, 1]

print("Best Student Model Parameters:")
print(random_search_stu.best_params_)
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
print("--- Training and Evaluating Professional Model (XGBoost) ---")
X_train_pro, X_test_pro, y_train_pro, y_test_pro = train_test_split(X_professionals, y_professionals, test_size=0.2, random_state=42, stratify=y_professionals)

# Impute missing values
print("Imputing missing values for professional data...")
imputer_pro = SimpleImputer(strategy='median')
X_train_pro = imputer_pro.fit_transform(X_train_pro)
X_test_pro = imputer_pro.transform(X_test_pro)

# Apply SMOTE to the training data
print("Applying SMOTE to professional training data...")
smote = SMOTE(random_state=42)
X_train_pro_resampled, y_train_pro_resampled = smote.fit_resample(X_train_pro, y_train_pro)
print(f"Original training set shape: {y_train_pro.shape[0]}")
print(f"Resampled training set shape: {y_train_pro_resampled.shape[0]}")

# Calculate scale_pos_weight for professional model due to class imbalance
pro_class_counts = pd.Series(y_train_pro_resampled).value_counts()
if 0 in pro_class_counts and 1 in pro_class_counts:
    scale_pos_weight_pro = pro_class_counts[0] / pro_class_counts[1]
else:
    scale_pos_weight_pro = 1 

xgb_pro = xgb.XGBClassifier(eval_metric='logloss', random_state=42, scale_pos_weight=scale_pos_weight_pro)
random_search_pro = RandomizedSearchCV(estimator=xgb_pro, param_distributions=param_grid_xgb, n_iter=100, cv=5, scoring='roc_auc', n_jobs=-1, verbose=1, random_state=42)
random_search_pro.fit(X_train_pro_resampled, y_train_pro_resampled)
best_model_professionals = random_search_pro.best_estimator_
y_pred_pro = best_model_professionals.predict(X_test_pro)
y_pred_proba_pro = best_model_professionals.predict_proba(X_test_pro)[:, 1]

print("Best Professional Model Parameters:")
print(random_search_pro.best_params_)
print("Professional Model Performance Metrics:")
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

# Get original column names before imputation
student_cols_original = X_students.columns.tolist()
professional_cols_original = X_professionals.columns.tolist()
all_cols_original = sorted(list(set(student_cols_original + professional_cols_original)))

with open(os.path.join(models_dir, 'student_columns.json'), 'w') as f:
    json.dump(all_cols_original, f)
with open(os.path.join(models_dir, 'professional_columns.json'), 'w') as f:
    json.dump(all_cols_original, f)
print(f"Column lists saved successfully in '{models_dir}' directory.")
