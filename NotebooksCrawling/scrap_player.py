import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from scrap_commons import *


# Base URL for Transfermarkt
base_url = 'https://www.transfermarkt.com'

# Headers to mimic a browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'
}

def fetch_performance_data(team_links, base_url, headers, timeout=50):
    """
    Function to fetch performance data for players in each team.

    Parameters:
    team_links (list): List of tuples containing team names and URLs.
    base_url (str): The base URL of the website (e.g., 'https://www.transfermarkt.com').
    headers (dict): Headers to use for the requests (e.g., for User-Agent).

    Returns:
    list: A list of dictionaries containing player performance data.
    """
    def extract_player_id(profile_url):
        """Extract player ID from the profile URL."""
        match = re.search(r'/spieler/(\d+)', profile_url)
        return match.group(1) if match else None

    performance_data = []

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

                # Fetch the player performance page
                response = requests.get(player_profile_url, headers=headers, timeout=timeout)
                player_soup = BeautifulSoup(response.content, 'html.parser')

                # Locate the performance history table
                performance_table = player_soup.find('table', class_='items')

                if performance_table:
                    # Loop through each row of the performance table
                    for row in performance_table.find_all('tr', class_=['odd', 'even']):
                        cols = row.find_all('td')
                        if cols:
                            season = cols[0].text.strip()
                            competition = cols[1].text.strip()
                            matches_played = cols[2].text.strip()
                            goals = cols[3].text.strip()
                            assists = cols[4].text.strip()
                            minutes_played = cols[5].text.strip()

                            # Append the player's performance data
                            performance_data.append({
                                'Team': team_name,
                                'Player': player_name,
                                'Player ID': player_id,
                                'Season': season,
                                'Competition': competition,
                                'Matches Played': matches_played,
                                'Goals': goals,
                                'Assists': assists,
                                'Minutes Played': minutes_played
                            })
                else:
                    print(f"No performance data found for {player_name}.")

                # Be polite and pause to avoid overloading the server
                time.sleep(1)

        # Pause between teams
        time.sleep(2)

    return performance_data