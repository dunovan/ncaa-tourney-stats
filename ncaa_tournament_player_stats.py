import requests
import pandas as pd
import os

def fetch_tournament_player_stats():
    # 1. Setup the API request using environment variables
    # This securely pulls the API_KEY secret from GitHub Actions
    api_key = os.environ.get("API_KEY")
    
    if not api_key:
        print("Error: API_KEY environment variable not found. Check your GitHub Secrets.")
        return

    url = "https://api.collegebasketballdata.com/games/players"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    # Query parameters for the 2026 Postseason 
    params = {
        "year": 2026,
        "seasonType": "postseason" 
    }
    
    print("Fetching data from API...")
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code != 200:
        print(f"Error {response.status_code}: {response.text}")
        return
        
    data = response.json()
    
    if not data:
        print("No data returned. The 2026 postseason may not have started or the query is empty.")
        return

    # 2. Flatten the nested JSON response
    flattened_data = []
    
    for game in data:
        game_id = game.get("id")
        
        teams = game.get("teams", [])
        for team_info in teams:
            team_name = team_info.get("team")
            
            players = team_info.get("players", [])
            for player in players:
                
                row = {
                    "Game ID": game_id,
                    "Team": team_name,
                    "Player Name": player.get("name"),
                }
                
                stats = player.get("stats", player)
                if isinstance(stats, dict):
                    for stat_name, stat_val in stats.items():
                        if stat_name not in row:
                            row[stat_name] = stat_val
                            
                flattened_data.append(row)
                
    # 3. Convert to a Pandas DataFrame and export
    df = pd.DataFrame(flattened_data)
    output_filename = "NCAA_Tournament_2026_Player_Stats.csv"
    df.to_csv(output_filename, index=False)
    print(f"Success! Exported {len(df)} rows of player data to '{output_filename}'.")

if __name__ == "__main__":
    fetch_tournament_player_stats()