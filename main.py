import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

# The "Master Key" URL that includes all Cups and Divisions
URL = "https://fulltime.thefa.com/fixtures.html?selectedFixtureGroupKey=all&selectedDateCode=all&selectedClubKey=&selectedTeamKey=&selectedNext6Weeks=false&league=1215610"
TARGET_VENUE = "Stewartby Sports Field"

def get_fixtures():
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    matches = []
    
    for row in soup.find_all('tr'):
        venue_cell = row.find('td', class_='venue')
        # This checks if the venue matches our village field
        if venue_cell and TARGET_VENUE.lower() in venue_cell.text.lower():
            home = row.find('td', class_='home-team').get_text(strip=True)
            away = row.find('td', class_='away-team').get_text(strip=True)
            dt_cell = row.find('td', class_='date-time')
            match_date = dt_cell.get_text(strip=True) if dt_cell else "TBC"
            
            matches.append({
                'title': f"{home} vs {away}",
                'description': f"Date: {match_date} | Venue: {TARGET_VENUE}"
            })
    return matches

fg = FeedGenerator()
fg.title('Stewartby Sports Field Fixtures')
fg.link(href=URL)
fg.description('Automated feed for all matches played at Stewartby')

found_matches = get_fixtures()
if not found_matches:
    fe = fg.add_entry()
    fe.title("No matches scheduled at Stewartby")
    fe.description("The scraper checked the FA site, but no games are currently listed for this venue.")
else:
    for match in found_matches:
        fe = fg.add_entry()
        fe.title(match['title'])
        fe.description(match['description'])

fg.rss_file('stewartby_fixtures.xml')
