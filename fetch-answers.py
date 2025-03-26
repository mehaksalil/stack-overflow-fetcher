import requests
import re
from bs4 import BeautifulSoup  # Import BeautifulSoup for HTML cleaning

def extract_question_id(url):
    """Extracts the question ID from a Stack Overflow question URL."""
    match = re.search(r"(\d+)", url)
    return match.group(1) if match else None

def clean_html(html_content):
    """Converts HTML content into readable text."""
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text()  # Extract readable text

def fetch_best_answer(question_url):
    """Fetches the highest-voted answer for a given question."""
    question_id = extract_question_id(question_url)
    
    if not question_id:
        print("❌ Invalid question URL. Please enter a valid Stack Overflow link.")
        return

    url = f"https://api.stackexchange.com/2.3/questions/{question_id}/answers?order=desc&sort=votes&site=stackoverflow&filter=withbody"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        answers = data.get("items", [])

        if not answers:
            print("No answers found for this question.")
            return

        best_answer = answers[0]
        cleaned_answer = clean_html(best_answer['body'])  # Clean the HTML

        print("\n✅ Best Answer:\n")
        print(cleaned_answer)

    else:
        print("❌ Error fetching answers:", response.status_code)

# Example usage
if __name__ == "__main__":
    question_link = input("Enter a Stack Overflow question link: ")
    fetch_best_answer(question_link)
