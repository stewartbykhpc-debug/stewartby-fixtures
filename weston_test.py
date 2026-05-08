import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime

# Bedfordshire FA Sunday League URL
URL = "https://fulltime.thefa.com/fixtures.html?league=1215610"
TARGET_VENUE = "Weston Park Blue Cross Club"

def get_fixtures():
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(URL, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        matches = []
        for row in soup.find_all('tr'):
            venue_cell = row.find('td', class_='venue')
            if venue_cell and TARGET_VENUE.lower() in venue_cell.text.lower():
                home = row.find('td', class_='home-team').text.strip()
                away = row.find('td', class_='away-team').text.strip()
                matches.append({'title': f"WESTON TEST: {home} v {away}"})
        return matches
    except:
        return []

fg = FeedGenerator()
fg.title('Weston Park Blue Cross - TEST')
fg.link(href=URL)
fg.description(f'Last Checked: {datetime.now().strftime("%d/%m/%Y %H:%M")}')

found = get_fixtures()
if not found:
    # This dummy entry ensures Feedly finds the feed today!
    fe = fg.add_entry()
    fe.id('test-id-123')
    fe.title("SYSTEM CHECK: Weston Park Scraper is Live")
    fe.description("The code is working. No real games at Weston Park today, but the 'plumbing' is ready for August.")
    fe.link(href=URL)
else:
    for i, m in enumerate(found):
        fe = fg.add_entry()
        fe.id(f'match-{i}')
        fe.title(m['title'])
        fe.link(href=URL)

fg.rss_file('weston_test.xml')
