import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime

# Target URL
url = 'https://myrepublica.nagariknetwork.com/'

# Fetch the page
response = requests.get(url)
soup = BeautifulSoup(response.text, features='html.parser')

# Find all article links on the page
all_links = soup.find_all('a', href=True)
articles_url = []

# Filter links that point to news articles
for link in all_links:
    href = link.get('href', '')
    # Look for links that match the news article URL pattern
    if '/news/' in href and href not in articles_url:
        # Handle both relative and absolute URLs
        if not href.startswith('http'):
            href = 'https://myrepublica.nagariknetwork.com' + href
        articles_url.append(href)

# Limit to first 10 articles to avoid too many requests
articles_url = articles_url[:10]

if not articles_url:
    print("Error: Could not find any news articles. The website structure may have changed.")
    exit()
articles_data = []
for each_article_url in articles_url:
    article_response = requests.get(each_article_url)
    article_soup = BeautifulSoup(article_response.text, features='html.parser')

    # Try to find title - could be in h1 or other headers
    title_tag = article_soup.find('h1')
    title = title_tag.get_text(strip=True) if title_tag else 'No title found'

    # Extract content - look for paragraphs in the main article area
    content_paragraphs = article_soup.find_all('p')
    if content_paragraphs:
        # Filter out navigation and sidebar paragraphs by taking only the first substantial ones
        content = '\n'.join(p.get_text(strip=True) for p in content_paragraphs[:5] if p.get_text(strip=True) and len(p.get_text(strip=True)) > 20)
    else:
        content = 'No content found'

    articles_data.append({
        'title': title,
        'content': content,
        'url': each_article_url,
        'scraped_at': datetime.now().isoformat()
    })
print(articles_data)
# File name
file_name = 'Myrepublica_articles.json'
# Write to JSON file
with open(file_name, 'w', encoding='utf-8') as f:
    json.dump(articles_data, f, ensure_ascii=False, indent=4)
print(f"Data saved to {file_name}")
