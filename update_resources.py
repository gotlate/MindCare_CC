import json
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time # For delays between requests

# --- Configuration ---+
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
STUDENT_RESOURCES_PATH = os.path.join(DATA_DIR, 'student_resources.json')
PROFESSIONAL_RESOURCES_PATH = os.path.join(DATA_DIR, 'professional_resources.json')

# Define the websites to scrape and their properties
WEBSITES_TO_SCRAPE = [
    {
        "name": "The REACH Institute",
        "url": "https://thereachinstitute.org/mental-health-blog/",
        "primary_audience": "Both",
        "selectors": {
            "post": "article.post", # Adjust this based on actual site HTML
            "title": "h2.entry-title a",
            "link": "h2.entry-title a",
            "description": ".entry-content p",
            "tags": ".post-tags a" # Adjust for tag selector if exists
        },
        "student_keywords": ["college transition", "child mental health", "teen", "high-risk children & youth", "school"],
        "professional_keywords": ["pediatric primary care", "clinician", "coding", "patient-centered mental health", "provider"],
        "research_keywords": ["study", "evidence-based", "citation", "journal"],
        "suggestion_keywords": ["tips for", "how to", "actionable guidance", "strategies for"],
    },
    {
        "name": "NIMH Publications",
        "url": "https://www.nimh.nih.gov/health/publications", # Brochures & Fact Sheets
        "research_url": "https://www.nimh.nih.gov/research/research-areas/publications", # Research Publications
        "primary_audience": "Both", # Handled by different URLs
        "selectors": {
            "brochure_item": ".listing-card", # Adjust for brochure/fact sheet items
            "research_item": ".listing-card", # Adjust for research publication items
            "title": "h3 a",
            "link": "h3 a",
            "description": "p",
        },
        "student_keywords": ["teen", "youth", "school", "family"], # For brochures
        "professional_keywords": ["journal", "pmid", "doi", "clinician", "research", "scientific"], # For research
        "research_keywords": ["study", "doi", "gen hosp psychiatry", "journal", "pmid", "research", "findings"],
        "suggestion_keywords": ["fact sheet", "brochure", "guide", "tips"],
    },
    {
        "name": "APA Blogs",
        "url": "https://www.psychiatry.org/news-room/apa-blogs", # General blog list
        "primary_audience": "Both",
        "selectors": {
            "post": ".listing-item", # Adjust
            "title": "h3 a",
            "link": "h3 a",
            "description": "p.description",
            "tags": ".tag" # Placeholder
        },
        "student_keywords": ["college", "student", "academic success", "youth", "school"],
        "professional_keywords": ["clinician", "provider", "educator", "mental health professional", "psychiatry"],
        "research_keywords": ["survey", "study", "data from"],
        "suggestion_keywords": ["how to", "strategies for", "guide"],
    },
    {
        "name": "NAMI Blogs",
        "url": "https://www.nami.org/blogs/",
        "primary_audience": "Both",
        "selectors": {
            "post": ".blog-post-card", # Adjust
            "title": "h2 a",
            "link": "h2 a",
            "description": ".blog-excerpt p",
            "tags": ".category-tag" # Placeholder
        },
        "student_keywords": ["college", "teen anxiety", "school stigma", "youth"],
        "professional_keywords": ["frontline wellness", "ceo", "provider", "advocate"],
        "research_keywords": ["study", "data-driven", "research"],
        "suggestion_keywords": ["ways to cope", "strategies to", "tips", "how to"],
        "personal_story_keywords": ["i recovered", "my journey", "personal experience", "living with"], # Special category for NAMI
    },
    {
        "name": "Scanlan Center Blog",
        "url": "https://scsmh.education.uiowa.edu/resources/blog",
        "primary_audience": "Students & Educators", # Will lean towards student for final categorization
        "selectors": {
            "post": ".views-row", # Adjust
            "title": "h3.title a",
            "link": "h3.title a",
            "description": ".field-content p",
        },
        "student_keywords": ["k-12", "school staff", "teens", "students", "youth", "classroom"],
        "professional_keywords": ["educators", "school staff", "teacher"], # For the "educator" part
        "research_keywords": ["current research", "study summary"],
        "suggestion_keywords": ["strategies", "tools", "guidance", "support conversations", "tips"],
    },
]

# --- Helper Functions for Data Management ---
def load_resources(file_path):
    if not os.path.exists(file_path):
        return {"Latest Articles": [], "Research & Studies": [], "Suggestions for Improving Mental Health": []}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Warning: Could not decode JSON from {file_path}. Returning empty structure.")
        return {"Latest Articles": [], "Research & Studies": [], "Suggestions for Improving Mental Health": []}

def save_resources(file_path, resources):
    # Keep only the latest 50 entries per category to prevent files from growing indefinitely
    for category in resources:
        resources[category] = resources[category][:50]
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(resources, f, indent=4, ensure_ascii=False)

