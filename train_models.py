import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import confusion_matrix, precision_score, recall_score, roc_auc_score, precision_recall_curve,accuracy_score
import matplotlib.pyplot as plt
import pickle

# Load the dataset
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

# Define binary and non-binary columns for encoding
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

# Separate features and target variable for students and professionals
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
    'n_estimators': [10],  # Fewer trees for a quicker test
    'max_depth': [5],      # Smaller depth for faster results
    'min_samples_split': [2]
}
# Grid search with class weights for students
grid_search_stu = GridSearchCV(RandomForestClassifier(class_weight='balanced', random_state=42), param_grid, cv=5)
grid_search_stu.fit(X_train_students, y_train_students)
best_model_students = grid_search_stu.best_estimator_

# Save the columns used during training (in your training script)
#with open('stud_model.pkl', 'wb') as file:
 #   stud_data = {
  #      "model" : best_model_students,
   #     "features_list": X_students.columns.tolist()
    #}
    #pickle.dump(stud_data, file)

# Grid search with class weights for professionals
grid_search_pro = GridSearchCV(RandomForestClassifier(class_weight='balanced', random_state=42), param_grid, cv=5)
grid_search_pro.fit(X_train_pro, y_train_pro)
best_model_professionals = grid_search_pro.best_estimator_

#print("Best model: " ,  best_model_professionals)

# with open('prof_model.pkl', 'wb') as file:
#     pickle.dump({"model": best_model_professionals}, file)


#with open('prof_model.pkl', 'wb') as file:
 #   prof_data = {
  #      "model": best_model_professionals,
   #     "features_list":X_professionals.columns.tolist()  # Make sure this exists when saving
    #}
    #pickle.dump(prof_data, file)



# Predict probabilities for the test sets
y_prob_stu = best_model_students.predict_proba(X_test_students)[:, 1]  # Probability of "Yes"
y_prob_prof = best_model_professionals.predict_proba(X_test_pro)[:, 1]

# Convert probabilities to risk scores (1-10 scale)
risk_score_stu = y_prob_stu * 10
risk_score_prof = y_prob_prof * 10

# Plot the precision-recall curve for professionals to find the best threshold
precision_prof, recall_prof, thresholds_prof = precision_recall_curve(y_test_pro, y_prob_prof)
plt.plot(thresholds_prof, precision_prof[:-1], label="Precision")
plt.plot(thresholds_prof, recall_prof[:-1], label="Recall")
plt.xlabel("Threshold")
plt.ylabel("Score")
plt.legend()
plt.title("Precision-Recall Curve for Working Professionals")
plt.show()

precision_stu, recall_stu, thresholds_stu = precision_recall_curve(y_test_students, y_prob_stu)
plt.plot(thresholds_stu, precision_stu[:-1], label="Precision")
plt.plot(thresholds_stu, recall_stu[:-1], label="Recall")
plt.xlabel("Threshold")
plt.ylabel("Score")
plt.legend()
plt.title("Precision-Recall Curve for Students")
plt.show()

# Based on the plot, select an optimal threshold (adjust the value if needed)
optimal_threshold_prof = 0.6  # Example threshold; adjust based on the plot
optimal_threshold_stu = 0.5
# Convert probabilities to categorical "Yes/No" labels using the optimal threshold
y_pred_stu = (y_prob_stu >= optimal_threshold_stu).astype(int)
y_pred_prof = (y_prob_prof >= optimal_threshold_prof).astype(int)
#y_pred_stu = best_model_students.predict(X_test_students)
#y_pred_prof = best_model_professionals.predict(X_test_pro)

# Evaluate models using confusion matrix, precision, recall, and ROC AUC
conf_matrix_stu = confusion_matrix(y_test_students, y_pred_stu)
conf_matrix_prof = confusion_matrix(y_test_pro, y_pred_prof)
precision_stu = precision_score(y_test_students, y_pred_stu)
precision_prof = precision_score(y_test_pro, y_pred_prof)
recall_stu = recall_score(y_test_students, y_pred_stu)
recall_prof = recall_score(y_test_pro, y_pred_prof)
roc_auc_stu = roc_auc_score(y_test_students, y_prob_stu)
roc_auc_prof = roc_auc_score(y_test_pro, y_prob_prof)
accuracy_stu = accuracy_score(y_test_students, y_pred_stu)
accuracy_prof = accuracy_score(y_test_pro, y_pred_prof)

# Print results
print("Students Confusion Matrix:\n", conf_matrix_stu)
print("Students Precision:", precision_stu)
print("Students Recall:", recall_stu)
print("Students ROC AUC:", roc_auc_stu)

print("Professionals Confusion Matrix:\n", conf_matrix_prof)
print("Professionals Precision:", precision_prof)
print("Professionals Recall:", recall_prof)
print("Professionals ROC AUC:", roc_auc_prof)

print("Students Accuracy:", accuracy_stu)
print("Professionals Accuracy:", accuracy_prof)