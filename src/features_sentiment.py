"""
Google NLP sentiment feature engineering for AdoptSense.

Parses pre-computed Google Cloud Natural Language API JSON files (one per
pet listing) into a flat numeric feature DataFrame.  These features are used
for analytical comparison in the notebook (Sections 3.4 and 3.5) but are
**not** included in the deployed pipeline, which uses VADER instead.

Typical usage
-------------
    from src.features_sentiment import SentimentFeatures, SENTIMENT_FEATURE_COLS

    sf = SentimentFeatures(cfg.TRAIN_SENTIMENT_DIR)
    sent_df = sf.load_for_ids(df["PetID"])
    df = df.merge(sent_df, on="PetID", how="left")
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd


# Fallback values used when a sentiment JSON is missing or malformed.
# Zero represents a neutral/absent signal, consistent with how 3.7% of
# training pets (those with empty descriptions) were handled at training time.
_FALLBACK: dict = {
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

SENTIMENT_FEATURE_COLS: list = list(_FALLBACK.keys())


def _parse_sentiment_json(path: Path) -> dict:  # pylint: disable=too-many-locals
    """Parse a single Google NLP sentiment JSON file into a flat feature dict.

    Parameters
    ----------
    path:
        Absolute path to a ``{PetID}.json`` file produced by the
        Google Cloud Natural Language API.

    Returns
    -------
    dict
        Keys match :data:`SENTIMENT_FEATURE_COLS`.  Extracted features:

        - ``sentiment_doc_score`` — document-level sentiment score (-1 to +1).
        - ``sentiment_doc_magnitude`` — document-level magnitude (0+, emotional strength).
        - ``sentiment_avg_sentence_score`` — mean per-sentence sentiment score.
        - ``sentiment_avg_sentence_magnitude`` — mean per-sentence sentiment magnitude.
        - ``sentiment_sentence_count`` — number of sentences in the description.
        - ``sentiment_pos_sentence_ratio`` — fraction of sentences with score > 0.
        - ``sentiment_neg_sentence_ratio`` — fraction of sentences with score < 0.
        - ``sentiment_entity_count`` — number of named entities detected.
        - ``sentiment_max_entity_salience`` — salience of the most prominent entity.
        - ``sentiment_avg_entity_salience`` — mean entity salience across all entities.
    """
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    # Document-level sentiment
    doc_sentiment = data.get("documentSentiment", {})
    doc_score = float(doc_sentiment.get("score", 0.0))
    doc_magnitude = float(doc_sentiment.get("magnitude", 0.0))

    # Sentence-level sentiment
    sentences = data.get("sentences", [])
    if sentences:
        scores = [s.get("sentiment", {}).get("score", 0.0) for s in sentences]
        magnitudes = [s.get("sentiment", {}).get("magnitude", 0.0) for s in sentences]
        n = len(sentences)
        avg_sentence_score = float(np.mean(scores))
        avg_sentence_magnitude = float(np.mean(magnitudes))
        sentence_count = n
        pos_ratio = float(sum(1 for s in scores if s > 0) / n)
        neg_ratio = float(sum(1 for s in scores if s < 0) / n)
    else:
        avg_sentence_score = 0.0
        avg_sentence_magnitude = 0.0
        sentence_count = 0
        pos_ratio = 0.0
        neg_ratio = 0.0

    # Entity-level features
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
    """Load pre-computed Google NLP sentiment JSON files into a feature DataFrame.

    One row is produced per PetID.  Missing or malformed JSON files are
    silently zero-filled so downstream feature matrices are always complete.

    Parameters
    ----------
    sentiment_dir:
        Directory containing ``{PetID}.json`` files produced by the
        Google Cloud Natural Language API.

    Examples
    --------
    Training data::

        sf = SentimentFeatures(cfg.TRAIN_SENTIMENT_DIR)
        sent_train = sf.load_for_ids(df_train["PetID"])
        df_train = df_train.merge(sent_train, on="PetID", how="left")
    """

    def __init__(self, sentiment_dir: Path) -> None:
        self.sentiment_dir = Path(sentiment_dir)

    def __repr__(self) -> str:
        return f"SentimentFeatures(sentiment_dir={self.sentiment_dir!r})"

    def load_for_ids(self, pet_ids: pd.Series) -> pd.DataFrame:
        """Parse sentiment JSON for each PetID and return a feature DataFrame.

        Parameters
        ----------
        pet_ids:
            Series of PetID strings from ``train.csv`` or ``test.csv``.

        Returns
        -------
        pd.DataFrame
            Columns: ``["PetID"] + SENTIMENT_FEATURE_COLS``.
            One row per PetID in the same order as the input.
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

        return pd.DataFrame(rows, columns=["PetID"] + SENTIMENT_FEATURE_COLS)

    def load_all(self) -> pd.DataFrame:
        """Parse every JSON file in the sentiment directory.

        Useful for computing coverage statistics without a reference CSV.

        Returns
        -------
        pd.DataFrame
            Columns: ``["PetID"] + SENTIMENT_FEATURE_COLS``.
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
        """Return the fraction of PetIDs that have a corresponding JSON file.

        Parameters
        ----------
        pet_ids:
            Series of PetID strings.

        Returns
        -------
        float
            Value between 0.0 and 1.0.
        """
        if len(pet_ids) == 0:
            return 0.0
        found = sum(
            1 for pid in pet_ids
            if (self.sentiment_dir / f"{pid}.json").exists()
        )
        return found / len(pet_ids)
