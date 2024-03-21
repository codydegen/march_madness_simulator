import json
import pandas as pd
from pathlib import Path

def load_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def load_csv(file_path):
    return pd.read_csv(file_path)

def save_json(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def main():
    current_dir = Path.cwd()  # Get the current working directory
    seeding_path = current_dir / "web_scraper"/ "mens2019" / "actual.json"
    teams_csv_path = current_dir / "team_data" / "2024_all_prepped_data.csv"
    output_path = current_dir / "web_scraper" / "mens2024" / "actual.json"

    seeding_data = load_json(seeding_path)
    teams_data = load_csv(teams_csv_path)

    # Create a dictionary mapping seeds and regions to team names from 2024 data
    team_mapping = {(row['team_region'], str(row['team_seed'])): row['team_name'] for _, row in teams_data.iterrows()}

    # Replace team names in 2019 bracket with team names from 2024 data
    for region, seeds in seeding_data.items():
        for seed, team_dict in seeds.items():
            team_name_2019 = list(team_dict.keys())[0]
            updated_team_name = team_mapping.get((region, seed), team_name_2019)
            seeding_data[region][seed] = {updated_team_name: team_dict[team_name_2019]}

    # Save the updated data to output_path
    save_json(seeding_data, output_path)

if __name__ == "__main__":
    main()
