from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Config:
    # Local data location (ignored by git)
    RAW_DIR: Path = Path("data/raw")

    # Kaggle structure
    TRAIN_DIR: Path = RAW_DIR / "train"
    TEST_DIR: Path = RAW_DIR / "test"

    TRAIN_CSV: Path = TRAIN_DIR / "train.csv"
    TEST_CSV: Path = TEST_DIR / "test.csv"
    SAMPLE_SUBMISSION: Path = RAW_DIR / "sample_submission.csv"

    TRAIN_IMAGES_DIR: Path = TRAIN_DIR / "train_images"
    TEST_IMAGES_DIR: Path = TEST_DIR / "test_images"

    TRAIN_METADATA_DIR: Path = TRAIN_DIR / "train_metadata"
    TEST_METADATA_DIR: Path = TEST_DIR / "test_metadata"

    TRAIN_SENTIMENT_DIR: Path = TRAIN_DIR / "train_sentiment"
    TEST_SENTIMENT_DIR: Path = TEST_DIR / "test_sentiment"

    # Label tables
    BREED_LABELS: Path = RAW_DIR / "breed_labels.csv"
    COLOR_LABELS: Path = RAW_DIR / "color_labels.csv"
    STATE_LABELS: Path = RAW_DIR / "state_labels.csv"

    # Columns
    TARGET_COL: str = "AdoptionSpeed"
    ID_COL: str = "PetID"
    TEXT_COL: str = "Description"

    # Split/repro
    RANDOM_STATE: int = 42
    TEST_SIZE: float = 0.2
