"""
Recommendations module - generates actionable recommendations for improving adoption
"""
import pandas as pd
from typing import Dict, List, Any


class RecommendationEngine:
    """Generate recommendations based on pet characteristics and predictions."""
    
    PHOTO_IMPACT = 0.95  # Photos are the strongest factor
    DESCRIPTION_IMPACT = 0.80
    AGE_IMPACT = 0.75
    FEE_IMPACT = 0.70
    HEALTH_IMPACT = 0.65
    
    RECOMMENDATIONS = {
        'photo': {
            'title': '📸 Photography Campaign',
            'description': 'Add high-quality photos of your pet',
            'tips': [
                'Upload 3-5 clear, high-quality photos minimum',
                'Include close-up face shots and full body photos',
                'Show pet in natural, appealing poses',
                'Ensure good lighting and clear focus',
                'Action shots (playing, running) are effective'
            ],
            'impact': 'CRITICAL - No photos = 60%+ slow adoption'
        },
        'description': {
            'title': '✍️ Description Enhancement',
            'description': 'Write engaging, detailed descriptions',
            'tips': [
                'Include personality traits and unique quirks',
                'Use warm, positive language to create emotional connection',
                'Mention favorite activities and hobbies',
                'Expand minimal descriptions to 50+ words',
                'Tell the pet\'s story - where they came from, why they\'re special'
            ],
            'impact': 'HIGH - Good descriptions accelerate adoption'
        },
        'price': {
            'title': '💰 Pricing Strategy',
            'description': 'Optimize adoption fee',
            'tips': [
                'Consider free or low-cost adoption incentives',
                'For slower categories: reduce fee by 20-30%',
                'Remember: fee is a significant barrier to adoption',
                'Deposit model: hold fee until sterilization completed',
                'Highlight fee value - includes vaccinations, health checks'
            ],
            'impact': 'HIGH - Free/low-cost pets adopt faster'
        },
        'age': {
            'title': '🐣 Age-Targeted Outreach',
            'description': 'Target marketing to age category',
            'tips': [
                'Young pets (0-3 mo): promote heavily on social media',
                'Older pets (2yr+): run special programs, emphasize maturity benefits',
                'Senior pets: highlight calm, trained behavior',
                'Create age-specific marketing campaigns',
                'Pair older pets in bonded pairs for better adoption'
            ],
            'impact': 'MEDIUM - Young pets naturally adopt faster'
        },
        'health': {
            'title': '🏥 Health Transparency',
            'description': 'Clearly communicate health status',
            'tips': [
                'Be upfront about any minor injuries or health issues',
                'Emphasize completed medical treatments',
                'Document vaccination and health records',
                'For injuries: provide recovery timeline and care needs',
                'Sterilization status: use as marketing angle (responsible pet owner)'
            ],
            'impact': 'MEDIUM - Health issues require extra marketing effort'
        },
        'sterilization': {
            'title': '🔒 Sterilization Strategy',
            'description': 'Leverage sterilization status',
            'tips': [
                'Not sterilized: mention costs and responsibility',
                'Sterilized: emphasize responsible ownership',
                'Offer sterilization as part of adoption package',
                'Use sterilization completion as adoption milestone',
                'Inform about behavioral & health benefits'
            ],
            'impact': 'LOW - Sterilization affects adoption pattern'
        }
    }
    
    def __init__(self):
        pass
    
    def generate_recommendations(self, pet_data: Dict[str, Any], prediction: int, confidence: float) -> List[Dict[str, Any]]:
        """
        Generate personalized recommendations for a pet based on its characteristics.
        
        Args:
            pet_data: Dictionary with pet information
            prediction: Adoption speed prediction (0-4)
            confidence: Confidence score for the prediction
            
        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        prioritized = []
        
        # Check each recommendation category
        if pet_data.get('PhotoAmt', 0) == 0:
            # Critical: no photos
            prioritized.append(('photo', self.PHOTO_IMPACT))
        
        desc_len = pet_data.get('desc_word_count', 0) if isinstance(pet_data.get('desc_word_count'), (int, float)) else 0
        if desc_len < 50:
            prioritized.append(('description', self.DESCRIPTION_IMPACT))
        
        if pet_data.get('Fee', 0) > 0:
            prioritized.append(('price', self.FEE_IMPACT))
        
        age = pet_data.get('Age', 0)
        if age and (age > 24):  # Older pets
            prioritized.append(('age', self.AGE_IMPACT))
        
        health = pet_data.get('Health', 1)
        if health and health > 1:  # Not healthy
            prioritized.append(('health', self.HEALTH_IMPACT))
        
        if pet_data.get('Sterilized', 0) in [2, 3]:  # Not sterilized or unsure
            prioritized.append(('sterilization', self.PHOTO_IMPACT * 0.3 if pet_data.get('Sterilized') == 2 else 0.4))
        
        # Sort by impact and get top 3
        prioritized.sort(key=lambda x: x[1], reverse=True)
        
        for key, impact_score in prioritized[:3]:
            if key in self.RECOMMENDATIONS:
                rec_data = self.RECOMMENDATIONS[key].copy()
                rec_data['key'] = key
                rec_data['impact_score'] = impact_score
                recommendations.append(rec_data)
        
        # If adoption is already fast, acknowledge it
        if prediction <= 1:
            recommendations.insert(0, {
                'key': 'maintain',
                'title': '✨ Excellent Profile',
                'description': 'Your pet has strong adoption appeal',
                'tips': ['Keep the current approach', 'Your pet is in the fast adoption category'],
                'impact': 'POSITIVE - Pet is performing well'
            })
        
        return recommendations
    
    def generate_summary(self, pet_data: Dict[str, Any], prediction: int, confidence: float) -> str:
        """
        Generate a text summary of recommendations.
        
        Args:
            pet_data: Dictionary with pet information
            prediction: Adoption speed prediction
            confidence: Confidence score
            
        Returns:
            Text summary
        """
        from frontend.utils.predictions import AdoptionPredictor
        
        speed_label = AdoptionPredictor.ADOPTION_SPEED_LABELS.get(prediction, "Unknown")
        
        summary = f"""
**Adoption Speed Prediction:** {speed_label} ({confidence*100:.1f}% confidence)

### Summary of Recommendations:

Based on the analysis of your pet's profile, here are the key areas to focus on:

1. **Photography** - Visual appeal is the #1 factor determining adoption speed
2. **Description Quality** - A compelling story increases interest dramatically  
3. **Reasonable Pricing** - Fee is a barrier to adoption for slower categories
4. **Age-Appropriate Marketing** - Match promotional strategy to pet's age group
5. **Health Transparency** - Clear health information builds trust with adopters

### Action Plan:

- **Immediate:** Address critical issues (no photos, minimal description)
- **Short-term:** Optimize listing quality (better photos, enhanced description)
- **Medium-term:** Consider pricing and marketing adjustments
- **Ongoing:** Update listing as pet settles, gather adoption interest feedback
        """
        
        return summary


def get_recommendations(pet_data: Dict[str, Any], prediction: int, confidence: float) -> List[Dict[str, Any]]:
    """Convenience function to get recommendations."""
    engine = RecommendationEngine()
    return engine.generate_recommendations(pet_data, prediction, confidence)


def get_recommendation_summary(pet_data: Dict[str, Any], prediction: int, confidence: float) -> str:
    """Convenience function to get recommendation summary."""
    engine = RecommendationEngine()
    return engine.generate_summary(pet_data, prediction, confidence)
