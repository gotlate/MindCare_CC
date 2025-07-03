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
    # This function now expects resources["Research & Studies"] to be already sorted and deduplicated
    resources["Research & Studies"] = resources.get("Research & Studies", [])[:50] # Keep latest 50 after sorting
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(resources, f, indent=4, ensure_ascii=False)

def scrape_semantic_scholar(query):
    results = []
    try:
        params = {
            'query': query,
            'limit': 10,  # Number of results per page
            'fields': 'title,abstract,url,publicationDate',
            'sort': 'publicationDate:desc' # Sort by publication date, newest first
        }
        response = requests.get(SEMANTIC_SCHOLAR_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        if 'data' in data:
            for paper in data['data']:
                title = paper.get('title', 'No Title')
                description = paper.get('abstract') # Get abstract, will be None if not present
                url = paper.get('url', '#') # Default to '#' if url is missing
                publication_date = paper.get('publicationDate') # Get publication date

                # Only add paper if it has a description (abstract) AND a valid URL (not just '#')
                if description and description.strip() and url and url != '#':
                    results.append({
                        "title": title,
                        "description": description,
                        "url": url,
                        "publicationDate": publication_date # Store publication date
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
    time.sleep(60) # Increased delay to 1 minute
    student_resources = load_resources(STUDENT_RESOURCES_PATH)
    student_research = scrape_semantic_scholar(STUDENT_RESEARCH_QUERY)
    
    if student_research:
        all_student_papers = student_resources.get("Research & Studies", []) + student_research
        
        # Use a dictionary for deduplication, keeping the entry with the latest publication date
        unique_student_papers_dict = {}
        for paper in all_student_papers:
            url = paper.get('url')
            pub_date = paper.get('publicationDate')
            
            if url and pub_date: # Ensure URL and publicationDate exist
                if url not in unique_student_papers_dict or pub_date > unique_student_papers_dict[url].get('publicationDate', ''):
                    unique_student_papers_dict[url] = paper
        
        # Convert dictionary values back to a list and sort by publicationDate (descending)
        sorted_student_papers = sorted(list(unique_student_papers_dict.values()), 
                                      key=lambda x: x.get('publicationDate', ''), 
                                      reverse=True)
        student_resources["Research & Studies"] = sorted_student_papers
        save_resources(STUDENT_RESOURCES_PATH, student_resources)
        print(f"Updated student research papers. Total: {len(sorted_student_papers)}")
    
    time.sleep(60) # Increased delay to 1 minute

    print("Updating professional research papers...")
    professional_resources = load_resources(PROFESSIONAL_RESOURCES_PATH)
    professional_research = scrape_semantic_scholar(PROFESSIONAL_RESEARCH_QUERY)
    
    if professional_research:
        all_professional_papers = professional_resources.get("Research & Studies", []) + professional_research

        # Use a dictionary for deduplication, keeping the entry with the latest publication date
        unique_professional_papers_dict = {}
        for paper in all_professional_papers:
            url = paper.get('url')
            pub_date = paper.get('publicationDate')
            
            if url and pub_date: # Ensure URL and publicationDate exist
                if url not in unique_professional_papers_dict or pub_date > unique_professional_papers_dict[url].get('publicationDate', ''):
                    unique_professional_papers_dict[url] = paper

        # Convert dictionary values back to a list and sort by publicationDate (descending)
        sorted_professional_papers = sorted(list(unique_professional_papers_dict.values()), 
                                          key=lambda x: x.get('publicationDate', ''), 
                                          reverse=True)
        professional_resources["Research & Studies"] = sorted_professional_papers
        save_resources(PROFESSIONAL_RESOURCES_PATH, professional_resources)
        print(f"Updated professional research papers. Total: {len(sorted_professional_papers)}")

if __name__ == "__main__":
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    update_research_papers()
    print("Research scraper finished.")