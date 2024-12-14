import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

# Base URL for Transfermarkt
base_url = 'https://www.transfermarkt.com'

# Headers to mimic a browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'
}


def get_team_links(league_name, league_code, season_year, timeout=10):
    """
    Function to get team links for a given league and season.

    Parameters:
    league_name (str): The name of the league formatted for the URL (e.g., 'premier-league').
    league_code (str): The Transfermarkt code for the league (e.g., 'GB1' for Premier League).
    season_year (str): The season year (e.g., '2023' for 2023/2024 season).

    Returns:
    list: A list of tuples containing team names and URLs.
    """
    # Construct the URL for the league's overview page
    league_url = f'{base_url}/{league_name}/startseite/wettbewerb/{league_code}/saison_id/{season_year}'

    # Request the league page
    response = requests.get(league_url, headers=headers, timeout=timeout)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all team links within the teams table
    teams_table = soup.find('table', class_='items')
    team_links = []
    for row in teams_table.find_all('tr', {'class': ['odd', 'even']}):
        team_tag = row.find('td', class_='hauptlink no-border-links').find('a')
        if team_tag:
            team_name = team_tag.text.strip()
            team_url = base_url + team_tag['href']
            team_links.append((team_name, team_url))
    return team_links
