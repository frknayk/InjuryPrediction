import pandas as pd
import os
import requests
import time
from bs4 import BeautifulSoup
from tqdm import tqdm
import os





def fetch_injury_data(player_name, player_id, base_url, headers, timeout=50):
    """
    Fetches detailed injury data from Transfermarkt for a specific player.

    Parameters:
    player_name (str): The Player name.
    player_id (int): The Player ID from the dataset.
    base_url (str): Base URL of Transfermarkt.
    headers (dict): Headers to use for the requests.
    timeout (int): Timeout for the requests.

    Returns:
    list: A list of dictionaries containing the injury history.
    """
    player_name_url = player_name.replace(" ", "-").lower()
    player_url = f"{base_url}/{player_name_url}/verletzungen/spieler/{player_id}"
    
    response = requests.get(player_url, headers=headers, timeout=timeout)
    if response.status_code != 200:
        print(f"Failed to fetch data for Player {player_name} (ID: {player_id}). HTTP Status: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    injury_table = soup.find('table', class_='items')

    if not injury_table:
        print(f"No injury table found for Player {player_name} (ID: {player_id}).")
        return []

    injuries = []
    rows = injury_table.find('tbody').find_all('tr')
    for row in rows:
        columns = row.find_all('td')
        if len(columns) < 6:
            continue

        season = columns[0].text.strip()
        injury_type = columns[1].text.strip()
        from_date = columns[2].text.strip()
        until_date = columns[3].text.strip()
        days_out = columns[4].text.strip()
        games_missed = columns[5].text.strip()

        # Extract club name from the "Games missed" column
        club_tag = columns[5].find('a')
        club = club_tag['title'] if club_tag else 'Unknown'

        injuries.append({
            'Season': season,
            'Injury': injury_type,
            'From': from_date,
            'Until': until_date,
            'Days Out': days_out,
            'Games Missed': games_missed,
            'Club': club
        })

    return injuries

if __name__ == '__main__':
    # Create directory to save intermediate results
    os.makedirs("output", exist_ok=True)

    # Load the merged dataset
    data_folder = "Data"
    merged_df_path = f"{data_folder}/merged_player_injury_data.csv"
    merged_df = pd.read_csv(merged_df_path)

    # Base URL for Transfermarkt
    base_url = "https://www.transfermarkt.com"
    headers = {"User-Agent": "Mozilla/5.0"}

    # Fix the merged dataset
    unique_players = merged_df[['Player', 'Player ID']].drop_duplicates()


    columns = ["Player", "Player ID", "Season", "Injury", "From", "Until", "Days Out", "Games Missed", "Club"]
    all_rows = []

    for idx, row in tqdm(unique_players.iterrows(), total=len(unique_players), desc="Processing Players"):
        player_name = row['Player']
        player_id = row['Player ID']
        # print(f"Processing Player: {player_name} (ID: {player_id})")
        injuries = fetch_injury_data(player_name, player_id, base_url, headers, timeout=50)
        if injuries:
            # Append each injury as a new row in the DataFrame
            for injury in injuries:
                all_rows.append({
                "Player": player_name,
                "Player ID": player_id,
                "Season": injury["Season"],
                "Injury": injury["Injury"],
                "From": injury["From"],
                "Until": injury["Until"],
                "Days Out": injury["Days Out"],
                "Games Missed": injury["Games Missed"],
                "Club": injury["Club"],
            })
            # Be polite and pause to avoid overloading the server
            time.sleep(1)
        # Save DataFrame every 500 iterations
        if (idx + 1) % 500 == 0:
            temp_df = pd.DataFrame(all_rows, columns=columns)
            temp_df.to_csv(f"output/df_injuries.csv", index=False)

    # New DataFrame to store detailed injury data
    df_injuries = pd.DataFrame(all_rows, columns=columns)
    df_injuries.to_csv(f"df_injuries.csv", index=False)