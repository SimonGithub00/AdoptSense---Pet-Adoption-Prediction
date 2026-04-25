"""
Matching Platform - Core utilities for two-sided marketplace
Handles listings, user types, KPI tracking, and pet matching
"""

import json
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Tuple
import pandas as pd


class UserType(Enum):
    """User types in the matching platform."""
    SHELTER = "shelter"
    PRIVATE_HOUSEHOLD = "private_household"
    ADOPTER = "adopter"


class PetStatus(Enum):
    """Status of a pet listing."""
    AVAILABLE = "available"
    MATCHED = "matched"
    ADOPTED = "adopted"
    DELISTED = "delisted"


class ListingPriority(Enum):
    """Listing priority levels (affects visibility)."""
    STANDARD = "standard"
    FEATURED = "featured"
    PROMOTED = "promoted"


@dataclass
class UserProfile:
    """User profile in the matching platform."""
    user_id: str
    username: str
    user_type: UserType
    email: str
    phone: Optional[str] = None
    location_state: Optional[str] = None
    organization_name: Optional[str] = None  # For shelters
    bio: Optional[str] = None
    verified: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        data = asdict(self)
        data['user_type'] = self.user_type.value
        return data


@dataclass
class PetListing:
    """Pet listing in the matching platform."""
    listing_id: str
    user_id: str
    pet_data: Dict  # Full pet feature data (from form/CSV)
    pet_name: str
    pet_type: int  # 1=Dog, 2=Cat
    adoption_speed_pred: int  # 0-4
    adoption_speed_confidence: float
    photos: List[str] = field(default_factory=list)  # Photo URLs/paths
    status: PetStatus = PetStatus.AVAILABLE
    priority: ListingPriority = ListingPriority.STANDARD
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    adopted_at: Optional[str] = None
    adoption_speed_actual: Optional[int] = None  # Recorded after adoption
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        data = asdict(self)
        data['status'] = self.status.value
        data['priority'] = self.priority.value
        return data


@dataclass
class PetMatch:
    """Match between a pet and potential adopter."""
    match_id: str
    listing_id: str
    adopter_id: str
    match_score: float  # 0-1 compatibility score
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    viewed_at: Optional[str] = None
    contacted_at: Optional[str] = None
    adopted_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class ListingKPI:
    """KPIs for a single listing."""
    listing_id: str
    views: int = 0
    contacts: int = 0
    matches: int = 0
    adoption_time_days: Optional[int] = None  # Null until adopted
    last_view_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class ShelterKPI:
    """Aggregated KPIs for a shelter."""
    user_id: str
    total_listings: int = 0
    active_listings: int = 0
    adopted_count: int = 0
    avg_adoption_speed: Optional[float] = None
    avg_length_of_stay_days: Optional[float] = None
    avg_views_per_listing: Optional[float] = None
    contact_rate: Optional[float] = None
    reinsertion_rate: Optional[float] = None  # % re-entering after adoption
    user_satisfaction_score: Optional[float] = None  # Likert scale average
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)


