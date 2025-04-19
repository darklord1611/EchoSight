import os
import re
from dotenv import load_dotenv
from newspaper import Article
import requests
import pyttsx3
from langchain_community.chat_models import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
import datetime
import json

load_dotenv()


class ArticleExample:
    def __init__(self, title, text, summary, url):
        self.title = title
        self.text = text
        self.summary = summary
        self.url = url

# ---- LLM SWITCHER ----
def get_llm(provider="openai"):
    if provider == "openai":
        return ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    elif provider == "gemini":
        return ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7, google_api_key=os.getenv("GOOGLE_API_KEY"))
    elif provider == "groq":
        return ChatGroq(model="llama3-8b-8192", groq_api_key=os.getenv("GROQ_API_KEY"))
    else:
        raise ValueError("Unsupported provider")


def refine_query(llm, original_query: str):
    prompt = f"""You are an expert search query refiner. Your task is to take a user's initial search query related to recent updates in a field and rewrite it into one more specific query that is highly likely to return links to an individual, informative article from a reputable source, rather than just index pages or general overviews.

Your refined query should incorporate strategies such as:

- Specifying the content type (e.g., "article," "news report").
- Emphasizing recency (e.g., "since April 2024," "in early 2025").
- Including keywords that suggest specific information and depth (e.g., "developments," "breakthroughs," "analysis").

You will receive the user's initial query, and you will output one refined search query.

Example:
User Query: Recent updates about AI
Refined Query: Recent news report on significant AI developments in early 2025.

Original query: "{original_query}"
"""
    result = llm.invoke(prompt)
    return result.content.strip()


# ---- SERPAPI SEARCH ----
def serpapi_search(query: str, num_results=5):
    params = {
        "q": query,
        "api_key": os.getenv("SERPAPI_API_KEY"),
        "engine": "google",
        "num": num_results
    }
    response = requests.get("https://serpapi.com/search", params=params)
    data = response.json()

    results = []
    if "organic_results" in data:
        for result in data["organic_results"][:num_results]:
            title = result.get("title")
            link = result.get("link")
            results.append((title, link))

    print("\n📄 SerpAPI Titles and URLs:\n")
    for title, url in results:
        print(f"📰 {title}\n🔗 {url}\n")

    return [url for _, url in results]


# ---- ARTICLE EXTRACTION ----
def extract_articles(urls):
    articles = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    for url in urls:
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            article = Article(url)
            article.set_html(response.text)
            article.download(input_html=response.text)
            article.parse()
            article.nlp()

            if article.text.strip():
                articles.append(ArticleExample(article.title, article.text[:2000], article.summary, url))
        except Exception as e:
            print(f"❌ Error extracting from {url}: {e}")
    return articles


# ---- SUMMARIZATION ----
def summarize_articles(llm, articles):
    if not articles:
        return "No valid articles to summarize."

    summaries = []
    for title, content, _ in articles:
        summary_prompt = f"📰 Title: {title}\n\n📖 Article:\n{content}\n\n✏️ Please provide a short summary."
        response = llm.invoke(summary_prompt)
        summaries.append(response.content.strip())

    return "\n\n".join(summaries)


# ---- TEXT TO SPEECH (optional) ----
def speak_text(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


# ---- PIPELINE ----
def execute_pipeline(user_query: str, provider="openai"):
    llm = get_llm(provider)

    print(f"🔍 Original Query:\n{user_query}\n")

    # Step 1: Refine Query
    # refined_query = refine_query(llm, user_query)
    # print(f"🎯 Refined Query:\n{refined_query}\n")

    refined_query = user_query + "news report articles"

    # Step 2: Search with SerpAPI
    urls = serpapi_search(refined_query)
    print(f"🔗 Extracted URLs:\n{urls}\n")


    # Step 3: Article Extraction
    articles = extract_articles(urls)
    print(f"📚 Retrieved {len(articles)} articles for summarization...\n")


    # # Step 5: TTS (optional)
    # # speak_text(summary)

    return articles


# ---- MAIN ----
if __name__ == "__main__":
    query = "Comparisons between OpenAI O3 and Gemini 2.0"
    execute_pipeline(query, provider="gemini")  # Options: "openai", "gemini", "groq"
