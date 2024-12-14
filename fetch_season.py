import pandas as pd
import os
import requests
import time
from bs4 import BeautifulSoup
from tqdm import tqdm


def fetch_season_stats(player_id, player_name):
    """
    Fetch season-based statistics for a player from Transfermarkt.

    Args:
        player_id (int): Player's Transfermarkt ID.
        player_name (str): Player's name for constructing the URL.

    Returns:
        pd.DataFrame: A dataframe containing season-based statistics.
    """
    # Format the player name to match the URL format
    player_slug = player_name.lower().replace(" ", "-")
    url = f"https://www.transfermarkt.com/{player_slug}/leistungsdatendetails/spieler/{player_id}/plus/0?saison=&verein=&liga=&wettbewerb=&pos=&trainer_id="

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Locate the table containing season stats
        stats_table = soup.find("table", {"class": "items"})
        if not stats_table:
            print(f"No statistics table found for {player_name} ({player_id}).")
            return pd.DataFrame()

        # Extract rows
        rows = stats_table.find_all("tr", {"class": ["odd", "even"]})

        # Collect data
        season_stats = []
        for row in rows:
            columns = row.find_all("td")
            # if len(columns) == 8:
            #     dbg = 1
            # if len(columns) == 9:
            #     dbg = 2
            # if len(columns) == 10:
            #     dbg = 3
            if len(columns) > 6:  # Ensure there are enough columns
                season_stats.append({
                    "Player": player_name,
                    "Player ID": player_id,
                    "Season": columns[0].text.strip(),
                    "Competition": columns[1].img['alt'] if columns[1].find("img") else columns[1].text.strip(),
                    "Club": columns[2].img['alt'] if columns[2].find("img") else columns[2].text.strip(),
                    "Appearances": columns[4].text.strip(),
                    "Minutes Played": columns[-1].text.strip()
                })
        return season_stats
        # # Convert to DataFrame
        # stats_df = pd.DataFrame(season_stats)
        # return stats_df

    except Exception as e:
        print(f"Error fetching data for {player_name} ({player_id}): {e}")
        return []


# Base URL for Transfermarkt
base_url = "https://www.transfermarkt.com"
headers = {"User-Agent": "Mozilla/5.0"}

# Load players pool dataset
unique_players = pd.read_csv('players_pool.csv')
unique_players = unique_players.drop_duplicates()

columns = ["Player", "Player ID", "Season", "Competition", "Appearances", "Club", "Minutes Played"]
all_market_data = []

for idx, row in tqdm(unique_players.iterrows(), total=len(unique_players), desc="Fetching Session Data"):
    player_name = row["Player"]
    player_id = row["Player ID"]
    stats = fetch_season_stats(player_id, player_name)
    for stat in stats:
        all_market_data.append(stat)
    # Be polite and pause to avoid overloading the server
    time.sleep(1)
    # Save DataFrame every 500 iterations
    if (idx + 1) % 50 == 0:
        temp_df = pd.DataFrame(all_market_data, columns=columns)
        temp_df.to_csv(f"output/df_season_stats.csv", index=False)

# New DataFrame to store detailed injury data
df_season_stats = pd.DataFrame(all_market_data, columns=columns)
df_season_stats.to_csv(f"df_season_stats.csv", index=False)