class MatchingPlatformDataStore:
    """In-memory data store for matching platform (prototyping).
    In production, replace with PostgreSQL + Redis."""
    
    def __init__(self):
        """Initialize data store."""
        self.users: Dict[str, UserProfile] = {}
        self.listings: Dict[str, PetListing] = {}
        self.matches: Dict[str, PetMatch] = {}
        self.listing_kpis: Dict[str, ListingKPI] = {}
        self.shelter_kpis: Dict[str, ShelterKPI] = {}
        self.watchlists: Dict[str, List[str]] = {}  # adopter_id -> [listing_ids]
    
    def add_user(self, user: UserProfile) -> bool:
        """Add a new user."""
        if user.user_id in self.users:
            return False
        self.users[user.user_id] = user
        if user.user_type == UserType.SHELTER:
            self.shelter_kpis[user.user_id] = ShelterKPI(user_id=user.user_id)
        return True
    
    def add_listing(self, listing: PetListing) -> bool:
        """Add a new pet listing."""
        if listing.listing_id in self.listings:
            return False
        self.listings[listing.listing_id] = listing
        self.listing_kpis[listing.listing_id] = ListingKPI(listing_id=listing.listing_id)
        
        # Increment shelter's active listings
        if listing.user_id in self.shelter_kpis:
            self.shelter_kpis[listing.user_id].active_listings += 1
            self.shelter_kpis[listing.user_id].total_listings += 1
        return True
    
    def get_listings(self, status: PetStatus = PetStatus.AVAILABLE, 
                    limit: int = 50) -> List[PetListing]:
        """Get listings by status."""
        return [
            listing for listing in self.listings.values()
            if listing.status == status
        ][:limit]
    
    def search_listings(self, pet_type: Optional[int] = None,
                       max_adoption_speed: Optional[int] = None,
                       state: Optional[str] = None,
                       limit: int = 50) -> List[PetListing]:
        """Search listings with filters."""
        results = [
            listing for listing in self.listings.values()
            if listing.status == PetStatus.AVAILABLE
            and (pet_type is None or listing.pet_type == pet_type)
            and (max_adoption_speed is None or listing.adoption_speed_pred <= max_adoption_speed)
        ]
        
        # Sort by adoption speed (fastest first)
        results.sort(key=lambda x: (x.adoption_speed_pred, -x.adoption_speed_confidence))
        
        return results[:limit]
    
    def add_to_watchlist(self, adopter_id: str, listing_id: str) -> bool:
        """Add listing to adopter's watchlist."""
        if adopter_id not in self.watchlists:
            self.watchlists[adopter_id] = []
        
        if listing_id not in self.watchlists[adopter_id]:
            self.watchlists[adopter_id].append(listing_id)
            return True
        return False
    
    def record_adoption(self, listing_id: str, adoption_speed_actual: int) -> bool:
        """Record adoption of a listing."""
        if listing_id not in self.listings:
            return False
        
        listing = self.listings[listing_id]
        listing.status = PetStatus.ADOPTED
        listing.adopted_at = datetime.now().isoformat()
        listing.adoption_speed_actual = adoption_speed_actual
        
        # Calculate actual adoption time in days
        created = datetime.fromisoformat(listing.created_at)
        adopted = datetime.fromisoformat(listing.adopted_at)
        adoption_days = (adopted - created).days
        
        # Update listing KPIs
        if listing_id in self.listing_kpis:
            self.listing_kpis[listing_id].adoption_time_days = adoption_days
        
        # Update shelter KPIs
        if listing.user_id in self.shelter_kpis:
            kpi = self.shelter_kpis[listing.user_id]
            kpi.adopted_count += 1
            kpi.active_listings -= 1
            self._update_shelter_averages(listing.user_id)
        
        return True
    
    def _update_shelter_averages(self, user_id: str):
        """Recalculate shelter KPIs."""
        if user_id not in self.shelter_kpis:
            return
        
        user_listings = [
            l for l in self.listings.values()
            if l.user_id == user_id and l.status == PetStatus.ADOPTED
        ]
        
        if not user_listings:
            return
        
        kpi = self.shelter_kpis[user_id]
        
        # Average adoption speed
        speeds = [l.adoption_speed_actual for l in user_listings if l.adoption_speed_actual is not None]
        if speeds:
            kpi.avg_adoption_speed = sum(speeds) / len(speeds)
        
        # Average length of stay
        los_values = [
            (datetime.fromisoformat(l.adopted_at) - datetime.fromisoformat(l.created_at)).days
            for l in user_listings
            if l.adopted_at
        ]
        if los_values:
            kpi.avg_length_of_stay_days = sum(los_values) / len(los_values)


