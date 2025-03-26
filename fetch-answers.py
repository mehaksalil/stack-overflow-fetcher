import requests

def fetch_questions(query):
    url = f"https://api.stackexchange.com/2.3/search?order=desc&sort=votes&intitle={query}&site=stackoverflow"
    response = requests.get(url)

    print("\n🔹 Raw API Response:")
    print(response.text)  # Prints the raw JSON response for debugging

    if response.status_code == 200:
        data = response.json()
        questions = data.get("items", [])

        if not questions:
            print("No questions found. Try a different search term.")
            return

        print("\n🔍 Top Stack Overflow Questions:")
        for idx, q in enumerate(questions[:5], 1):
            print(f"{idx}. {q['title']} - {q['link']}")

    else:
        print("❌ Error fetching data:", response.status_code)

# Example usage
if __name__ == "__main__":
    user_query = input("Enter your search query: ")
    fetch_questions(user_query)
