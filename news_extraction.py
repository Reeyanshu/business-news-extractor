import requests
import time
import json
import os
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import google.generativeai as genai

# Configure Google Gemini API
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# Define news sources focused on business/economy in India
NEWS_SOURCES = [
    {"name": "Economic Times", "url": "https://economictimes.indiatimes.com/markets/stocks/news", "selector": ".eachStory"},
    {"name": "Business Standard", "url": "https://www.business-standard.com/markets", "selector": ".article"},
    {"name": "Livemint", "url": "https://www.livemint.com/market", "selector": ".headline"},
    {"name": "Financial Express", "url": "https://www.financialexpress.com/market/", "selector": ".ie-story"}
]

# Company and industry keywords to filter for relevance
COMPANY_KEYWORDS = ["reliance", "tata", "infosys", "hdfc", "icici", "adani"]  # Add your companies
INDUSTRY_KEYWORDS = ["manufacturing", "it", "banking", "pharma", "telecom", "energy", "automobile"]  # Add your industries
ECONOMY_KEYWORDS = ["gdp", "inflation", "fiscal", "rbi", "monetary policy", "budget", "tax", "deficit"]

# Exclusion keywords for filtering out noise
EXCLUSION_KEYWORDS = ["stock price", "share price", "stocks to buy", "buy", "sell", "target price", 
                      "recommendation", "political", "election", "cricket", "bollywood", "movie"]

def fetch_news(source):
    """Fetch news from a single source"""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        response = requests.get(source["url"], headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        
        articles = []
        for article in soup.select(source["selector"]):
            # Extract headline, URL, and summary based on site structure
            # This is simplified and would need customization for each site
            headline_elem = article.find("h2") or article.find("h3")
            headline = headline_elem.text.strip() if headline_elem else ""
            
            link_elem = article.find("a")
            url = link_elem.get("href") if link_elem else ""
            if url and not url.startswith("http"):
                url = source["url"].split("/", 3)[0] + "//" + source["url"].split("/", 3)[2] + url
            
            summary_elem = article.find("p")
            summary = summary_elem.text.strip() if summary_elem else ""
            
            if headline and url:
                articles.append({
                    "source": source["name"],
                    "headline": headline,
                    "url": url,
                    "summary": summary,
                    "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
        
        return articles
    except Exception as e:
        print(f"Error fetching from {source['name']}: {e}")
        return []

def is_relevant(article):
    """Check if article is relevant to business/economy and not stock price/recommendations"""
    text = (article["headline"] + " " + article["summary"]).lower()
    
    # Check for exclusion keywords first
    if any(keyword in text for keyword in EXCLUSION_KEYWORDS):
        return False
    
    # Check if it contains any relevant keywords
    has_company = any(keyword in text for keyword in COMPANY_KEYWORDS)
    has_industry = any(keyword in text for keyword in INDUSTRY_KEYWORDS)
    has_economy = any(keyword in text for keyword in ECONOMY_KEYWORDS)
    
    return has_company or has_industry or has_economy

def summarize_with_gemini(articles):
    """Summarize articles using Google's Gemini API"""
    if not articles:
        return []
    
    # Set up the Gemini model
    model = genai.GenerativeModel('gemini-pro')
    
    summarized_articles = []
    for article in articles:
        try:
            prompt = f"""
            Summarize this business/economy news article in 2-3 sentences. 
            Focus ONLY on fundamental impacts to companies, industries, or the Indian economy.
            DO NOT include stock price movements or investment recommendations.
            
            Article from {article['source']}:
            Headline: {article['headline']}
            Text: {article['summary']}
            """
            
            response = model.generate_content(prompt)
            
            ai_summary = response.text.strip()
            article["ai_summary"] = ai_summary
            summarized_articles.append(article)
            
            # Avoid rate limiting
            time.sleep(1)
            
        except Exception as e:
            print(f"Error summarizing article: {e}")
            article["ai_summary"] = "Error generating summary."
            summarized_articles.append(article)
            
    return summarized_articles

def save_to_csv(articles, filename="business_news_summary.csv"):
    """Save articles to CSV file"""
    try:
        df = pd.DataFrame(articles)
        
        # If file exists, append without duplicating headlines
        if os.path.exists(filename):
            existing_df = pd.read_csv(filename)
            combined_df = pd.concat([existing_df, df])
            combined_df.drop_duplicates(subset=["headline"], keep="first", inplace=True)
            combined_df.to_csv(filename, index=False)
        else:
            df.to_csv(filename, index=False)
            
        print(f"Saved {len(articles)} articles to {filename}")
    except Exception as e:
        print(f"Error saving to CSV: {e}")

def main():
    all_articles = []
    
    # Fetch news from all sources
    for source in NEWS_SOURCES:
        print(f"Fetching news from {source['name']}...")
        articles = fetch_news(source)
        print(f"Found {len(articles)} articles")
        all_articles.extend(articles)
    
    # Filter for relevance
    print("Filtering for relevant business news...")
    relevant_articles = [article for article in all_articles if is_relevant(article)]
    print(f"Found {len(relevant_articles)} relevant articles out of {len(all_articles)}")
    
    # Summarize with Gemini
    print("Summarizing articles...")
    summarized_articles = summarize_with_gemini(relevant_articles)
    
    # Save results
    save_to_csv(summarized_articles)
    
    # Also create a timestamped file for archiving
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_to_csv(summarized_articles, f"business_news_{timestamp}.csv")
    
    print("News extraction and summarization completed.")

if __name__ == "__main__":
    main()
