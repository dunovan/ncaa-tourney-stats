import requests
import pandas as pd
import os

def fetch_tournament_player_stats():
    api_key = os.environ.get("API_KEY")
    if not api_key:
        print("Error: API_KEY environment variable not found. Check your GitHub Secrets.")
        return

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    # Query parameters for the 2026 Postseason 
    params = {
        "year": 2026,
        "seasonType": "regular",
        "startDateRange": 2026-01-01,
        "endDateRange": 2026-03-01
    }
    
    # 1. Fetch game metadata to get the tournament round
    print("Fetching game schedules to determine tournament rounds...")
    games_url = "https://api.collegebasketballdata.com/games"
    games_response = requests.get(games_url, headers=headers, params=params)
    
    game_rounds = {}
    if games_response.status_code == 200:
        for game in games_response.json():
            # The API usually stores the round info in the 'notes' field for postseason games
            # We use 'or' to fallback to "Unknown Round" just in case the notes field is null
            game_rounds[game.get("id")] = game.get("notes") or "Unknown Round"

    # 2. Fetch the player stats
    print("Fetching player stats...")
    stats_url = "https://api.collegebasketballdata.com/games/players"
    stats_response = requests.get(stats_url, headers=headers, params=params)
    
    if stats_response.status_code != 200:
        print(f"Error {stats_response.status_code}: {stats_response.text}")
        return
        
    data = stats_response.json()
    
    if not data:
        print("No data returned. The 2026 postseason may not have started yet.")
        return

    # 3. Flatten the JSON and inject the Round
    flattened_data = []
    
    for game in data:
        game_id = game.get("id")
        
        # Pull the round from our dictionary mapping
        tournament_round = game_rounds.get(game_id, "Unknown Round")
        
        teams = game.get("teams", [])
        for team_info in teams:
            team_name = team_info.get("team")
            
            players = team_info.get("players", [])
            for player in players:
                
                row = {
                    "Game ID": game_id,
                    "Round": tournament_round, # <-- The new Round column
                    "Team": team_name,
                    "Player Name": player.get("name"),
                }
                
                stats = player.get("stats", player)
                if isinstance(stats, dict):
                    for stat_name, stat_val in stats.items():
                        if stat_name not in row:
                            row[stat_name] = stat_val
                            
                flattened_data.append(row)
                
    # 4. Convert to a Pandas DataFrame and export
    df = pd.DataFrame(flattened_data)
    output_filename = "NCAA_Tournament_2026_Player_Stats.csv"
    df.to_csv(output_filename, index=False)
    print(f"Success! Exported {len(df)} rows of player data to '{output_filename}'.")

if __name__ == "__main__":
    fetch_tournament_player_stats()
