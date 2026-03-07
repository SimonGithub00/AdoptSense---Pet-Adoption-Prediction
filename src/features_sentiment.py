import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Optional


# Fallback values used when a sentiment JSON is missing or malformed
_FALLBACK = {
    "sentiment_doc_score": 0.0,
    "sentiment_doc_magnitude": 0.0,
    "sentiment_avg_sentence_score": 0.0,
    "sentiment_avg_sentence_magnitude": 0.0,
    "sentiment_sentence_count": 0,
    "sentiment_pos_sentence_ratio": 0.0,
    "sentiment_neg_sentence_ratio": 0.0,
    "sentiment_entity_count": 0,
    "sentiment_max_entity_salience": 0.0,
    "sentiment_avg_entity_salience": 0.0,
}

SENTIMENT_FEATURE_COLS = list(_FALLBACK.keys())


def _parse_sentiment_json(path: Path) -> dict:
    """
    Parse a single Google NLP sentiment JSON file and return a flat feature dict.

    Extracted features:
        sentiment_doc_score            - Document-level sentiment score (-1 to +1).
        sentiment_doc_magnitude        - Document-level magnitude (0+, strength of emotion).
        sentiment_avg_sentence_score   - Mean per-sentence sentiment score.
        sentiment_avg_sentence_magnitude - Mean per-sentence sentiment magnitude.
        sentiment_sentence_count       - Number of sentences in the description.
        sentiment_pos_sentence_ratio   - Fraction of sentences with score > 0.
        sentiment_neg_sentence_ratio   - Fraction of sentences with score < 0.
        sentiment_entity_count         - Number of named entities detected.
        sentiment_max_entity_salience  - Salience of the most prominent entity.
        sentiment_avg_entity_salience  - Mean entity salience across all entities.
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # --- Document-level sentiment ---
    doc_sentiment = data.get("documentSentiment", {})
    doc_score = float(doc_sentiment.get("score", 0.0))
    doc_magnitude = float(doc_sentiment.get("magnitude", 0.0))

    # --- Sentence-level sentiment ---
    sentences = data.get("sentences", [])
    if sentences:
        scores = [s.get("sentiment", {}).get("score", 0.0) for s in sentences]
        magnitudes = [s.get("sentiment", {}).get("magnitude", 0.0) for s in sentences]
        avg_sentence_score = float(np.mean(scores))
        avg_sentence_magnitude = float(np.mean(magnitudes))
        sentence_count = len(sentences)
        pos_ratio = float(sum(1 for s in scores if s > 0) / sentence_count)
        neg_ratio = float(sum(1 for s in scores if s < 0) / sentence_count)
    else:
        avg_sentence_score = 0.0
        avg_sentence_magnitude = 0.0
        sentence_count = 0
        pos_ratio = 0.0
        neg_ratio = 0.0

    # --- Entity-level features ---
    entities = data.get("entities", [])
    if entities:
        saliences = [e.get("salience", 0.0) for e in entities]
        entity_count = len(entities)
        max_salience = float(max(saliences))
        avg_salience = float(np.mean(saliences))
    else:
        entity_count = 0
        max_salience = 0.0
        avg_salience = 0.0

    return {
        "sentiment_doc_score": doc_score,
        "sentiment_doc_magnitude": doc_magnitude,
        "sentiment_avg_sentence_score": avg_sentence_score,
        "sentiment_avg_sentence_magnitude": avg_sentence_magnitude,
        "sentiment_sentence_count": sentence_count,
        "sentiment_pos_sentence_ratio": pos_ratio,
        "sentiment_neg_sentence_ratio": neg_ratio,
        "sentiment_entity_count": entity_count,
        "sentiment_max_entity_salience": max_salience,
        "sentiment_avg_entity_salience": avg_salience,
    }


class SentimentFeatures:
    """
    Load pre-computed Google NLP sentiment JSON files and convert them into a
    flat numeric feature DataFrame, one row per PetID.

    Usage
    -----
    # For training data:
    sf = SentimentFeatures(cfg.TRAIN_SENTIMENT_DIR)
    sent_train = sf.load_for_ids(df_train["PetID"])

    # For test data:
    sf_test = SentimentFeatures(cfg.TEST_SENTIMENT_DIR)
    sent_test = sf_test.load_for_ids(df_test["PetID"])

    # Merge into main DataFrame:
    df_train = df_train.merge(sent_train, on="PetID", how="left")
    """

    def __init__(self, sentiment_dir: Path):
        """
        Parameters
        ----------
        sentiment_dir : Path
            Directory containing {PetID}.json files produced by Google NLP API.
        """
        self.sentiment_dir = Path(sentiment_dir)

    def load_for_ids(self, pet_ids: pd.Series) -> pd.DataFrame:
        """
        Parse sentiment JSON for each PetID and return a merged feature DataFrame.

        Missing or malformed JSON files are filled with zeros so downstream
        feature matrices are always complete.

        Parameters
        ----------
        pet_ids : pd.Series
            Series of PetID strings from train.csv or test.csv.

        Returns
        -------
        pd.DataFrame
            Columns: ["PetID"] + SENTIMENT_FEATURE_COLS
            One row per PetID (same order as input, no duplicates dropped).
        """
        rows = []
        for pet_id in pet_ids:
            path = self.sentiment_dir / f"{pet_id}.json"
            if path.exists():
                try:
                    features = _parse_sentiment_json(path)
                except (json.JSONDecodeError, KeyError, TypeError):
                    features = dict(_FALLBACK)
            else:
                features = dict(_FALLBACK)
            features["PetID"] = pet_id
            rows.append(features)

        df = pd.DataFrame(rows, columns=["PetID"] + SENTIMENT_FEATURE_COLS)
        return df

    def load_all(self) -> pd.DataFrame:
        """
        Parse every JSON file in the sentiment directory.

        Useful for computing coverage statistics or bulk loading without a CSV.

        Returns
        -------
        pd.DataFrame
            Columns: ["PetID"] + SENTIMENT_FEATURE_COLS
        """
        rows = []
        for json_path in sorted(self.sentiment_dir.glob("*.json")):
            pet_id = json_path.stem
            try:
                features = _parse_sentiment_json(json_path)
            except (json.JSONDecodeError, KeyError, TypeError):
                features = dict(_FALLBACK)
            features["PetID"] = pet_id
            rows.append(features)

        return pd.DataFrame(rows, columns=["PetID"] + SENTIMENT_FEATURE_COLS)

    def coverage(self, pet_ids: pd.Series) -> float:
        """
        Return the fraction of PetIDs that have a corresponding sentiment JSON.

        Parameters
        ----------
        pet_ids : pd.Series

        Returns
        -------
        float between 0.0 and 1.0
        """
        found = sum(
            1 for pid in pet_ids if (self.sentiment_dir / f"{pid}.json").exists()
        )
        return found / len(pet_ids) if len(pet_ids) > 0 else 0.0