class RecommendationEngine:
    """Generate recommendations for listings based on AI analysis."""
    
    ADOPTION_SPEED_LABELS = {
        0: "Same day (Exceptional)",
        1: "1-7 days (Strong)",
        2: "8-30 days (Moderate)",
        3: "31-90 days (Slow)",
        4: "No adoption (Critical)"
    }
    
    @staticmethod
    def get_shelter_recommendations(listing: PetListing, pred_data: Dict) -> List[Dict]:
        """Generate recommendations for shelter listings."""
        recommendations = []
        
        # Photo count recommendation
        if pred_data.get('PhotoAmt', 0) < 3:
            recommendations.append({
                'priority': 'high',
                'type': 'photos',
                'text': f"Add more photos (currently {pred_data.get('PhotoAmt', 0)}). Listings with 3-5 photos have 2.5x faster adoption."
            })
        
        # Fee recommendation
        if pred_data.get('Fee', 0) > 100:
            recommendations.append({
                'priority': 'high',
                'type': 'fee',
                'text': "Consider reducing adoption fee. Free/low-fee adoptions show 40% faster adoption speeds."
            })
        
        # Age recommendation
        age_months = pred_data.get('Age', 0)
        if age_months > 24:
            recommendations.append({
                'priority': 'medium',
                'type': 'age',
                'text': f"Older pets (>{age_months} months) adopt slower. Highlight unique personality traits and life experience."
            })
        
        # Description length
        desc_length = len(str(pred_data.get('Description', '')).split())
        if desc_length < 20:
            recommendations.append({
                'priority': 'medium',
                'type': 'description',
                'text': "Improve description (currently too short). Detailed, personable descriptions increase adoption likelihood."
            })
        elif desc_length > 200:
            recommendations.append({
                'priority': 'low',
                'type': 'description',
                'text': "Shorten description. Concise but engaging descriptions perform best."
            })
        
        # Video recommendation
        if pred_data.get('VideoAmt', 0) == 0:
            recommendations.append({
                'priority': 'low',
                'type': 'video',
                'text': "Add a short video. Listings with video increase engagement by 60%."
            })
        
        # Health status
        if pred_data.get('Health', 1) != 1:
            recommendations.append({
                'priority': 'high',
                'type': 'health',
                'text': "Be transparent about health status in description. Clear communication builds adopter trust."
            })
        
        return sorted(recommendations, key=lambda x: {'high': 0, 'medium': 1, 'low': 2}[x['priority']])
    
    @staticmethod
    def get_household_recommendations(listing: PetListing, pred_data: Dict) -> List[Dict]:
        """Generate recommendations for private household listings."""
        recs = RecommendationEngine.get_shelter_recommendations(listing, pred_data)
        
        # Add household-specific recommendations
        recs.append({
            'priority': 'medium',
            'type': 'story',
            'text': "Share your pet's story and why you're rehoming. Personal context helps adopters bond."
        })
        
        return recs


def create_sample_listings() -> List[PetListing]:
    """Create sample listings for demo."""
    return [
        PetListing(
            listing_id="listing_001",
            user_id="shelter_001",
            pet_name="Max",
            pet_type=1,
            adoption_speed_pred=0,
            adoption_speed_confidence=0.85,
            pet_data={'Age': 12, 'PhotoAmt': 4, 'Fee': 50, 'Health': 1},
            photos=["max_1.jpg", "max_2.jpg"]
        ),
        PetListing(
            listing_id="listing_002",
            user_id="household_001",
            pet_name="Whiskers",
            pet_type=2,
            adoption_speed_pred=1,
            adoption_speed_confidence=0.72,
            pet_data={'Age': 24, 'PhotoAmt': 2, 'Fee': 0, 'Health': 1},
            photos=["whiskers_1.jpg"]
        ),
        PetListing(
            listing_id="listing_003",
            user_id="shelter_001",
            pet_name="Luna",
            pet_type=2,
            adoption_speed_pred=3,
            adoption_speed_confidence=0.65,
            pet_data={'Age': 60, 'PhotoAmt': 1, 'Fee': 150, 'Health': 2},
            photos=["luna_1.jpg"]
        ),
    ]
