import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime

# Target URL
url = 'https://thehimalayantimes.com/'

# Fetch the page
response = requests.get(url)
soup = BeautifulSoup(response.text, features='html.parser')
# Find all article links on the page
all_links = soup.find_all('a', href=True)
articles_url = []

# Filter links that point to news articles - look for category patterns
for link in all_links:
    href = link.get('href', '')
    # Look for links matching common category patterns (not the section navigation)
    # Exclude /morearticles/ and /category/ and other non-article pages
    if href and any(pattern in href for pattern in ['/kathmandu/', '/nepal/', '/world/', '/business/', '/sports/', '/entertainment/', '/opinion/', '/lifestyle/', '/science-and-tech/', '/health/', '/environment/']):
        if href not in articles_url and not href.endswith('/') and '/morearticles/' not in href and '/category/' not in href and '/archives' not in href:
            # Handle both relative and absolute URLs
            if not href.startswith('http'):
                href = 'https://thehimalayantimes.com' + href
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

    # Try to find title - look for h1 or h2 tags that contain actual article titles
    title_tag = article_soup.find('h1')
    if title_tag and title_tag.get_text(strip=True):
        title = title_tag.get_text(strip=True)
    else:
        # Try h2 as fallback
        title_tag = article_soup.find('h2')
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
file_name = 'Himalayantimes_articles.json'
# Write to JSON file
with open(file_name, 'w', encoding='utf-8') as f:
    json.dump(articles_data, f, ensure_ascii=False, indent=4)
print(f"Data saved to {file_name}")