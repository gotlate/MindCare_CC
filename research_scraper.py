import json
import os
import requests
import time

# --- Configuration ---
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
STUDENT_RESOURCES_PATH = os.path.join(DATA_DIR, 'student_resources.json')
PROFESSIONAL_RESOURCES_PATH = os.path.join(DATA_DIR, 'professional_resources.json')

# Search queries for Semantic Scholar
STUDENT_RESEARCH_QUERY = "mental health college students"
PROFESSIONAL_RESEARCH_QUERY = "workplace mental health burnout"

# Semantic Scholar API Endpoint
SEMANTIC_SCHOLAR_API_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

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

def scrape_semantic_scholar(query):
    results = []
    try:
        params = {
            'query': query,
            'limit': 10,  # Number of results per page
            'fields': 'title,abstract,url'
        }
        response = requests.get(SEMANTIC_SCHOLAR_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        if 'data' in data:
            for paper in data['data']:
                title = paper.get('title', 'No Title')
                description = paper.get('abstract', 'No Abstract Available')
                url = paper.get('url', '#')

                results.append({
                    "title": title,
                    "description": description,
                    "url": url
                })
        else:
            print(f"No data found for query: {query}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching from Semantic Scholar for query '{query}': {e}")
    except KeyError as e:
        print(f"Error parsing Semantic Scholar response for query '{query}': Missing key {e}")
    return results


def update_research_papers():
    print("Updating student research papers...")
    time.sleep(5) # Add delay before the first API call
    student_resources = load_resources(STUDENT_RESOURCES_PATH)
    student_research = scrape_semantic_scholar(STUDENT_RESEARCH_QUERY)
    
    if student_research:
        # Add new papers, preventing duplicates
        existing_urls = {paper['url'] for paper in student_resources.get("Research & Studies", [])}
        new_papers = [paper for paper in student_research if paper['url'] not in existing_urls]
        student_resources["Research & Studies"] = new_papers + student_resources.get("Research & Studies", [])
        save_resources(STUDENT_RESOURCES_PATH, student_resources)
        print(f"Added {len(new_papers)} new research papers for students.")
    
    time.sleep(10) # Increased delay between requests

    print("Updating professional research papers...")
    professional_resources = load_resources(PROFESSIONAL_RESOURCES_PATH)
    professional_research = scrape_semantic_scholar(PROFESSIONAL_RESEARCH_QUERY)
    
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