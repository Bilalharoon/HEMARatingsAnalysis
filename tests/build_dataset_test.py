from src.build_dataset import build_dataset
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RAW_DATA_DIR = BASE_DIR / "../data/raw"
FIGHTER_RATINGS_HISTORY_FILE = RAW_DATA_DIR / "fighter_ratings_history.csv"

