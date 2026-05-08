import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timedelta

URL = "https://fulltime.thefa.com/fixtures.html?selectedFixtureGroupKey=all&selectedDateCode=all&selectedClubKey=&selectedTeamKey=&selectedNext6Weeks=false&league=1215610"
TARGET_VENUE = "Weston Park Blue Cross Club"
LOOKAHEAD_DAYS = 30

def get_fixtures():
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(URL, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        matches = []
        today = datetime.now()
        future_limit = today + timedelta(days=LOOKAHEAD_DAYS)

        # Look at every table row
        for row in soup.find_all('tr'):
            try:
                # 1. Safety Check: Does this row have a venue?
                venue_cell = row.find('td', class_='venue')
                if not venue_cell or TARGET_VENUE.lower() not in venue_cell.text.lower():
                    continue

                # 2. Date Check: Extract and parse
                date_cell = row.find('td', class_='date-time')
                if not date_cell:
                    continue

                date_text = date_cell.text.strip()
                # Attempt to parse: "Sun 18 May 26"
                parts = date_text.split()
                if len(parts) < 4: continue # Skip if date is weird like "TBC"
                
                clean_date = f"{parts[1]} {parts[2]} {parts[3]}" # "18 May 26"
                match_dt = datetime.strptime(clean_date, "%d %b %y")

                # 3. Filter: Only next 30 days
                if today <= match_dt <= future_limit:
                    home = row.find('td', class_='home-team').text.strip()
                    away = row.find('td', class_='away-team').text.strip()
                    matches.append({
                        'title': f"{match_dt.strftime('%d/%m')}: {home} v {away}",
                        'desc': f"Kickoff: {date_text} at {TARGET_VENUE}"
                    })
            except:
                continue # If one row is broken, just skip to the next!

        return matches
    except Exception as e:
        print(f"Global Error: {e}")
        return []

# --- RSS Generation ---
fg = FeedGenerator()
fg.title('Weston Park - Next 30 Days')
fg.link(href=URL)
fg.description(f'Last Scanned: {datetime.now().strftime("%d/%m %H:%M")}')

found = get_fixtures()
if not found:
    fe = fg.add_entry()
    fe.id('no-games-found')
    fe.title(f"No games at Weston Park until { (datetime.now() + timedelta(days=30)).strftime('%d %b') }")
    fe.description("The plumbing is working, but no matches matched the criteria.")
else:
    for i, m in enumerate(found):
        fe = fg.add_entry()
        fe.id(f"match-{i}-{datetime.now().day}") # Unique ID for Feedly
        fe.title(m['title'])
        fe.description(m['desc'])

fg.rss_file('weston_test.xml')
