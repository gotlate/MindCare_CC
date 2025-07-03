import pandas as pd

df = pd.read_csv("final_depression_dataset_1.csv")

# Separate the dataset into students and professionals
students_df = df[df['Working Professional or Student'] == "Student"].copy()
professionals_df = df[df['Working Professional or Student'] == "Working Professional"].copy()

# Convert 'Depression' to numerical for correlation calculation
students_df['Depression_numeric'] = students_df['Depression'].apply(lambda x: 1 if x == 'Yes' else 0)
professionals_df['Depression_numeric'] = professionals_df['Depression'].apply(lambda x: 1 if x == 'Yes' else 0)

# Calculate Correlation for Students: CGPA vs Depression
# Drop rows where 'CGPA' is NaN before calculating correlation
students_df_cleaned_cgpa = students_df.dropna(subset=['CGPA'])
corr_stu_cgpa = students_df_cleaned_cgpa['CGPA'].corr(students_df_cleaned_cgpa['Depression_numeric'])
print(f"Correlation between CGPA and Depression (Students): {corr_stu_cgpa}")

# Calculate Correlation for Students: Work/Study Hours vs Depression
# Drop rows where 'Work/Study Hours' is NaN before calculating correlation
students_df_cleaned_work_hours = students_df.dropna(subset=['Work/Study Hours'])
corr_stu_work_hours = students_df_cleaned_work_hours['Work/Study Hours'].corr(students_df_cleaned_work_hours['Depression_numeric'])
print(f"Correlation between Work/Study Hours and Depression (Students): {corr_stu_work_hours}")

# Calculate Correlation for Professionals: Work/Study Hours vs Depression
# Drop rows where 'Work/Study Hours' is NaN before calculating correlation
professionals_df_cleaned_work_hours = professionals_df.dropna(subset=['Work/Study Hours'])
corr_pro_work_hours = professionals_df_cleaned_work_hours['Work/Study Hours'].corr(professionals_df_cleaned_work_hours['Depression_numeric'])
print(f"Correlation between Work/Study Hours and Depression (Professionals): {corr_pro_work_hours}")