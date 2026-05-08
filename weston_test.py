import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timedelta

# 1. Config
URL = "https://fulltime.thefa.com/fixtures.html?league=1215610"
TARGET_VENUE = "Weston Park Blue Cross Club"
LOOKAHEAD_DAYS = 30

def get_fixtures():
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    matches = []
    today = datetime.now()
    future_limit = today + timedelta(days=LOOKAHEAD_DAYS)

    for row in soup.find_all('tr'):
        venue_cell = row.find('td', class_='venue')
        if venue_cell and TARGET_VENUE.lower() in venue_cell.text.lower():
            # Extract the date string
            date_cell = row.find('td', class_='date-time')
            if not date_cell: continue
            
            date_text = date_cell.text.strip() # Usually looks like "Sun 10 May 26 10:30"
            
            try:
                # We try to turn the FA text into a real date the computer understands
                # Removing the day name (Sun/Mon) to make it easier to parse
                clean_date = " ".join(date_text.split()[1:4]) # "10 May 26"
                match_dt = datetime.strptime(clean_date, "%d %b %y")
                
                # Check if it's between now and next month
                if today <= match_dt <= future_limit:
                    home = row.find('td', class_='home-team').text.strip()
                    away = row.find('td', class_='away-team').text.strip()
                    matches.append({
                        'title': f"{match_dt.strftime('%d/%m')}: {home} v {away}",
                        'desc': f"Kickoff: {date_text}"
                    })
            except Exception as e:
                # If the FA format changes slightly, we still grab it just in case
                print(f"Skipping row: {e}")

    return matches

# RSS Generation
fg = FeedGenerator()
fg.title('Weston Park - Next 30 Days')
fg.link(href=URL)
fg.description(f'Updated {datetime.now().strftime("%d/%m %H:%M")}')

found = get_fixtures()
if not found:
    fe = fg.add_entry()
    fe.id('no-games')
    fe.title(f"No games at Weston Park for the next {LOOKAHEAD_DAYS} days")
    fe.description("The scraper is working, but the schedule is clear.")
else:
    for m in found:
        fe = fg.add_entry()
        fe.id(m['title'])
        fe.title(m['title'])
        fe.description(m['desc'])

fg.rss_file('weston_test.xml')
