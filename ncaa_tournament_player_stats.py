import requests
import pandas as pd
import os

def fetch_tournament_player_stats():
    api_key = os.environ.get("API_KEY")
    if not api_key:
        print("Error: API_KEY environment variable not found. Check your GitHub Secrets.")
        return

    url = "https://api.collegebasketballdata.com/games/players"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    # We use 'season' instead of 'year' based on the X-Ray, 
    # but include 'year' just to be universally safe with this API.
    params = {
        "season": 2026, 
        "year": 2026,
        "seasonType": "postseason",
        "tournament": "NCAA"
    }
    
    print("Fetching player stats from API...")
    
    try:
        # 30-second timeout to prevent GitHub Action hanging
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code != 200:
            print(f"Error {response.status_code}: {response.text}")
            return
            
        data = response.json()
        
        if not data:
            print("No data returned. The 2026 postseason has not been finalized in the database yet.")
            return

        # Flatten the JSON
        flattened_data = []
        
        for game in data:
            # Grab the top-level info based exactly on the X-Ray
            game_id = game.get("gameId")
            team_name = game.get("team")
            
            # Grab the round from either 'notes' or 'tournament'
            tournament_round = game.get("notes") or game.get("tournament") or "Unknown Round"
            
            # Go straight to the players array
            players = game.get("players", [])
            for player in players:
                
                row = {
                    "Game ID": game_id,
                    "Round": tournament_round,
                    "Team": team_name,
                    "Player Name": player.get("name"),
                }
                
                stats = player.get("stats", player)
                if isinstance(stats, dict):
                    for stat_name, stat_val in stats.items():
                        # Add stats to row (avoiding duplicating the name)
                        if stat_name not in row and stat_name != "name":
                            row[stat_name] = stat_val
                            
                flattened_data.append(row)
                
        # Convert to a Pandas DataFrame and export
        df = pd.DataFrame(flattened_data)
        output_filename = "NCAA_Tournament_2026_Player_Stats.csv"
        df.to_csv(output_filename, index=False)
        print(f"Success! Exported {len(df)} rows of player data to '{output_filename}'.")

    except requests.exceptions.Timeout:
        print("CRITICAL: The API request timed out. The provider's server is hanging.")
    except Exception as e:
        print(f"CRITICAL: An unexpected error occurred: {e}")

if __name__ == "__main__":
    fetch_tournament_player_stats()
