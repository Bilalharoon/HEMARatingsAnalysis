import pandas as pd
from src.fighter_state import FighterState
from datetime import datetime, timedelta
from pathlib import Path


# Config
BASE_DIR = Path(__file__).resolve().parent
RAW_DATA_DIR = BASE_DIR / "../data/raw"
PROCESSED_DATA_DIR = BASE_DIR / "../data/processed"

MATCHES_FILE = RAW_DATA_DIR / "tournament_histories.csv"
RATINGS_HISTORY_FILE = RAW_DATA_DIR / "fighter_ratings_history.csv"
OUTPUT_FILE = PROCESSED_DATA_DIR / "pre_match_features.csv"


def convert_date(date_str):
    return datetime.strptime(date_str.strip(), "%B %Y").date()


def build_dataset():
    fighter_states: dict[int, FighterState] = {}
    rows = []
    print("loading data...")
    matches = pd.read_csv(MATCHES_FILE)    
    ratings = pd.read_csv(RATINGS_HISTORY_FILE)
    print(matches.head())
    print(ratings.head())

    matches['tournament_date'] = matches['tournament_date'].apply(convert_date)
    matches = matches.sort_values(by='tournament_date').reset_index(drop=True)

    ratings['tournament_date'] = ratings['date'].apply(convert_date)
    ratings = ratings.sort_values(by='tournament_date').reset_index(drop=True)

    for _, match in matches.iterrows():
        fighter_id = int(match['fighter_id']) if not pd.isna(match['fighter_id']) else None
        opponent_id = int(match['opponent_id']) if not pd.isna(match['opponent_id']) else None
        match_date = match['tournament_date']


        for fid in (fighter_id, opponent_id):
            previous_ratings = ratings[(ratings['fighter_id'] == fid) & (ratings['tournament_date'] < match_date)]
            if not previous_ratings.empty:
                current_date = ratings['tournament_date'].iloc[-1]
                current_date = (current_date - timedelta(days=1)).replace(day=1)
                print(f'Reconstructing state for fighter {fid}...')
                rating = previous_ratings['rating'].iloc[-1]
                if fid not in fighter_states: 
                    fighter_states[fid] = FighterState(
                        fid,
                        float(rating),
                        match['tournament_date'],
                    )
                else:
                    fighter_states[fid].rating = float(rating)
                    fighter_states[fid].tournament_date = match['tournament_date']
                    fighter_states[fid].record_match(match['outcome'] == 'WIN' if fid == fighter_id else match['outcome'] != 'WIN', match_date)
            
            if fighter_id in fighter_states and opponent_id in fighter_states:
                a = fighter_states[fighter_id]
                b = fighter_states[opponent_id]

                rows.append({
                    'fighter_id': a.fighter_id,
                    'opponent_id': b.fighter_id,
                    'match_date': match_date,
                    'ratings_diff': a.rating - b.rating,
                    'experience_diff': a.matches_fought - b.matches_fought,
                    'days_since_last_fought_diff': (a.days_since_last_fight(current_date) - b.days_since_last_fight(current_date)).days if a.days_since_last_fight(current_date) is not None and b.days_since_last_fight(current_date) is not None else 999,
                    'division': match['division'],
                    'stage': match['stage'],
                    'label': 1 if match['outcome'] == 'WIN' else 0
                })

    
    
    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Dataset saved to {OUTPUT_FILE}")
    print(f'Number of rows: {len(df)}')

if __name__ == '__main__':
    build_dataset()

