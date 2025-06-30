import json
import os

# --- Configuration ---
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
STUDENT_RESOURCES_PATH = os.path.join(DATA_DIR, 'student_resources.json')
PROFESSIONAL_RESOURCES_PATH = os.path.join(DATA_DIR, 'professional_resources.json')

# --- Static Data ---
STATIC_ARTICLES_STUDENT = [
    {"title": "Mindfulness for Students", "url": "https://www.mindful.org/mindfulness-for-students/"},
    {"title": "The Jed Foundation", "url": "https://www.jedfoundation.org/"},
    {"title": "Active Minds", "url": "https://www.activeminds.org/"}
]

STATIC_ARTICLES_PROFESSIONAL = [
    {"title": "Harvard Business Review - Mental Health", "url": "https://hbr.org/topic/mental-health"},
    {"title": "Mental Health America - Workplace Wellness", "url": "https://www.mhanational.org/workplace-wellness"},
    {"title": "Forbes - Mental Health in the Workplace", "url": "https://www.forbes.com/mental-health-in-the-workplace/"}
]

SUGGESTIONS_STUDENT = [
    "Take regular study breaks.",
    "Prioritize getting 7-9 hours of sleep.",
    "Connect with a study group or club.",
    # ... Add many more suggestions here
] * 10 # Multiplying to get a larger pool

SUGGESTIONS_PROFESSIONAL = [
    "Set clear boundaries between work and personal life.",
    "Use your paid time off to fully disconnect.",
    "Practice mindfulness or meditation for a few minutes each day.",
    # ... Add many more suggestions here
] * 10

# --- Helper Functions ---
def load_resources(file_path):
    if not os.path.exists(file_path):
        return {"Latest Articles": [], "Research & Studies": [], "Suggestions": []}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"Latest Articles": [], "Research & Studies": [], "Suggestions": []}

def save_resources(file_path, resources):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(resources, f, indent=4, ensure_ascii=False)

def populate_files():
    # Student resources
    student_resources = load_resources(STUDENT_RESOURCES_PATH)
    student_resources["Latest Articles"] = STATIC_ARTICLES_STUDENT
    student_resources["Suggestions"] = SUGGESTIONS_STUDENT
    save_resources(STUDENT_RESOURCES_PATH, student_resources)
    print("Populated student resources with static articles and suggestions.")

    # Professional resources
    professional_resources = load_resources(PROFESSIONAL_RESOURCES_PATH)
    professional_resources["Latest Articles"] = STATIC_ARTICLES_PROFESSIONAL
    professional_resources["Suggestions"] = SUGGESTIONS_PROFESSIONAL
    save_resources(PROFESSIONAL_RESOURCES_PATH, professional_resources)
    print("Populated professional resources with static articles and suggestions.")

if __name__ == "__main__":
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    populate_files()
    print("Static resource population complete.")
