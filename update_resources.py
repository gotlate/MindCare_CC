import json
import os
from datetime import datetime

data_dir = os.path.join(os.path.dirname(__file__), 'data')
student_resources_path = os.path.join(data_dir, 'student_resources.json')
professional_resources_path = os.path.join(data_dir, 'professional_resources.json')

def load_resources(file_path):
    if not os.path.exists(file_path):
        return {"Latest Articles": [], "Research & Studies": [], "Suggestions for Improving Mental Health": []}
    with open(file_path, 'r') as f:
        return json.load(f)

def save_resources(file_path, resources):
    with open(file_path, 'w') as f:
        json.dump(resources, f, indent=4)

def update_student_resources():
    resources = load_resources(student_resources_path)
    
    # Simulate fetching new student-related data
    current_week = datetime.now().strftime('%Y-%W') # Year-Week number
    new_article_title = f"New Student Article - Week {current_week}"
    new_research_title = f"New Student Research - Week {current_week}"

    new_articles = [
        {
            "title": new_article_title,
            "description": f"This is a simulated new article for students updated on {datetime.now().strftime('%Y-%m-%d')}.",
            "url": f"https://example.com/student-new-article-{current_week}"
        },
        {
            "title": "Stress Management for Online Learning",
            "description": "Tips for students adapting to virtual classrooms and managing stress.",
            "url": "https://example.com/student-online-learning-stress"
        }
    ]

    new_research = [
        {
            "title": new_research_title,
            "description": f"This is a simulated new research paper for students updated on {datetime.now().strftime('%Y-%m-%d')}.",
            "url": f"https://example.com/student-new-research-{current_week}"
        }
    ]

    # Add new entries if they don't already exist (based on title simplicity for this demo)
    # In a real scenario, you'd check for unique IDs or full URLs
    for article in new_articles:
        if not any(a['title'] == article['title'] for a in resources['Latest Articles']):
            resources['Latest Articles'].insert(0, article) # Add to top

    for research in new_research:
        if not any(r['title'] == research['title'] for r in resources['Research & Studies']):
            resources['Research & Studies'].insert(0, research) # Add to top

    save_resources(student_resources_path, resources)
    print(f"Student resources updated: {student_resources_path}")

def update_professional_resources():
    resources = load_resources(professional_resources_path)

    # Simulate fetching new professional-related data
    current_week = datetime.now().strftime('%Y-%W') # Year-Week number
    new_article_title = f"New Professional Article - Week {current_week}"
    new_suggestion_title = f"New Professional Suggestion - Week {current_week}"

    new_articles = [
        {
            "title": new_article_title,
            "description": f"This is a simulated new article for professionals updated on {datetime.now().strftime('%Y-%m-%d')}.",
            "url": f"https://example.com/prof-new-article-{current_week}"
        },
        {
            "title": "Burnout Prevention for Healthcare Workers",
            "description": "Strategies to combat professional burnout in demanding environments.",
            "url": "https://example.com/prof-healthcare-burnout"
        }
    ]

    new_suggestions = [
        {
            "title": new_suggestion_title,
            "description": f"This is a simulated new suggestion for professionals updated on {datetime.now().strftime('%Y-%m-%d')}.",
            "url": f"https://example.com/prof-new-suggestion-{current_week}"
        }
    ]

    for article in new_articles:
        if not any(a['title'] == article['title'] for a in resources['Latest Articles']):
            resources['Latest Articles'].insert(0, article) # Add to top

    for suggestion in new_suggestions:
        if not any(s['title'] == suggestion['title'] for s in resources['Suggestions for Improving Mental Health']):
            resources['Suggestions for Improving Mental Health'].insert(0, suggestion) # Add to top

    save_resources(professional_resources_path, resources)
    print(f"Professional resources updated: {professional_resources_path}")

if __name__ == "__main__":
    print("Running resource update script...")
    update_student_resources()
    update_professional_resources()
    print("Resource update complete.")
