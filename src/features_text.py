"""
Text feature engineering for AdoptSense (stub for future use).

This module is reserved for TF-IDF or transformer-based NLP features
derived from the pet ``Description`` column.  Current sentiment extraction
is handled by VADER inside :class:`~src.features_tabular.TabularFeatures`.

Planned extension
-----------------
A ``TextFeatures`` transformer could be added here and combined with the
tabular preprocessing pipeline for richer description representations, for
example a fine-tuned DistilBERT encoder or a sparse TF-IDF matrix passed
to a separate branch of the model.
"""
