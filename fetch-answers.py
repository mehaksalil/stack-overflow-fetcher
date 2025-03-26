import requests
import json
import os
import time
import re
from bs4 import BeautifulSoup

CACHE_FILE = "cache.json"
CACHE_EXPIRY = 24 * 60 * 60  # 24 hours in seconds

def load_cache():
    """Loads cache from file or returns an empty dictionary if cache does not exist."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

cache=load_cache()

def save_cache(cache):
    """Saves the cache dictionary to a JSON file."""
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=4)

def extract_question_id(url):
    """Extracts the question ID from a Stack Overflow question URL."""
    match = re.search(r"(\d+)", url)
    return match.group(1) if match else None

def clean_html(html_content):
    """Converts HTML content into readable text and formats code snippets."""
    soup = BeautifulSoup(html_content, "html.parser")

    for code in soup.find_all("code"):
        code.string = f"\n📌 Code Snippet:\n{code.get_text()}\n"

    return soup.get_text()

def search_stackoverflow(query):
    """Searches Stack Overflow for relevant questions based on keywords."""
    print(f"🔎 Searching Stack Overflow for: {query}...")
    url = f"https://api.stackexchange.com/2.3/search?order=desc&sort=relevance&intitle={query}&site=stackoverflow"
    response = requests.get(url)

    if response.status_code == 200:
        questions = response.json().get("items", [])
        if not questions:
            print("❌ No matching questions found.")
            return None

        print("\n✅ Found these relevant questions:")
        for i, q in enumerate(questions[:5]):  # Show top 5 results
            print(f"{i+1}. {q['title']} (🔼 {q['score']} votes)")

        choice = int(input("\nEnter the number of the question you want answers for: ")) - 1
        if 0 <= choice < len(questions):
            return questions[choice]["link"]  # Return the URL of the selected question
        else:
            print("❌ Invalid selection. Please try again.")
            return None
    else:
        print("❌ Error fetching search results:", response.status_code)
        return None

def fetch_best_answers(question_link, num_answers=3):
    """Fetch top answers for a given Stack Overflow question, using cache if available."""
    question_id = extract_question_id(question_link)

    # Check cache first
    if question_id in cache:
        print("✅ Using cached data.")
        return cache[question_id]  # Return cached answers

    print("🌍 Fetching answers from Stack Overflow API...")
    
    url = f"https://api.stackexchange.com/2.3/questions/{question_id}/answers"
    params = {
        "order": "desc",
        "sort": "votes",
        "site": "stackoverflow",
        "filter": "!9_bDDxJY5"
    }

    response = requests.get(url, params=params)
    data = response.json()

    print("🔍 API Response:", data)  # This will help debug

    if "items" not in data or not data["items"]:
        print("⚠️ No answers found. API might have returned an empty response.")
        return []

    sorted_answers = sorted(
        data["items"], 
        key=lambda ans: (ans.get("is_accepted", False), ans["score"]), 
        reverse=True
    )

    best_answers = sorted_answers[:num_answers]

    # Save to cache before returning
    cache[question_id] = best_answers
    save_cache(cache)

    return best_answers


if __name__ == "__main__":
    search_query = input("Enter your Stack Overflow search query: ")
    question_link = search_stackoverflow(search_query)

    if question_link:
        num_answers = int(input("How many answers do you want to fetch? (default: 3): ") or 3)
        fetch_best_answers(question_link, num_answers)
def load_cache():
    """Loads cache from file or returns an empty dictionary if cache does not exist or is corrupted."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                data = f.read().strip()
                return json.loads(data) if data else {}  # If file is empty, return an empty dict
        except json.JSONDecodeError:
            print("⚠️ Cache file is corrupted. Resetting cache...")
            return {}
    return {}
def fetch_best_answers(question_link, num_answers=3):
    """Fetch the top answers for a given Stack Overflow question link."""
    question_id = extract_question_id(question_link)
    url = f"https://api.stackexchange.com/2.3/questions/{question_id}/answers"
    
    params = {
        "order": "desc",
        "sort": "votes",  # Sort answers by votes
        "site": "stackoverflow",
        "filter": "!9_bDDxJY5"  # Ensures we get full answer bodies
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "items" not in data or not data["items"]:
        print("No answers found.")
        return
    
    # Rank answers: Accepted ones come first, then highest voted
    sorted_answers = sorted(
        data["items"], 
        key=lambda ans: (ans.get("is_accepted", False), ans["score"]), 
        reverse=True
    )

    # Print or return the top `num_answers`
    for answer in sorted_answers[:num_answers]:
        print(f"Answer (Score: {answer['score']}, Accepted: {answer.get('is_accepted', False)})")
        print(answer["body"])  # or use BeautifulSoup to clean HTML
        print("-" * 50)
