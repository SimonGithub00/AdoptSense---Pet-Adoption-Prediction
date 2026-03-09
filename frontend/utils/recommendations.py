"""
Recommendations module - identifies factors that help or hinder pet adoption.
"""
from typing import Dict, List, Any, Tuple


def _word_count(d: Dict) -> int:
    """Return word count of the pet's description."""
    desc = d.get('Description', '') or ''
    return len(str(desc).split())


# Each factor has an optional 'positive' and/or 'negative' side.
# 'check' receives the raw pet data dict and returns True if the condition applies.
# 'label' and 'sentence' are callables that return a string given the pet data dict.
# 'weight' controls ranking priority (higher = shown first).
# Weights span from 10 (critical) down to 1 (minor but worth mentioning).
ADOPTION_FACTORS = [
    # --- PHOTOS ---
    {
        'key': 'photos_many',
        'positive': {
            'check': lambda d: d.get('PhotoAmt', 0) >= 5,
            'label': lambda d: f"Many photos ({int(d.get('PhotoAmt', 0))})",
            'sentence': lambda d: (
                f"Having {int(d.get('PhotoAmt', 0))} photos gives adopters a thorough "
                "look at the pet and is the single strongest driver of fast adoption."
            ),
        },
        'negative': None,
        'weight': 10,
    },
    {
        'key': 'photos_some',
        'positive': {
            'check': lambda d: 3 <= d.get('PhotoAmt', 0) < 5,
            'label': lambda d: f"Has {int(d.get('PhotoAmt', 0))} photos",
            'sentence': lambda d: (
                f"Having {int(d.get('PhotoAmt', 0))} photos is a good start — "
                "photos are the strongest single factor in attracting adopters."
            ),
        },
        'negative': None,
        'weight': 9,
    },
    {
        'key': 'photos_few',
        'positive': None,
        'negative': {
            'check': lambda d: 1 <= d.get('PhotoAmt', 0) <= 2,
            'label': lambda d: f"Only {int(d.get('PhotoAmt', 0))} photo(s) — more recommended",
            'sentence': lambda d: (
                f"Having only {int(d.get('PhotoAmt', 0))} photo(s) limits adoption appeal — "
                "listings with 5+ photos attract significantly more interest."
            ),
        },
        'weight': 9,
    },
    {
        'key': 'photos_none',
        'positive': None,
        'negative': {
            'check': lambda d: d.get('PhotoAmt', 0) == 0,
            'label': lambda d: "No photos uploaded",
            'sentence': lambda d: (
                "No photos is the single biggest barrier to adoption — "
                "listings without images are almost never chosen by potential adopters."
            ),
        },
        'weight': 10,
    },
    # --- ADOPTION FEE ---
    {
        'key': 'free_adoption',
        'positive': {
            'check': lambda d: d.get('Fee', 0) == 0,
            'label': lambda d: "Free adoption fee",
            'sentence': lambda d: (
                "A zero adoption fee removes the most common financial barrier "
                "and attracts significantly more potential adopters."
            ),
        },
        'negative': None,
        'weight': 9,
    },
    {
        'key': 'high_fee',
        'positive': None,
        'negative': {
            'check': lambda d: d.get('Fee', 0) > 150,
            'label': lambda d: f"High adoption fee ({int(d.get('Fee', 0))})",
            'sentence': lambda d: (
                f"An adoption fee of {int(d.get('Fee', 0))} deters many adopters — "
                "consider reducing it significantly or waiving it entirely."
            ),
        },
        'weight': 9,
    },
    {
        'key': 'moderate_fee',
        'positive': None,
        'negative': {
            'check': lambda d: 0 < d.get('Fee', 0) <= 150,
            'label': lambda d: f"Has an adoption fee ({int(d.get('Fee', 0))})",
            'sentence': lambda d: (
                f"Even a modest fee of {int(d.get('Fee', 0))} can slow adoption — "
                "free listings consistently adopt faster across all categories."
            ),
        },
        'weight': 7,
    },
    # --- AGE ---
    {
        'key': 'young_age',
        'positive': {
            'check': lambda d: 0 <= d.get('Age', 999) <= 12,
            'label': lambda d: f"Young age ({int(d.get('Age', 0))} months)",
            'sentence': lambda d: (
                f"At {int(d.get('Age', 0))} months old, this pet is in the most "
                "adoptable age range and naturally attracts the highest demand."
            ),
        },
        'negative': None,
        'weight': 8,
    },
    {
        'key': 'middle_age',
        'positive': None,
        'negative': {
            'check': lambda d: 13 <= d.get('Age', 0) <= 36,
            'label': lambda d: f"Past peak adoption age ({int(d.get('Age', 0))} months)",
            'sentence': lambda d: (
                f"At {int(d.get('Age', 0))} months, demand is lower than for young pets — "
                "highlighting personality and training can compensate."
            ),
        },
        'weight': 6,
    },
    {
        'key': 'old_age',
        'positive': None,
        'negative': {
            'check': lambda d: d.get('Age', 0) > 36,
            'label': lambda d: f"Older age ({int(d.get('Age', 0))} months)",
            'sentence': lambda d: (
                f"At {int(d.get('Age', 0))} months, this pet faces a harder adoption "
                "market — targeted senior-pet campaigns are strongly recommended."
            ),
        },
        'weight': 8,
    },
    # --- HEALTH ---
    {
        'key': 'healthy',
        'positive': {
            'check': lambda d: d.get('Health', 1) == 1,
            'label': lambda d: "In good health",
            'sentence': lambda d: (
                "Being in good health is a strong positive signal — "
                "healthy pets typically adopt 2-3x faster than those with health issues."
            ),
        },
        'negative': None,
        'weight': 7,
    },
    {
        'key': 'health_issues',
        'positive': None,
        'negative': {
            'check': lambda d: d.get('Health', 1) in [2, 3],
            'label': lambda d: (
                "Minor injury" if d.get('Health') == 2 else "Serious injury or illness"
            ),
            'sentence': lambda d: (
                "A minor injury slows adoption — be transparent about recovery "
                "timeline and care needs to reassure potential adopters."
                if d.get('Health') == 2 else
                "A serious health condition is a significant obstacle — "
                "extra veterinary documentation and targeted outreach are essential."
            ),
        },
        'weight': 7,
    },
    # --- VACCINATED ---
    {
        'key': 'vaccinated',
        'positive': {
            'check': lambda d: d.get('Vaccinated', 3) == 1,
            'label': lambda d: "Vaccinated",
            'sentence': lambda d: (
                "Being vaccinated reassures adopters about the pet's health "
                "and reduces their expected initial veterinary costs."
            ),
        },
        'negative': None,
        'weight': 7,
    },
    {
        'key': 'not_vaccinated',
        'positive': None,
        'negative': {
            'check': lambda d: d.get('Vaccinated', 3) == 2,
            'label': lambda d: "Not vaccinated",
            'sentence': lambda d: (
                "Not being vaccinated raises health concerns and adds unexpected "
                "costs for the adopter, which can discourage many prospects."
            ),
        },
        'weight': 7,
    },
    {
        'key': 'vaccination_unknown',
        'positive': None,
        'negative': {
            'check': lambda d: d.get('Vaccinated', 3) == 3,
            'label': lambda d: "Vaccination status unknown",
            'sentence': lambda d: (
                "Uncertain vaccination status creates doubt for adopters — "
                "getting a vet check and confirming status will improve appeal."
            ),
        },
        'weight': 5,
    },
    # --- DEWORMED ---
    {
        'key': 'dewormed',
        'positive': {
            'check': lambda d: d.get('Dewormed', 3) == 1,
            'label': lambda d: "Dewormed",
            'sentence': lambda d: (
                "Being dewormed signals attentive care and makes the pet "
                "more appealing to health-conscious adopters."
            ),
        },
        'negative': None,
        'weight': 6,
    },
    {
        'key': 'not_dewormed',
        'positive': None,
        'negative': {
            'check': lambda d: d.get('Dewormed', 3) == 2,
            'label': lambda d: "Not dewormed",
            'sentence': lambda d: (
                "Not being dewormed can concern potential adopters about "
                "parasite risk and the overall health of the pet."
            ),
        },
        'weight': 6,
    },
    {
        'key': 'dewormed_unknown',
        'positive': None,
        'negative': {
            'check': lambda d: d.get('Dewormed', 3) == 3,
            'label': lambda d: "Deworming status unknown",
            'sentence': lambda d: (
                "Uncertainty about deworming status can raise concern — "
                "a simple vet visit to confirm and document this will help."
            ),
        },
        'weight': 4,
    },
    # --- STERILIZED ---
    {
        'key': 'sterilized',
        'positive': {
            'check': lambda d: d.get('Sterilized', 3) == 1,
            'label': lambda d: "Sterilized",
            'sentence': lambda d: (
                "Being sterilized signals responsible care and appeals to adopters "
                "who want a pet ready to bring home without extra procedures."
            ),
        },
        'negative': None,
        'weight': 5,
    },
    {
        'key': 'not_sterilized',
        'positive': None,
        'negative': {
            'check': lambda d: d.get('Sterilized', 3) == 2,
            'label': lambda d: "Not sterilized",
            'sentence': lambda d: (
                "Not being sterilized adds an additional responsibility and cost "
                "for the adopter, which can discourage some prospects."
            ),
        },
        'weight': 5,
    },
    {
        'key': 'sterilized_unknown',
        'positive': None,
        'negative': {
            'check': lambda d: d.get('Sterilized', 3) == 3,
            'label': lambda d: "Sterilization status unknown",
            'sentence': lambda d: (
                "Uncertain sterilization status is off-putting for many adopters — "
                "clarifying this adds confidence and reduces hesitation."
            ),
        },
        'weight': 4,
    },
    # --- DESCRIPTION ---
    {
        'key': 'great_description',
        'positive': {
            'check': lambda d: _word_count(d) >= 80,
            'label': lambda d: f"Rich description ({_word_count(d)} words)",
            'sentence': lambda d: (
                f"A {_word_count(d)}-word description tells the pet's story effectively "
                "and creates a strong emotional connection with potential adopters."
            ),
        },
        'negative': None,
        'weight': 7,
    },
    {
        'key': 'decent_description',
        'positive': {
            'check': lambda d: 50 <= _word_count(d) < 80,
            'label': lambda d: f"Adequate description ({_word_count(d)} words)",
            'sentence': lambda d: (
                f"A {_word_count(d)}-word description provides a good introduction — "
                "expanding it further with personality traits would boost interest."
            ),
        },
        'negative': None,
        'weight': 5,
    },
    {
        'key': 'short_description',
        'positive': None,
        'negative': {
            'check': lambda d: 20 <= _word_count(d) < 50,
            'label': lambda d: f"Short description ({_word_count(d)} words)",
            'sentence': lambda d: (
                f"A {_word_count(d)}-word description is too brief — aim for 80+ words "
                "covering personality, history, and what makes this pet special."
            ),
        },
        'weight': 6,
    },
    {
        'key': 'very_short_description',
        'positive': None,
        'negative': {
            'check': lambda d: _word_count(d) < 20,
            'label': lambda d: f"Very short description ({_word_count(d)} words)",
            'sentence': lambda d: (
                f"Only {_word_count(d)} words — this is far too short to build "
                "interest; a compelling story is one of the most effective tools for adoption."
            ),
        },
        'weight': 8,
    },
    # --- SIZE ---
    {
        'key': 'small_size',
        'positive': {
            'check': lambda d: d.get('MaturitySize', 0) == 1,
            'label': lambda d: "Small body size",
            'sentence': lambda d: (
                "Small pets fit easily in apartments and homes with limited space, "
                "which broadens the pool of eligible adopters."
            ),
        },
        'negative': None,
        'weight': 3,
    },
    {
        'key': 'medium_size',
        'positive': None,
        'negative': {
            'check': lambda d: d.get('MaturitySize', 0) == 2,
            'label': lambda d: "Medium size — slightly limits adopter pool",
            'sentence': lambda d: (
                "Medium-sized pets are popular but exclude some apartment dwellers — "
                "emphasizing adaptability and exercise needs can help."
            ),
        },
        'weight': 2,
    },
    {
        'key': 'large_size',
        'positive': None,
        'negative': {
            'check': lambda d: d.get('MaturitySize', 0) in [3, 4],
            'label': lambda d: "Large or extra-large size",
            'sentence': lambda d: (
                "Large pets require more space and resources, which notably narrows "
                "the adopter pool — highlighting a gentle temperament can help."
            ),
        },
        'weight': 4,
    },
    # --- QUANTITY ---
    {
        'key': 'single_pet',
        'positive': {
            'check': lambda d: int(d.get('Quantity', 1)) == 1,
            'label': lambda d: "Listed as a single pet",
            'sentence': lambda d: (
                "Being listed individually simplifies the adoption decision "
                "and broadens the potential adopter base considerably."
            ),
        },
        'negative': None,
        'weight': 3,
    },
    {
        'key': 'multiple_pets',
        'positive': None,
        'negative': {
            'check': lambda d: int(d.get('Quantity', 1)) > 1,
            'label': lambda d: f"Multiple pets in listing ({int(d.get('Quantity', 1))} animals)",
            'sentence': lambda d: (
                f"Adopting {int(d.get('Quantity', 1))} pets at once is a bigger "
                "commitment, which reduces the number of eligible adopters."
            ),
        },
        'weight': 4,
    },
    # --- VIDEO ---
    {
        'key': 'has_video',
        'positive': {
            'check': lambda d: d.get('VideoAmt', 0) >= 1,
            'label': lambda d: f"Has {int(d.get('VideoAmt', 0))} video(s)",
            'sentence': lambda d: (
                "Videos let adopters see the pet's personality in motion, "
                "giving the listing a meaningful edge over photo-only profiles."
            ),
        },
        'negative': None,
        'weight': 4,
    },
    {
        'key': 'no_video',
        'positive': None,
        'negative': {
            'check': lambda d: d.get('VideoAmt', 0) == 0,
            'label': lambda d: "No video uploaded",
            'sentence': lambda d: (
                "Adding even one short video showing the pet's personality "
                "can significantly increase engagement from potential adopters."
            ),
        },
        'weight': 3,
    },
]


