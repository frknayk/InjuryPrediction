import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from scrap_commons import *

# Dictionary mapping league names to their Transfermarkt codes and formatted names for URLs
leagues = {
    'Premier League': {'code': 'GB1', 'url_name': 'premier-league'},
    'Bundesliga': {'code': 'L1', 'url_name': 'bundesliga'},
    'Ligue 1': {'code': 'FR1', 'url_name': 'ligue-1'},
    'Serie A': {'code': 'IT1', 'url_name': 'serie-a'},
    'La Liga': {'code': 'ES1', 'url_name': 'laliga'},
    'Süper Lig': {'code': 'TR1', 'url_name': 'super-lig'}
}


def fetch_injury_data(team_links, base_url, headers, timeout=50):
    """
    Function to fetch injury data for players in each team.

    Parameters:
    team_links (list): List of tuples containing team names and URLs.
    base_url (str): The base URL of the website (e.g., 'https://www.transfermarkt.com').
    headers (dict): Headers to use for the requests (e.g., for User-Agent).

    Returns:
    list: A list of dictionaries containing player injury data.
    """
    # Function to extract player ID from the profile URL
    def extract_player_id(profile_url):
        """Function to extract player ID from the profile URL."""
        match = re.search(r'/spieler/(\d+)', profile_url)
        return match.group(1) if match else None
        
    injury_data = []
    
    # Loop over each team
    for team_name, team_url in team_links:
        print(f"Processing team: {team_name}")
        
        # Fetch the team squad page
        response = requests.get(team_url, headers=headers, timeout=timeout)
        team_soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all player rows
        for player_row in team_soup.select('tr.odd, tr.even'):
            # Extract player name and profile link
            name_tag = player_row.select_one('td.hauptlink a')
            if name_tag:
                player_name = name_tag.text.strip()
                player_profile_url = base_url + name_tag['href'].strip()
                
                # Extract player ID from profile URL
                player_id = extract_player_id(player_profile_url)
                
                # Extract player position
                position = player_row.find('td', class_='posrela').find_all('td')[-1].text.strip()
                
                # Extract birthdate and age
                birthdate = player_row.select('td.zentriert')[1].text.split('(')[0][:-1]
                age = int(player_row.select('td.zentriert')[1].text.split('(')[1].split(')')[0])
                # birthdate_age = player_row.select_one('td.zentriert').text.strip()
                
                # Extract nationality (handling multiple nationalities if present)
                nationality_imgs = player_row.select('td.zentriert img.flaggenrahmen')
                nationalities = [img['title'] for img in nationality_imgs]
                nationality = ", ".join(nationalities)
                
                # Extract market value
                market_value_tag = player_row.find('td', class_='rechts hauptlink')
                market_value = market_value_tag.text.strip() if market_value_tag else 'N/A'
                
                # Construct the injury page URL
                injury_url = player_profile_url.replace("profil", "verletzungen")
                
                # Fetch the injury page
                response = requests.get(injury_url, headers=headers, timeout=timeout)
                player_soup = BeautifulSoup(response.content, 'html.parser')
                
                # Locate the injury history table
                injury_table = player_soup.find('table', class_='items')
                
                if injury_table:
                    # Loop through each row of the injury table
                    for row in injury_table.find_all('tr', class_=['odd', 'even']):
                        cols = row.find_all('td')
                        if cols:
                            season = cols[0].text.strip()
                            injury_type = cols[1].text.strip()
                            start_date = cols[2].text.strip()
                            end_date = cols[3].text.strip()
                            days_out = cols[4].text.strip()
                            games_missed = cols[5].text.strip()
                            
                            # Append the player's injury data
                            injury_data.append({
                                'Team': team_name,
                                'Player': player_name,
                                'Player ID': player_id,
                                'Position': position,
                                'Birthdate': birthdate,
                                'Age': age,
                                'Nationality': nationality,
                                'Market Value': market_value,
                                'Season': season,
                                'Injury Type': injury_type,
                                'Start Date': start_date,
                                'End Date': end_date,
                                'Days Out': days_out,
                                'Games Missed': games_missed
                            })
                else:
                    # Append data if no injury history is found
                    injury_data.append({
                        'Team': team_name,
                        'Player': player_name,
                        'Player ID': player_id,
                        'Position': position,
                        'Birthdate': birthdate,
                        'Age': age,
                        'Nationality': nationality,
                        'Market Value': market_value,
                        'Season': 'N/A',
                        'Injury Type': 'N/A',
                        'Start Date': 'N/A',
                        'End Date': 'N/A',
                        'Days Out': 'N/A',
                        'Games Missed': 'N/A'
                    })

                # Be polite and pause to avoid overloading the server
                time.sleep(1)
        
        # Pause between teams
        time.sleep(2)

    return injury_data

def main():
    import requests
    from bs4 import BeautifulSoup
    import pandas as pd
    import time

    my_leagues = {'Premier League': {'code': 'GB1', 'url_name': 'premier-league'}}
    seasons = [2024]

    for season in seasons:
        for league in my_leagues:
            print("Reading league data: ", league)
            league_dict = my_leagues[league]
            team_links = get_team_links(
                league_name=league_dict['url_name'], 
                league_code=league_dict['code'], 
                season_year=season, 
                timeout=10)
            time.sleep(2)
            injury_data = fetch_injury_data(team_links, base_url, headers, timeout=100)
            df_injury_data = pd.DataFrame(injury_data)
            # df_injury_data.to_csv(f"player_injury_data_{league}_{season}.csv", index=False)

if __name__ == '__main__':
    main()