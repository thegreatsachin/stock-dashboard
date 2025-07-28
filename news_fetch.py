import requests

def fetch_news(ticker: str, api_key: str):
    url = f"https://newsapi.org/v2/everything?q={ticker}&sortBy=publishedAt&language=en&apiKey={api_key}"
    response = requests.get(url)
    
    if response.status_code == 200:
        articles = response.json().get("articles", [])[:5]
        return articles
    else:
        return []