def get_description_sentiment(description: str) -> dict:
    """
    Run VADER sentiment analysis on a pet description (same analysis the model uses).

    Returns a dict with keys:
        compound  (-1 to +1 overall score)
        pos / neu / neg  (0–1 proportion scores)
        tone        human-readable label
        tone_color  'success' | 'info' | 'warning' | 'error'  (for Streamlit)
        advice      one-sentence interpretation for the adopter
    """
    try:
        import ssl
        import certifi
        from nltk.sentiment import SentimentIntensityAnalyzer
        import nltk
        try:
            nltk.data.find('sentiment/vader_lexicon')
        except LookupError:
            _orig = ssl._create_default_https_context
            ssl._create_default_https_context = lambda: ssl.create_default_context(
                cafile=certifi.where()
            )
            try:
                nltk.download('vader_lexicon', quiet=True)
            finally:
                ssl._create_default_https_context = _orig
        sia = SentimentIntensityAnalyzer()
        scores = sia.polarity_scores(description or '')
    except Exception:
        scores = {'compound': 0.0, 'pos': 0.0, 'neu': 1.0, 'neg': 0.0}

    compound = scores['compound']

    if compound >= 0.5:
        tone, tone_color, advice = (
            'Very Positive', 'success',
            'The description radiates warmth and enthusiasm — '
            'this strongly supports a faster adoption.'
        )
    elif compound >= 0.05:
        tone, tone_color, advice = (
            'Positive', 'success',
            'The description has a positive tone, which builds emotional connection '
            'with potential adopters.'
        )
    elif compound > -0.05:
        tone, tone_color, advice = (
            'Neutral', 'info',
            'The description reads as factual/neutral — adding warmer, more personal '
            'language could improve adoption speed.'
        )
    elif compound > -0.5:
        tone, tone_color, advice = (
            'Negative', 'warning',
            'The description carries a negative tone; consider rewriting with upbeat, '
            'hopeful language to attract more adopters.'
        )
    else:
        tone, tone_color, advice = (
            'Very Negative', 'error',
            'The description is strongly negative in tone — this actively discourages '
            'adopters and should be rewritten.'
        )

    return {
        'compound': compound,
        'pos': scores['pos'],
        'neu': scores['neu'],
        'neg': scores['neg'],
        'tone': tone,
        'tone_color': tone_color,
        'advice': advice,
    }


def get_adoption_factors(
    pet_data: Dict[str, Any]
) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    """
    Evaluate a pet's features and return the top-5 positive and top-5 negative
    adoption factors, each with a human-readable label and one-sentence explanation.

    Args:
        pet_data: Raw pet data dictionary (from original_data in prediction results).

    Returns:
        (positive_factors, negative_factors) - each a list of up to 5 dicts with
        keys 'label' and 'sentence', sorted by importance.
    """
    positives = []
    negatives = []

    for factor in ADOPTION_FACTORS:
        try:
            if factor['positive'] and factor['positive']['check'](pet_data):
                positives.append({
                    'label': factor['positive']['label'](pet_data),
                    'sentence': factor['positive']['sentence'](pet_data),
                    'weight': factor['weight'],
                })
            if factor['negative'] and factor['negative']['check'](pet_data):
                negatives.append({
                    'label': factor['negative']['label'](pet_data),
                    'sentence': factor['negative']['sentence'](pet_data),
                    'weight': factor['weight'],
                })
        except Exception:
            continue

    positives.sort(key=lambda x: x['weight'], reverse=True)
    negatives.sort(key=lambda x: x['weight'], reverse=True)

    return positives[:5], negatives[:5]
