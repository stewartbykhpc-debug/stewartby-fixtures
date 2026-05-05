import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

URLS = ["https://fulltime.thefa.com/fixtures.html?league=1215610", "https://fulltime.thefa.com/fixtures.html?league=8441113"]
VENUE_TARGET = "Stewartby Sports Field"
FALLBACK_TEAMS = ["OB City", "AFC Clophill", "Stewartby", "United"]

def get_fixtures():
    headers = {'User-Agent': 'Mozilla/5.0'}
    matches = []
    for url in URLS:
        try:
            r = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(r.content, 'html.parser')
            for row in soup.find_all('tr', class_='fixture-row'):
                home = row.find('td', class_='home-team').get_text(strip=True) if row.find('td', class_='home-team') else "Unknown"
                away = row.find('td', class_='away-team').get_text(strip=True) if row.find('td', class_='away-team') else "Unknown"
                venue_text = row.find('td', class_='venue').get_text(strip=True) if row.find('td', class_='venue') else "TBC"
                include = False
                if VENUE_TARGET.lower() in venue_text.lower(): include = True
                elif "TBC" in venue_text.upper() and any(t.lower() in home.lower() for t in FALLBACK_TEAMS):
                    include = True
                    venue_text = f"TBC (Stewartby Fallback: {home})"
                if include:
                    matches.append({'title': f"{home} v {away}", 'desc': f"Venue: {venue_text}", 'link': url})
        except: continue
    return matches

fg = FeedGenerator()
fg.title('Stewartby Fixtures'); fg.link(href=URLS[0]); fg.description('Stewartby Tracker')
for m in get_fixtures():
    fe = fg.add_entry(); fe.title(m['title']); fe.description(m['desc']); fe.link(href=m['link'])
fg.rss_file('stewartby_fixtures.xml')
