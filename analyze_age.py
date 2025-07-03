import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("final_depression_dataset_1.csv")

students_df = df[df['Working Professional or Student'] == "Student"].copy()
professionals_df = df[df['Working Professional or Student'] == "Working Professional"].copy()

# Convert 'Depression' to numerical for correlation calculation
students_df['Depression_numeric'] = students_df['Depression'].apply(lambda x: 1 if x == 'Yes' else 0)
professionals_df['Depression_numeric'] = professionals_df['Depression'].apply(lambda x: 1 if x == 'Yes' else 0)

# Plot Age distribution for Students
plt.figure(figsize=(12, 6))
sns.histplot(data=students_df, x='Age', hue='Depression', kde=True, multiple='stack')
plt.title('Age Distribution for Students by Depression Status')
plt.xlabel('Age')
plt.ylabel('Count')
plt.savefig('student_age_distribution.png')
plt.clf()

# Plot Age distribution for Professionals
plt.figure(figsize=(12, 6))
sns.histplot(data=professionals_df, x='Age', hue='Depression', kde=True, multiple='stack')
plt.title('Age Distribution for Professionals by Depression Status')
plt.xlabel('Age')
plt.ylabel('Count')
plt.savefig('professional_age_distribution.png')
plt.clf()

# Calculate Correlation for Students
corr_stu = students_df['Age'].corr(students_df['Depression_numeric'])
print(f"Correlation between Age and Depression (Students): {corr_stu}")

# Calculate Correlation for Professionals
corr_pro = professionals_df['Age'].corr(professionals_df['Depression_numeric'])
print(f"Correlation between Age and Depression (Professionals): {corr_pro}")
