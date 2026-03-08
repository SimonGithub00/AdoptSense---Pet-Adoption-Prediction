"""
Central project configuration for AdoptSense.

All filesystem paths are resolved relative to the project root so the
notebook and frontend work regardless of the working directory from which
they are invoked.  Import and instantiate once:

    from src.config import Config
    cfg = Config()
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:  # pylint: disable=invalid-name,too-many-instance-attributes
    """Immutable configuration container — all fields are resolved at import time."""

    # ------------------------------------------------------------------ #
    # Project layout                                                       #
    # ------------------------------------------------------------------ #

    # Project root: one level above /src
    ROOT_DIR: Path = Path(__file__).resolve().parents[1]

    # Top-level data directory
    DATA_DIR: Path = ROOT_DIR / "data"

    # ------------------------------------------------------------------ #
    # Kaggle dataset directories                                           #
    # ------------------------------------------------------------------ #

    TRAIN_DIR: Path = DATA_DIR / "train"
    TEST_DIR: Path = DATA_DIR / "test"

    # Raw CSV files
    TRAIN_CSV: Path = TRAIN_DIR / "train.csv"
    TEST_CSV: Path = TEST_DIR / "test.csv"          # no AdoptionSpeed labels — not used for eval
    SAMPLE_SUBMISSION: Path = DATA_DIR / "sample_submission.csv"

    # Pet images (not used in current tabular pipeline)
    TRAIN_IMAGES_DIR: Path = TRAIN_DIR / "train_images"
    TEST_IMAGES_DIR: Path = TEST_DIR / "test_images"

    # Image metadata JSON (not used in current tabular pipeline)
    TRAIN_METADATA_DIR: Path = TRAIN_DIR / "train_metadata"
    TEST_METADATA_DIR: Path = TEST_DIR / "test_metadata"

    # Google NLP sentiment JSON files — used for analytical comparison in notebook
    TRAIN_SENTIMENT_DIR: Path = TRAIN_DIR / "train_sentiment"
    TEST_SENTIMENT_DIR: Path = TEST_DIR / "test_sentiment"

    # ------------------------------------------------------------------ #
    # Label lookup tables                                                  #
    # ------------------------------------------------------------------ #

    BREED_LABELS: Path = DATA_DIR / "breed_labels.csv"
    COLOR_LABELS: Path = DATA_DIR / "color_labels.csv"
    STATE_LABELS: Path = DATA_DIR / "state_labels.csv"

    # ------------------------------------------------------------------ #
    # Column names                                                         #
    # ------------------------------------------------------------------ #

    TARGET_COL: str = "AdoptionSpeed"
    ID_COL: str = "PetID"
    TEXT_COL: str = "Description"

    # ------------------------------------------------------------------ #
    # Reproducibility and splitting                                        #
    # ------------------------------------------------------------------ #

    RANDOM_STATE: int = 42
    TEST_SIZE: float = 0.2     # fraction of labelled data held out for validation
