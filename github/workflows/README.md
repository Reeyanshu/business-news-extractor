# Indian Business News Extractor

An automated tool that extracts and summarizes business, economy, and industry news relevant to Indian companies every 3 hours.

## Features

- Focuses strictly on business, economy, and industry news
- Filters out noise like stock price movements, recommendations, and non-business news
- Uses Google's Gemini AI to summarize the relevant articles
- Completely automated through GitHub Actions (runs every 3 hours)
- Maintains a history of all extracted news

## Setup Instructions

1. **Create a new GitHub repository**
   - Go to https://github.com/new
   - Name your repository (e.g., "business-news-extractor")
   - Choose "Public" (for free GitHub Actions minutes)
   - Click "Create repository"

2. **Add files to the repository**
   - Upload `news_extraction.py` (the main script)
   - Create `.github/workflows` directory and add `news_extraction.yml`
   - Add this README.md

3. **Set up the Google API key for Gemini**
   - Go to https://makersuite.google.com/app/apikey to get your API key
   - Then go to your repository's Settings
   - Click on "Secrets and variables" → "Actions"
   - Click "New repository secret"
   - Name: `GOOGLE_API_KEY`
   - Value: Your Google API key
   - Click "Add secret"

4. **Customize the script (optional)**
   - Edit the company keywords to match your interests
   - Edit the industry keywords to match your focus areas
   - Add or remove news sources as needed

5. **Trigger your first run**
   - Go to the "Actions" tab in your repository
   - Click on "Business News Extraction"
   - Click "Run workflow" to test it now (don't wait for the scheduled run)

## How It Works

1. Every 3 hours, GitHub Actions runs the Python script
2. The script fetches articles from business news sources
3. It filters out irrelevant or noisy content
4. It uses Google's Gemini AI to summarize the relevant articles
5. The results are saved to CSV files and committed to the repository
6. You can access the latest news at any time by viewing `business_news_summary.csv`

## Important Notes

- The Google Gemini API usage will incur costs based on the number of articles processed, but Google offers a generous free tier
- The script is designed to minimize API calls by pre-filtering articles
- The GitHub repository serves as both the execution environment and the data storage

## Customization

You can customize the following in the `news_extraction.py` file:

- `NEWS_SOURCES`: Add or remove news sources
- `COMPANY_KEYWORDS`: Add companies you're interested in
- `INDUSTRY_KEYWORDS`: Add industries you're tracking
- `ECONOMY_KEYWORDS`: Add economic indicators you care about
- `EXCLUSION_KEYWORDS`: Add keywords for content you want to exclude
