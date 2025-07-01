import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV, RandomizedSearchCV
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

# Ensure column order is consistent after preprocessing and before splitting
# Align columns after one-hot encoding to ensure consistency
student_cols = list(X_students.columns)
professional_cols = list(X_professionals.columns)


all_cols = sorted(list(set(student_cols + professional_cols)))

X_students = X_students.reindex(columns=all_cols, fill_value=0)
X_professionals = X_professionals.reindex(columns=all_cols, fill_value=0)

# --- Model Training and Evaluation ---

# Define a larger parameter grid for RandomizedSearch
param_grid_xgb_large = {
    'n_estimators': [100, 200, 300, 500],
    'max_depth': [3, 5, 7, 9],
    'learning_rate': [0.01, 0.05, 0.1],
    'subsample': [0.7, 0.8, 0.9, 1.0],
    'colsample_bytree': [0.7, 0.8, 0.9, 1.0],
    'gamma': [0, 0.1, 0.2]
}

# Define the original, smaller parameter grid for GridSearchCV
param_grid_xgb_small = {
    'n_estimators': [100, 200],
    'max_depth': [3, 5, 7],
    'learning_rate': [0.05, 0.1],
    'subsample': [0.7, 1.0],
    'colsample_bytree': [0.7, 1.0]
}

# --- Student Model ---
print("--- Training and Evaluating Student Model (XGBoost with RandomizedSearchCV) ---")
X_train_stu, X_test_stu, y_train_stu, y_test_stu = train_test_split(X_students, y_students, test_size=0.2, random_state=42, stratify=y_students)

# Impute missing values for student data
print("Imputing missing values for student data...")
# Ensure X_train_stu and X_test_stu are pandas DataFrames before imputation
X_train_stu = pd.DataFrame(X_train_stu, columns=all_cols)
X_test_stu = pd.DataFrame(X_test_stu, columns=all_cols)

# Impute missing values for student data
print("Imputing missing values for student data...")
imputer_stu = SimpleImputer(strategy='median')
X_train_stu = imputer_stu.fit_transform(X_train_stu)
X_test_stu = imputer_stu.transform(X_test_stu)

xgb_stu = xgb.XGBClassifier(eval_metric='logloss', random_state=42)
random_search_stu = RandomizedSearchCV(estimator=xgb_stu, param_distributions=param_grid_xgb_large, n_iter=100, cv=5, scoring='roc_auc', n_jobs=-1, verbose=1, random_state=42)
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
print("--- Training and Evaluating Professional Model (XGBoost with GridSearchCV, SMOTE, and scale_pos_weight) ---")
X_train_pro, X_test_pro, y_train_pro, y_test_pro = train_test_split(X_professionals, y_professionals, test_size=0.2, random_state=42, stratify=y_professionals)

# Ensure X_train_pro and X_test_pro are pandas DataFrames with correct columns before imputation
X_train_pro = pd.DataFrame(X_train_pro, columns=all_cols)
X_test_pro = pd.DataFrame(X_test_pro, columns=all_cols)

# Add print statements to check shapes and column counts before imputation
print(f"Shape of X_train_pro before imputation: {X_train_pro.shape}")
print(f"Length of all_cols: {len(all_cols)}")
print(f"Columns of X_train_pro before imputation: {X_train_pro.columns.tolist()}")


# Impute missing values for professional data
print("Imputing missing values for professional data...")
imputer_pro = SimpleImputer(strategy='median')
X_train_pro_imputed = imputer_pro.fit_transform(X_train_pro)
X_test_pro_imputed = imputer_pro.transform(X_test_pro)

# Calculate scale_pos_weight for professional model due to class imbalance
print(f"Shape of y_train_pro before value_counts: {y_train_pro.shape}")
pro_class_counts = pd.Series(y_train_pro).value_counts()
if 0 in pro_class_counts and 1 in pro_class_counts and pro_class_counts[1] > 0:
    scale_pos_weight_pro = pro_class_counts[0] / pro_class_counts[1]
else:
    scale_pos_weight_pro = 1
print(f"Calculated scale_pos_weight for professional model: {scale_pos_weight_pro:.2f}")

# Apply SMOTE to the training data
print("Applying SMOTE to professional training data...")
smote = SMOTE(random_state=42)

# Add print statements to check data types and missing values before SMOTE
print(f"Data type of X_train_pro_imputed before SMOTE: {X_train_pro_imputed.dtype}")
print(f"Number of missing values in X_train_pro_imputed before SMOTE: {np.isnan(X_train_pro_imputed).sum()}")
print(f"Data type of y_train_pro before SMOTE: {y_train_pro.dtype}")

# Explicitly convert X_train_pro_imputed to float type NumPy array
X_train_pro_imputed = X_train_pro_imputed.astype(float)
X_train_pro_resampled, y_train_pro_resampled = smote.fit_resample(X_train_pro_imputed, y_train_pro)
print(f"Original training set shape: {y_train_pro.shape[0]}")
print(f"Resampled training set shape: {y_train_pro_resampled.shape[0]}")

assert X_train_pro_resampled.shape[1] == len(all_cols), "Feature count mismatch in professional training data after SMOTE."

xgb_pro = xgb.XGBClassifier(eval_metric='logloss', random_state=42, scale_pos_weight=scale_pos_weight_pro)
grid_search_pro = GridSearchCV(estimator=xgb_pro, param_grid=param_grid_xgb_small, cv=3, scoring='roc_auc', n_jobs=-1, verbose=1)
grid_search_pro.fit(X_train_pro_resampled, y_train_pro_resampled)
best_model_professionals = grid_search_pro.best_estimator_


X_test_pro = pd.DataFrame(X_test_pro_imputed, columns=all_cols)
y_pred_pro = best_model_professionals.predict(X_test_pro)
y_pred_proba_pro = best_model_professionals.predict_proba(X_test_pro)[:, 1]

print("Best Professional Model Parameters:")
print(grid_search_pro.best_params_)
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

# Save the unified list of columns used for training
with open(os.path.join(models_dir, 'student_columns.json'), 'w') as f:
    json.dump(all_cols, f)
with open(os.path.join(models_dir, 'professional_columns.json'), 'w') as f:
    json.dump(all_cols, f)
print(f"Column lists saved successfully in '{models_dir}' directory.")