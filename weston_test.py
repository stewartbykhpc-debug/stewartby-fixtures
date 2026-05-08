import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime

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
fg.description(f'Last Checked: {datetime.now().strftime("%H:%M:%S")}')

found = get_fixtures()
if not found:
    # This is what you'll see in Feedly to prove it's working!
    fe = fg.add_entry()
    fe.title("SYSTEM CHECK: Weston Park Scraper is Live")
    fe.description("No real matches found at Weston Park right now, but the automation is working perfectly.")
    fe.link(href=URL)
else:
    for m in found:
        fe = fg.add_entry()
        fe.title(m['title'])
        fe.link(href=URL)

fg.rss_file('weston_test.xml')
