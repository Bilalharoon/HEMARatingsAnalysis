
import pandas as pd
from datetime import datetime
from pathlib import Path
import numpy as np

# Config
BASE_DIR = Path(".").resolve()
RAW_DATA_DIR = BASE_DIR / "data/raw"
MATCHES_FILE = RAW_DATA_DIR / "tournament_histories.csv"
RATINGS_HISTORY_FILE = RAW_DATA_DIR / "fighter_ratings_history.csv"

def convert_date(date_str):
    try:
        return datetime.strptime(date_str.strip(), "%B %Y").date()
    except:
        return None

print("Loading data...")
matches = pd.read_csv(MATCHES_FILE)
ratings = pd.read_csv(RATINGS_HISTORY_FILE)

matches['match_date'] = matches['tournament_date'].apply(convert_date)
ratings['rating_date'] = ratings['date'].apply(convert_date)

print(f"Total matches: {len(matches)}")
print(f"Total rating records: {len(ratings)}")



matches['fighter_id'] = matches['fighter_id'].astype('Int64')
matches['opponent_id'] = matches['opponent_id'].astype('Int64')
unique_fighters_in_matches = set(matches['fighter_id'].dropna().astype(str)) | set(matches['opponent_id'].dropna().astype(str))
unique_fighters_in_ratings = set(ratings['fighter_id'].dropna().astype(str))

print(f"Unique fighters in matches: {len(unique_fighters_in_matches)}")
print(f"Unique fighters in ratings: {len(unique_fighters_in_ratings)}")
print(f"Fighters in matches but missing from ratings history entirely: {len(unique_fighters_in_matches - unique_fighters_in_ratings)}")
print(f"Unique fighters in both matches and ratings: {len(unique_fighters_in_matches & unique_fighters_in_ratings)}")

print(list(unique_fighters_in_matches)[:10])
print(list(unique_fighters_in_ratings)[:10])
# Check date constraint validity
# For a sample of matches, check if ratings exist before
# This is slow to do fully, so let's do a simplified check
# Merge approach

# Get min rating date for each fighter
min_rating_dates = ratings.groupby('fighter_id')['rating_date'].min()
min_rating_dates.index = min_rating_dates.index.astype(str)

matches['fighter_id'] = matches['fighter_id'].astype(str)
matches['opponent_id'] = matches['opponent_id'].astype(str)

# Check how many matches have both fighters with a rating date < match_date
matches['f_min_date'] = matches['fighter_id'].map(min_rating_dates)
matches['o_min_date'] = matches['opponent_id'].map(min_rating_dates)

# Condition: min_date < match_date
valid_f = matches['f_min_date'] < matches['match_date']
valid_o = matches['o_min_date'] < matches['match_date']

valid_matches = matches[valid_f & valid_o]

print(f"Matches where both fighters have at least one rating strictly BEFORE the match date: {len(valid_matches)}")
print(f"Percentage retained: {len(valid_matches)/len(matches)*100:.2f}%")
