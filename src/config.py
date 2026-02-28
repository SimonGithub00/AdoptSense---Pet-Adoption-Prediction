from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Config:
    """Central project configuration with paths resolved from project root."""

    # Project root (one level above /src)
    ROOT_DIR: Path = Path(__file__).resolve().parents[1]

    # Data root
    DATA_DIR: Path = ROOT_DIR / "data"

    # Kaggle structure
    TRAIN_DIR: Path = DATA_DIR / "train"
    TEST_DIR: Path = DATA_DIR / "test"

    TRAIN_CSV: Path = TRAIN_DIR / "train.csv"
    TEST_CSV: Path = TEST_DIR / "test.csv"
    SAMPLE_SUBMISSION: Path = DATA_DIR / "sample_submission.csv"

    TRAIN_IMAGES_DIR: Path = TRAIN_DIR / "train_images"
    TEST_IMAGES_DIR: Path = TEST_DIR / "test_images"

    TRAIN_METADATA_DIR: Path = TRAIN_DIR / "train_metadata"
    TEST_METADATA_DIR: Path = TEST_DIR / "test_metadata"

    TRAIN_SENTIMENT_DIR: Path = TRAIN_DIR / "train_sentiment"
    TEST_SENTIMENT_DIR: Path = TEST_DIR / "test_sentiment"

    # Label tables
    BREED_LABELS: Path = DATA_DIR / "breed_labels.csv"
    COLOR_LABELS: Path = DATA_DIR / "color_labels.csv"
    STATE_LABELS: Path = DATA_DIR / "state_labels.csv"

    # Columns
    TARGET_COL: str = "AdoptionSpeed"
    ID_COL: str = "PetID"
    TEXT_COL: str = "Description"

    # Split/repro
    RANDOM_STATE: int = 42
    TEST_SIZE: float = 0.2