"""
Tabular feature engineering for AdoptSense.

Provides :class:`TabularFeatures`, which transforms a raw pet-listing
DataFrame (as loaded from ``train.csv``) into a numeric feature matrix
ready for XGBoost.  VADER sentiment scores are computed inline from the
``Description`` column so no external API or pre-computed file is needed
at inference time.
"""

import pandas as pd

try:
    from nltk.sentiment import SentimentIntensityAnalyzer
    import nltk

    # Ensure the VADER lexicon is present; download silently if not.
    try:
        nltk.data.find("sentiment/vader_lexicon")
    except LookupError:
        nltk.download("vader_lexicon", quiet=True)

    SENTIMENT_AVAILABLE = True
except ImportError:
    SENTIMENT_AVAILABLE = False


class TabularFeatures:
    """Engineer tabular features for pet adoption speed prediction.

    All transformations are deterministic and stateless (no fit step),
    so a single instance can be reused across train, validation, and
    live inference without risk of data leakage.
    """

    def __init__(self) -> None:
        """Initialise label mappings and the VADER sentiment analyser."""
        self.speed_labels = {
            0: "Same day",
            1: "1-7d",
            2: "8-30d",
            3: "31-90d",
            4: "No adoption",
        }
        self.sia = SentimentIntensityAnalyzer() if SENTIMENT_AVAILABLE else None

    def __repr__(self) -> str:
        vader_status = "enabled" if self.sia is not None else "disabled (nltk not found)"
        return f"TabularFeatures(vader={vader_status})"

    def feature_engineering_tabular(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform raw pet-listing data into an XGBoost-ready feature matrix.

        Parameters
        ----------
        df:
            Raw DataFrame containing columns from ``train.csv`` or equivalent.
            The DataFrame is not modified in place; a copy is returned.

        Returns
        -------
        pd.DataFrame
            Numeric feature matrix with 27 columns (23 structural + 4 VADER
            sentiment).  All values are numeric so the caller can apply a
            ``StandardScaler`` directly.
        """
        df = df.copy()

        # --- 1. Fill missing numeric values with column medians ---
        numeric_cols = ["Age", "PhotoAmt", "Fee", "VideoAmt", "Quantity"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].fillna(df[col].median())

        # --- 2. Binary flags from numeric features ---
        df["has_photo"] = (df["PhotoAmt"] > 0).astype(int)
        df["has_video"] = (df["VideoAmt"] > 0).astype(int)
        df["is_free"] = (df["Fee"] == 0).astype(int)
        df["has_name"] = df["Name"].notna().astype(int)

        # --- 3. Ordinal age bins ---
        # 0 = <1 mo, 1 = 1-3 mo, 2 = 3-12 mo, 3 = 1-2 yr, 4 = 2+ yr
        df["age_bin"] = pd.cut(
            df["Age"],
            bins=[-1, 1, 3, 12, 24, 300],
            labels=["<1mo", "1-3mo", "3-12mo", "1-2yr", "2yr+"],
        ).cat.codes

        # --- 4. Description length and VADER sentiment ---
        df["desc_word_count"] = df["Description"].fillna("").str.split().str.len()

        if self.sia is not None:
            sentiments = df["Description"].fillna("").apply(
                lambda x: self.sia.polarity_scores(x)
                if x
                else {"compound": 0, "pos": 0, "neu": 0, "neg": 0}
            )
            df["sentiment_compound"] = sentiments.apply(lambda x: x["compound"])
            df["sentiment_pos"] = sentiments.apply(lambda x: x["pos"])
            df["sentiment_neg"] = sentiments.apply(lambda x: x["neg"])
            df["sentiment_neu"] = sentiments.apply(lambda x: x["neu"])
        else:
            # Fallback: zero-fill when VADER is unavailable
            df["sentiment_compound"] = 0.0
            df["sentiment_pos"] = 0.0
            df["sentiment_neg"] = 0.0
            df["sentiment_neu"] = 0.0

        # --- 5. Ordinal photo and description bins ---
        df["photo_bin"] = pd.cut(
            df["PhotoAmt"],
            bins=[-1, 0, 2, 5, 10, 100],
            labels=["0", "1-2", "3-5", "6-10", "10+"],
        ).cat.codes

        df["desc_bin"] = pd.cut(
            df["desc_word_count"],
            bins=[-1, 0, 25, 75, 150, 1000],
            labels=["None", "Short", "Medium", "Long", "Very Long"],
        ).cat.codes

        # --- 6. Categorical features (kept as integer codes for XGBoost) ---
        categorical_cols = [
            "Type", "Gender", "MaturitySize", "FurLength",
            "Vaccinated", "Dewormed", "Sterilized", "Health",
            "Color1", "State",
        ]
        for col in categorical_cols:
            if col in df.columns:
                df[col] = df[col].fillna(-1)

        # --- 7. Assemble final feature list ---
        feature_cols = (
            numeric_cols
            + ["has_photo", "has_video", "is_free", "has_name"]
            + ["age_bin", "photo_bin", "desc_bin", "desc_word_count"]
            + ["sentiment_compound", "sentiment_pos", "sentiment_neg", "sentiment_neu"]
            + categorical_cols
        )

        # Keep only columns that are present in the DataFrame
        feature_cols = [col for col in feature_cols if col in df.columns]
        return df[feature_cols]
