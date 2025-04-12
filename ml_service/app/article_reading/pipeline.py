import requests
from bs4 import BeautifulSoup
from newspaper import Article
import pyttsx3
from dotenv import load_dotenv
import os



load_dotenv()
# Replace with your own OpenAI key
from openai import OpenAI
from newspaper import Article
import re

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Step 1: Perform the web search using OpenAI's new Responses API
def fetch_web_search(query: str):

    search_prompt = (
        "Find up to 3 of the most recent and relevant news articles related to the topic: "
        f"'{query}'."
        "Only include trustworthy sources like major publishers (e.g., The Guardian, BBC, New York Times, etc). "
        "Return the article titles and direct URLs only. Do not provide summaries or commentary. "
    )

    response = client.responses.create(
        model="gpt-4o",
        tools=[{"type": "web_search_preview"}],
        input=search_prompt,
    )

    print("📄 Full Search Output:\n", response.output_text)

    # Optional: Extract URLs from the response text for downstream use
    urls = extract_urls(response.output_text)
    return urls, response.output_text

# Step 2: Basic URL extractor (regex-based)
def extract_urls(text):
    pattern = r"https?://[^\s)\]]+"
    return re.findall(pattern, text)

# Step 3: Extract article content from each URL

import requests
from newspaper import Article

def extract_articles(urls):
    articles = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    
    for url in urls:
        try:
            # Fetch the article content using requests with custom headers
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Will raise an HTTPError for bad responses
            
            # Use newspaper to parse the article text from the content retrieved by requests
            article = Article(url)
            article.set_html(response.text)
            article.parse()

            
            # Summarize the article
            article.nlp()

            # Append the title and truncated content
            if article.text.strip():
                articles.append((article.title, article.text, article.summary))  # Limit content to 5000 characters for token management
        except Exception as e:
            print(f"❌ Error extracting from {url}: {e}")
    
    return articles


# Step 4: Summarize extracted articles
def summarize_articles(articles):
    if not articles:
        return "No valid articles to summarize."

    summaries = []
    for title, content in articles:
        summary_prompt = f"📰 Title: {title}\n\n📖 Article:\n{content}\n\n✏️ Please provide a short summary."
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes news articles for blind users."},
                {"role": "user", "content": summary_prompt}
            ]
        )
        summaries.append(response.choices[0].message.content.strip())
    return "\n\n".join(summaries)


def execute_pipeline(query: str):
    # Step 1: Fetch web search results
    urls, search_output = fetch_web_search(query)
    print(f"\n🔗 Extracted URLs: {urls}\n")

    # Step 2: Extract articles from URLs
    articles = extract_articles(urls)
    print(f"\n📚 Retrieved {len(articles)} articles for summarization...\n")

    # Step 3: Summarize articles
    summary = summarize_articles(articles)
    print("\n✅ Summaries:\n")
    print(summary)

    return summary

# ---- MAIN WORKFLOW ----
if __name__ == "__main__":
    user_query = "🎙️ Voice Input (e.g., 'Read the latest AI news from The Guardian'):\n> "

    # urls, search_output = fetch_web_search(user_query)
    # print(f"\n🔗 Extracted URLs: {urls}\n")


    # urls = ['https://www.reuters.com/technology/artificial-intelligence/openai-rolls-out-assistant-like-feature-tasks-take-alexa-siri-2025-01-14/?utm_source=openai', 'https://www.reuters.com/technology/artificial-intelligence/google-brings-ai-voice-assistant-gemini-live-iphone-2024-11-14/?utm_source=openai', 'https://www.reuters.com/technology/artificial-intelligence/microsoft-revamps-ai-copilot-with-new-voice-reasoning-capabilities-2024-10-01/?utm_source=openai']

    urls = ["https://www.theguardian.com/technology/2025/apr/10/energy-demands-from-ai-datacentres-to-quadruple-by-2030-says-report/?utm_source=openai"]

    articles = extract_articles(urls)
    print(f"\n📚 Retrieved {len(articles)} articles for summarization...\n")

    print(articles)

    # summary = summarize_articles(articles)
    # print("\n✅ Summaries:\n")
    # print(summary)
