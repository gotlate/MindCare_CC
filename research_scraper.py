import json
import os
import requests
from bs4 import BeautifulSoup
import time

# --- Configuration ---
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
STUDENT_RESOURCES_PATH = os.path.join(DATA_DIR, 'student_resources.json')
PROFESSIONAL_RESOURCES_PATH = os.path.join(DATA_DIR, 'professional_resources.json')

# Search queries for Google Scholar
STUDENT_RESEARCH_QUERY = "mental health college students"
PROFESSIONAL_RESEARCH_QUERY = "workplace mental health burnout"

# --- Helper Functions ---
def load_resources(file_path):
    if not os.path.exists(file_path):
        return {"Support & Awareness Platforms": [], "Research & Studies": [], "Suggestions": []}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"Support & Awareness Platforms": [], "Research & Studies": [], "Suggestions": []}

def save_resources(file_path, resources):
    resources["Research & Studies"] = resources.get("Research & Studies", [])[:50] # Keep latest 50
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(resources, f, indent=4, ensure_ascii=False)

def scrape_google_scholar(query):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    # Using a search query that sorts by date
    url = f"https://scholar.google.com/scholar?q={query.replace(' ', '+')}&hl=en&as_sdt=0,5&scisbd=1"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        for result in soup.select('.gs_ri'):
            title_tag = result.select_one('.gs_rt a')
            description_tag = result.select_one('.gs_rs')
            
            if title_tag:
                title = title_tag.get_text(strip=True)
                link = title_tag['href']
                description = description_tag.get_text(strip=True) if description_tag else "No abstract available."
                
                results.append({
                    "title": title,
                    "description": description,
                    "url": link
                })
        return results
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Google Scholar for query '{query}': {e}")
        return []

def update_research_papers():
    print("Updating student research papers...")
    student_resources = load_resources(STUDENT_RESOURCES_PATH)
    student_research = scrape_google_scholar(STUDENT_RESEARCH_QUERY)
    
    if student_research:
        # Add new papers, preventing duplicates
        existing_urls = {paper['url'] for paper in student_resources.get("Research & Studies", [])}
        new_papers = [paper for paper in student_research if paper['url'] not in existing_urls]
        student_resources["Research & Studies"] = new_papers + student_resources.get("Research & Studies", [])
        save_resources(STUDENT_RESOURCES_PATH, student_resources)
        print(f"Added {len(new_papers)} new research papers for students.")
    
    time.sleep(5) # Delay between requests

    print("Updating professional research papers...")
    professional_resources = load_resources(PROFESSIONAL_RESOURCES_PATH)
    professional_research = scrape_google_scholar(PROFESSIONAL_RESEARCH_QUERY)
    
    if professional_research:
        existing_urls = {paper['url'] for paper in professional_resources.get("Research & Studies", [])}
        new_papers = [paper for paper in professional_research if paper['url'] not in existing_urls]
        professional_resources["Research & Studies"] = new_papers + professional_resources.get("Research & Studies", [])
        save_resources(PROFESSIONAL_RESOURCES_PATH, professional_resources)
        print(f"Added {len(new_papers)} new research papers for professionals.")

if __name__ == "__main__":
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    update_research_papers()
    print("Research scraper finished.")
