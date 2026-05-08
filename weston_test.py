import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

# URL for the Bedford & District Sunday League
URL = "https://fulltime.thefa.com/fixtures.html?league=1215610"
# Updated target for your test
TARGET_VENUE = "Weston Park Blue Cross Club"

def get_fixtures():
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    matches = []
    
    # Selecting rows - FA Full-Time uses 'tr' for matches
    for row in soup.find_all('tr'):
        venue_cell = row.find('td', class_='venue')
        if venue_cell and TARGET_VENUE.lower() in venue_cell.text.lower():
            home = row.find('td', class_='home-team').get_text(strip=True)
            away = row.find('td', class_='away-team').get_text(strip=True)
            dt_cell = row.find('td', class_='date-time')
            match_date = dt_cell.get_text(strip=True) if dt_cell else "TBC"
            
            matches.append({
                'title': f"TEST: {home} vs {away}",
                'description': f"Date: {match_date} | Venue: {venue_cell.text.strip()}"
            })
    return matches

fg = FeedGenerator()
fg.title('Weston Park TEST Feed')
fg.link(href=URL)
fg.description('Testing the scraper logic on Weston Park Blue Cross')

found_matches = get_fixtures()
if not found_matches:
    # If no matches, we add one dummy entry so you can see it in Feedly
    fe = fg.add_entry()
    fe.title("SYSTEM CHECK: No Weston Park games found today")
    fe.description("The scraper is working, but the FA site has no games listed for this venue.")
else:
    for match in found_matches:
        fe = fg.add_entry()
        fe.title(match['title'])
        fe.description(match['description'])

fg.rss_file('weston_test.xml')
print(f"Test feed created with {len(found_matches)} matches.")