# --- Web Scraping Core Logic ---
def fetch_html(url, retries=3, delay=2):
    """Fetches HTML content from a given URL with retries and delays."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    for i in range(retries):
        try:
            print(f"Fetching: {url} (Attempt {i+1})")
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            if i < retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print(f"Failed to fetch {url} after {retries} attempts.")
                return None
    return None

def extract_data(soup, selectors):
    """Extracts data from a BeautifulSoup object using provided selectors."""
    items = []
    posts = soup.select(selectors["post"])
    for post in posts:
        title_tag = post.select_one(selectors["title"])
        description_tag = post.select_one(selectors.get("description"))
        
        title = title_tag.get_text(strip=True) if title_tag else "No Title"
        link = title_tag['href'] if title_tag and title_tag.has_attr('href') else "#"
        description = description_tag.get_text(strip=True) if description_tag else "No Description"

        # Ensure absolute URL
        if link and not link.startswith('http'):
            # This requires knowing the base URL of the source website for relative links
            # For simplicity, we'll assume most links are absolute or from the same domain
            # In a real scenario, you'd prepend the base URL
            pass 
        
        tags = [tag.get_text(strip=True) for tag in post.select(selectors.get("tags", []))]

        items.append({
            "title": title,
            "description": description,
            "url": link,
            "tags": tags # Include tags for categorization
        })
    return items

# --- Categorization Logic ---
def categorize_audience(item, website_config):
    text_content = (item['title'] + " " + item['description'] + " ".join(item['tags'])).lower()
    
    if website_config["primary_audience"] == "Student":
        return "Student"
    if website_config["primary_audience"] == "Professional":
        return "Professional"

    # If primary_audience is "Both" or general, use keywords
    for keyword in website_config.get("student_keywords", []):
        if keyword.lower() in text_content:
            return "Student"
    for keyword in website_config.get("professional_keywords", []):
        if keyword.lower() in text_content:
            return "Professional"
            
    # Default based on website's general lean, or to a general category if unsure
    if "college" in website_config["name"].lower() or "school" in website_config["name"].lower():
        return "Student"
    return "Professional" # Default if no specific keywords hit

def categorize_content_type(item, website_config):
    text_content = (item['title'] + " " + item['description']).lower()
    
    for keyword in website_config.get("research_keywords", []):
        if keyword.lower() in text_content:
            return "Research & Studies"
    
    for keyword in website_config.get("suggestion_keywords", []):
        if keyword.lower() in text_content:
            return "Suggestions for Improving Mental Health"

    if website_config["name"] == "NAMI Blogs":
        for keyword in website_config.get("personal_story_keywords", []):
            if keyword.lower() in text_content:
                return "Latest Articles" # Or create a "Personal Stories" category if desired

    return "Latest Articles" # Default


def scrape_and_update():
    student_data = load_resources(STUDENT_RESOURCES_PATH)
    professional_data = load_resources(PROFESSIONAL_RESOURCES_PATH)

    all_scraped_items = []

    for config in WEBSITES_TO_SCRAPE:
        print(f"Scraping from: {config['name']} ({config['url']})")
        html_content = fetch_html(config['url'])
        if html_content:
            soup = BeautifulSoup(html_content, 'html.parser')
            scraped_items = extract_data(soup, config['selectors'])
            
            # Special handling for NIMH's research URL
            if "research_url" in config:
                print(f"Scraping additional research from: {config['research_url']}")
                research_html_content = fetch_html(config['research_url'])
                if research_html_content:
                    research_soup = BeautifulSoup(research_html_content, 'html.parser')
                    scraped_items.extend(extract_data(research_soup, config['selectors'])) # Use same selectors for simplicity

            # Add source website to item and categorize
            for item in scraped_items:
                item['source'] = config['name']
                item['audience'] = categorize_audience(item, config)
                item['content_type'] = categorize_content_type(item, config)
                all_scraped_items.append(item)
        time.sleep(2) # Be polite and add a delay

    # Process and add to JSON files, preventing duplicates
    new_student_entries_count = 0
    new_professional_entries_count = 0

    for item in all_scraped_items:
        resource_entry = {
            "title": item['title'],
            "description": item['description'],
            "url": item['url'],
            # "source": item['source'] # Optional: add source if you want it in JSON
        }
        
        target_data = None
        if item['audience'] == "Student":
            target_data = student_data
        elif item['audience'] == "Professional":
            target_data = professional_data
        
        if target_data:
            category_list = target_data.get(item['content_type'], [])
            # Check for duplicates based on URL
            if not any(entry['url'] == resource_entry['url'] for entry in category_list):
                category_list.insert(0, resource_entry) # Add to the top of the list
                target_data[item['content_type']] = category_list
                if item['audience'] == "Student":
                    new_student_entries_count += 1
                else:
                    new_professional_entries_count += 1
            else:
                print(f"Skipping duplicate: {item['title']}")
        else:
            print(f"Warning: Could not categorize item: {item['title']}")

    save_resources(STUDENT_RESOURCES_PATH, student_data)
    save_resources(PROFESSIONAL_RESOURCES_PATH, professional_data)
    
    print(f"Finished scraping and updating. Added {new_student_entries_count} new student entries and {new_professional_entries_count} new professional entries.")

# --- Main Execution ---
if __name__ == "__main__":
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        # Initialize empty JSON files if they don't exist
        save_resources(STUDENT_RESOURCES_PATH, {"Latest Articles": [], "Research & Studies": [], "Suggestions for Improving Mental Health": []})
        save_resources(PROFESSIONAL_RESOURCES_PATH, {"Latest Articles": [], "Research & Studies": [], "Suggestions for Improving Mental Health": []})
        print("Created data directory and initialized empty JSON files.")

    scrape_and_update()