import requests
import re
import json
import os
import time
from bs4 import BeautifulSoup

CACHE_FILE = "cache.json"
CACHE_EXPIRY = 24 * 60 * 60  # 24 hours in seconds

def load_cache():
    """Loads cache from file, or returns an empty dictionary if cache does not exist."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

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

    # Format <code> blocks separately
    for code in soup.find_all("code"):
        code.string = f"\n📌 Code Snippet:\n{code.get_text()}\n"

    return soup.get_text()  # Extract readable text

def fetch_best_answers(question_url, num_answers=3):
    """Fetches multiple highly upvoted answers, using caching for faster performance."""
    question_id = extract_question_id(question_url)
    
    if not question_id:
        print("❌ Invalid question URL. Please enter a valid Stack Overflow link.")
        return

    cache = load_cache()
    
    # Check if question exists in cache and is not expired
    if question_id in cache and time.time() - cache[question_id]["timestamp"] < CACHE_EXPIRY:
        print("🔄 Loading cached answers...\n")
        answers = cache[question_id]["answers"]
    else:
        print("🌐 Fetching new answers from Stack Overflow...\n")
        url = f"https://api.stackexchange.com/2.3/questions/{question_id}/answers?order=desc&sort=votes&site=stackoverflow&filter=withbody"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            answers = data.get("items", [])

            if not answers:
                print("❌ No answers found for this question.")
                return

            # Save fetched data to cache
            cache[question_id] = {
                "timestamp": time.time(),
                "answers": answers
            }
            save_cache(cache)
        else:
            print("❌ Error fetching answers:", response.status_code)
            return

    print("\n" + "=" * 50)
    print(f"✅ Top {min(num_answers, len(answers))} Answers:\n")

    for i, answer in enumerate(answers[:num_answers]):
        cleaned_answer = clean_html(answer['body'])
        print(f"🔹 **Answer {i+1} (Votes: {answer['score']})**\n")
        print(cleaned_answer)
        print("-" * 50 + "\n")

    print("=" * 50 + "\n")

# Example usage
if __name__ == "__main__":
    question_link = input("Enter a Stack Overflow question link: ")
    num_answers = int(input("How many answers do you want to fetch? (default: 3): ") or 3)
    fetch_best_answers(question_link, num_answers)
