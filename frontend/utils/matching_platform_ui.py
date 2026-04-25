"""
Matching Platform UI - Streamlit interface for the two-sided marketplace
Handles browsing, listing creation, KPI dashboards, and user interactions
"""

import uuid
from datetime import datetime
from typing import Optional, Tuple
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from frontend.utils.matching_platform import (
    MatchingPlatformDataStore,
    UserProfile,
    PetListing,
    UserType,
    PetStatus,
    ListingPriority,
    RecommendationEngine,
    create_sample_listings,
)
from frontend.utils.predictions import AdoptionPredictor


class MatchingPlatformUI:
    """Streamlit UI for the matching platform."""
    
    ADOPTION_SPEED_COLORS = {
        0: "#4CAF50",  # Green - Fast
        1: "#8BC34A",  # Light Green
        2: "#FFC107",  # Amber
        3: "#FF9800",  # Orange
        4: "#F44336",  # Red
    }
    
    ADOPTION_SPEED_LABELS = {
        0: "⭐⭐⭐⭐⭐ Same day",
        1: "⭐⭐⭐⭐ 1-7 days",
        2: "⭐⭐⭐ 8-30 days",
        3: "⭐⭐ 31-90 days",
        4: "⭐ No adoption",
    }
    
    @staticmethod
    def initialize_session_state():
        """Initialize session state for matching platform."""
        if 'mp_datastore' not in st.session_state:
            st.session_state.mp_datastore = MatchingPlatformDataStore()
            
            # Create sample data for demo
            for listing in create_sample_listings():
                st.session_state.mp_datastore.add_listing(listing)
        
        if 'mp_current_user' not in st.session_state:
            st.session_state.mp_current_user = None
        
        if 'mp_current_view' not in st.session_state:
            st.session_state.mp_current_view = 'browse'
    
    @staticmethod
    def render_user_selector():
        """Render user role selector in sidebar."""
        st.sidebar.markdown("### 👤 You Are:")
        user_type = st.sidebar.radio(
            "Select your role:",
            options=["Adopter", "Shelter Manager", "Private Owner"],
            key="user_role_selector"
        )
        
        return {
            "Adopter": UserType.ADOPTER,
            "Shelter Manager": UserType.SHELTER,
            "Private Owner": UserType.PRIVATE_HOUSEHOLD,
        }[user_type]
    
    @staticmethod
    def render_main_navigation(user_type: UserType):
        """Render main navigation menu."""
        if user_type == UserType.ADOPTER:
            tabs = ["🔍 Browse Pets", "❤️ Watchlist", "💬 Messages", "📊 Dashboard"]
        elif user_type == UserType.SHELTER:
            tabs = ["📋 My Listings", "➕ Create Listing", "📊 KPIs", "📧 Messages"]
        else:  # PRIVATE_HOUSEHOLD
            tabs = ["📋 My Listings", "➕ Create Listing", "📊 Analytics", "❤️ Watchlist"]
        
        return tabs
    
    @staticmethod
    def render_listings_browser():
        """Render listings browser for adopters."""
        st.header("🔍 Browse Available Pets")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            pet_type = st.selectbox(
                "Pet Type",
                options=[None, 1, 2],
                format_func=lambda x: "All Types" if x is None else ("🐶 Dogs" if x == 1 else "🐱 Cats")
            )
        
        with col2:
            adoption_speed = st.selectbox(
                "Max Adoption Speed",
                options=[None, 0, 1, 2, 3, 4],
                format_func=lambda x: "All Speeds" if x is None else MatchingPlatformUI.ADOPTION_SPEED_LABELS.get(x, "")
            )
        
        with col3:
            sort_by = st.selectbox(
                "Sort By",
                options=["Fastest Adoption", "Newest", "Most Views"],
                key="listings_sort"
            )
        
        st.markdown("---")
        
        # Get listings
        datastore = st.session_state.mp_datastore
        listings = datastore.search_listings(
            pet_type=pet_type,
            max_adoption_speed=adoption_speed,
            limit=20
        )
        
        if not listings:
            st.info("No pets match your criteria. Try adjusting your filters!")
            return
        
        # Display listings in grid
        cols = st.columns(3)
        for idx, listing in enumerate(listings):
            with cols[idx % 3]:
                MatchingPlatformUI.render_listing_card(listing)
    
    @staticmethod
    def render_listing_card(listing: PetListing):
        """Render a single listing card."""
        with st.container(border=True):
            # Pet name and type
            pet_type_emoji = "🐶" if listing.pet_type == 1 else "🐱"
            st.markdown(f"## {pet_type_emoji} {listing.pet_name}")
            
            # Adoption speed badge
            speed = listing.adoption_speed_pred
            speed_label = MatchingPlatformUI.ADOPTION_SPEED_LABELS.get(speed, "Unknown")
            confidence = listing.adoption_speed_confidence
            
            color = MatchingPlatformUI.ADOPTION_SPEED_COLORS.get(speed, "#999999")
            st.markdown(
                f"<div style='background-color: {color}; color: white; padding: 0.5rem; "
                f"border-radius: 0.5rem; text-align: center; margin: 0.5rem 0;'>"
                f"<b>{speed_label}</b><br><small>Confidence: {confidence:.0%}</small></div>",
                unsafe_allow_html=True
            )
            
            # Pet details
            age_months = listing.pet_data.get('Age', 0)
            age_years = age_months / 12
            st.caption(f"📅 Age: {age_years:.1f} years ({age_months} months)")
            
            photo_count = len(listing.photos)
            st.caption(f"📸 Photos: {photo_count}")
            
            # Actions
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("💬 Message", key=f"msg_{listing.listing_id}", use_container_width=True):
                    st.success("Message sent! (Demo)")
            
            with col2:
                if st.button("❤️ Save", key=f"save_{listing.listing_id}", use_container_width=True):
                    if 'adopter_001' not in st.session_state.mp_datastore.watchlists:
                        st.session_state.mp_datastore.watchlists['adopter_001'] = []
                    if listing.listing_id not in st.session_state.mp_datastore.watchlists['adopter_001']:
                        st.session_state.mp_datastore.watchlists['adopter_001'].append(listing.listing_id)
                        st.success("Added to watchlist!")
                    else:
                        st.info("Already in watchlist")
            
            with col3:
                if st.button("ℹ️ Details", key=f"details_{listing.listing_id}", use_container_width=True):
                    st.session_state.mp_view_details = listing.listing_id
    
    @staticmethod
    def render_my_listings_manager():
        """Render listings manager for shelters/households."""
        st.header("📋 My Listings")
        
        user_type = st.session_state.get('mp_user_type', UserType.SHELTER)
        datastore = st.session_state.mp_datastore
        
        # Get user's listings
        user_listings = [
            l for l in datastore.listings.values()
            if l.user_id in ["shelter_001", "household_001"]  # Demo users
        ]
        
        if not user_listings:
            st.info("No listings yet. Create one to get started!")
            return
        
        # Summary stats
        col1, col2, col3, col4 = st.columns(4)
        
        active = sum(1 for l in user_listings if l.status == PetStatus.AVAILABLE)
        adopted = sum(1 for l in user_listings if l.status == PetStatus.ADOPTED)
        
        with col1:
            st.metric("Total Listings", len(user_listings))
        with col2:
            st.metric("Active", active)
        with col3:
            st.metric("Adopted", adopted)
        with col4:
            adoption_rate = (adopted / len(user_listings) * 100) if user_listings else 0
            st.metric("Adoption Rate", f"{adoption_rate:.1f}%")
        
        st.markdown("---")
        
        # Listings table
        for listing in user_listings:
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                st.markdown(f"**{listing.pet_name}**")
                st.caption(f"Status: {listing.status.value} | Pred Speed: {MatchingPlatformUI.ADOPTION_SPEED_LABELS.get(listing.adoption_speed_pred, 'Unknown')}")
            
            with col2:
                if st.button("✏️ Edit", key=f"edit_{listing.listing_id}", use_container_width=True):
                    st.info("Edit functionality coming soon!")
            
            with col3:
                if st.button("📊 Stats", key=f"stats_{listing.listing_id}", use_container_width=True):
                    st.session_state.mp_view_stats = listing.listing_id
            
            with col4:
                if listing.status == PetStatus.AVAILABLE:
                    if st.button("✅ Mark Adopted", key=f"adopt_{listing.listing_id}", use_container_width=True):
                        datastore.record_adoption(listing.listing_id, adoption_speed_actual=listing.adoption_speed_pred)
                        st.rerun()
    
    @staticmethod
    def render_create_listing_form(user_type: UserType):
        """Render form to create a new listing."""
        st.header("➕ Create Pet Listing")
        
        if user_type == UserType.SHELTER:
            st.info("🏥 Shelter Mode: You can list multiple pets from your inventory.")
        else:
            st.info("👨‍👩‍👧 Private Mode: List your personal pet to find a new home.")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            pet_name = st.text_input("Pet Name", value="")
            pet_type = st.selectbox("Pet Type", options=[1, 2],
                                   format_func=lambda x: "🐶 Dog" if x == 1 else "🐱 Cat")
            age_months = st.slider("Age (months)", min_value=0, max_value=120, value=12)
        
        with col2:
            fee = st.number_input("Adoption Fee ($)", min_value=0, max_value=1000, value=50, step=10)
            photo_count = st.number_input("Number of Photos", min_value=0, max_value=10, value=3)
            health_status = st.selectbox("Health Status", 
                                        options=[1, 2, 3],
                                        format_func=lambda x: {1: "Healthy", 2: "Minor Injury", 3: "Serious Injury"}[x])
        
        description = st.text_area("Pet Description", placeholder="Tell us about this pet...", height=100)
        
        st.markdown("---")
        
        # Photo upload (placeholder)
        st.markdown("### 📸 Upload Photos")
        uploaded_files = st.file_uploader("Upload pet photos", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])
        
        st.markdown("---")
        
        # Prediction preview (optional)
        show_preview = st.checkbox("Get AI Prediction Preview", value=True)
        
        if show_preview and pet_name:
            st.markdown("### 🤖 AI Adoption Speed Prediction")
            st.info("Based on your listing data, we estimate...")
            
            # Create dummy prediction
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Predicted Adoption Speed", "Speed 1 (1-7 days)", delta="Excellent")
            with col2:
                st.metric("Confidence", "85%", delta="+5%")
            
            # Show recommendations
            with st.expander("📋 Recommendations to improve adoption speed"):
                st.markdown("""
                1. **Add more photos** - You have 3 photos, aim for 4-5 for best results
                2. **Consider free adoption** - Free pets adopt 40% faster
                3. **Highlight personality** - Your description is good, keep it detailed
                """)
        
        st.markdown("---")
        
        col1, col2 = st.columns([1, 4])
        
        with col1:
            if st.button("📤 Publish Listing", type="primary", use_container_width=True):
                if not pet_name or not description:
                    st.error("Please fill in pet name and description")
                else:
                    st.success(f"✅ Listing published! Pet '{pet_name}' is now visible to adopters.")
                    st.balloons()
        
        with col2:
            st.caption("Your listing will be live immediately and visible to potential adopters in your area.")
    
    @staticmethod
    def render_kpi_dashboard(user_type: UserType):
        """Render KPI dashboard for shelters/households."""
        st.header("📊 Performance Dashboard")
        
        datastore = st.session_state.mp_datastore
        user_id = "shelter_001"  # Demo user
        
        if user_id not in datastore.shelter_kpis:
            st.info("No adoption data yet. Create listings to get started!")
            return
        
        kpi = datastore.shelter_kpis[user_id]
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Listings", kpi.total_listings, help="Total pets listed")
        with col2:
            st.metric("Adopted", kpi.adopted_count, help="Successfully adopted")
        with col3:
            adoption_rate = (kpi.adopted_count / kpi.total_listings * 100) if kpi.total_listings > 0 else 0
            st.metric("Adoption Rate", f"{adoption_rate:.1f}%")
        with col4:
            st.metric("Avg LOS (days)", 
                     f"{kpi.avg_length_of_stay_days:.0f}" if kpi.avg_length_of_stay_days else "N/A",
                     help="Avg length of stay in shelter")
        
        st.markdown("---")
        
        # Charts
        tab1, tab2, tab3 = st.tabs(["📈 Trends", "🎯 Adoption Patterns", "📋 Details"])
        
        with tab1:
            st.markdown("### Adoption Timeline")
            # Sample data
            dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
            adoptions = [0, 0, 1, 0, 0, 2, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=dates, y=adoptions, mode='lines+markers', name='Adoptions'))
            fig.update_layout(title="Daily Adoptions (Last 30 Days)", xaxis_title="Date", yaxis_title="Count", height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            st.markdown("### Adoption Speed Distribution")
            
            speeds = [0, 1, 1, 2, 1, 3]  # Sample data
            fig = px.histogram(speeds, nbins=5, title="Distribution of Adoption Speeds",
                              labels={0: "Adoption Speed", "count": "Number of Pets"})
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.markdown("### Detailed Statistics")
            st.dataframe({
                "Metric": ["Avg Adoption Speed", "Avg Length of Stay", "Contact Rate", "Reinsertion Rate"],
                "Value": [
                    f"{kpi.avg_adoption_speed:.1f}" if kpi.avg_adoption_speed else "N/A",
                    f"{kpi.avg_length_of_stay_days:.0f} days" if kpi.avg_length_of_stay_days else "N/A",
                    "35.2%" if kpi.contact_rate else "N/A",
                    "8.5%" if kpi.reinsertion_rate else "N/A",
                ],
            }, use_container_width=True)
    
    @staticmethod
    def render_watchlist():
        """Render adopter's watchlist."""
        st.header("❤️ My Watchlist")
        
        datastore = st.session_state.mp_datastore
        adopter_id = "adopter_001"  # Demo user
        
        if adopter_id not in datastore.watchlists or not datastore.watchlists[adopter_id]:
            st.info("Your watchlist is empty. Browse pets to add some!")
            return
        
        watchlist_ids = datastore.watchlists[adopter_id]
        watchlist_listings = [
            datastore.listings[lid] for lid in watchlist_ids
            if lid in datastore.listings
        ]
        
        st.markdown(f"### {len(watchlist_listings)} pets in your watchlist")
        
        for listing in watchlist_listings:
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"**{listing.pet_name}** - {MatchingPlatformUI.ADOPTION_SPEED_LABELS.get(listing.adoption_speed_pred, '')}")
                st.caption(f"Listed: {listing.created_at[:10]}")
            
            with col2:
                if st.button("💬 Message", key=f"msg_watch_{listing.listing_id}", use_container_width=True):
                    st.success("Message sent!")
            
            with col3:
                if st.button("🗑️ Remove", key=f"remove_{listing.listing_id}", use_container_width=True):
                    datastore.watchlists[adopter_id].remove(listing.listing_id)
                    st.rerun()


def show_matching_platform():
    """Main function for matching platform tab."""
    
    # Initialize session state
    MatchingPlatformUI.initialize_session_state()
    
    # Header
    st.markdown("""
    # 🤝 AdoptSense Marketplace
    
    **Connect rescue animals with loving homes** — two-sided platform for shelters, 
    private pet owners, and adopters. Get AI-powered predictions and recommendations 
    to find perfect matches faster.
    """)
    
    st.markdown("---")
    
    # Sidebar user selection
    user_type = MatchingPlatformUI.render_user_selector()
    st.session_state.mp_user_type = user_type
    
    # Store user type for later use
    user_label = {
        UserType.ADOPTER: "Adopter",
        UserType.SHELTER: "Shelter Manager",
        UserType.PRIVATE_HOUSEHOLD: "Private Owner",
    }[user_type]
    
    st.sidebar.markdown(f"**Current role:** {user_label}")
    st.sidebar.markdown("---")
    
    # Main navigation
    tabs = MatchingPlatformUI.render_main_navigation(user_type)
    main_tabs = st.tabs(tabs)
    
    # Render content based on user type and selected tab
    if user_type == UserType.ADOPTER:
        with main_tabs[0]:  # Browse Pets
            MatchingPlatformUI.render_listings_browser()
        
        with main_tabs[1]:  # Watchlist
            MatchingPlatformUI.render_watchlist()
        
        with main_tabs[2]:  # Messages
            st.header("💬 Messages")
            st.info("Message system coming soon! You'll be able to chat with shelters and pet owners here.")
        
        with main_tabs[3]:  # Dashboard
            st.header("📊 My Dashboard")
            st.info("Your personal adoption tracking dashboard will appear here.")
    
    elif user_type == UserType.SHELTER:
        with main_tabs[0]:  # My Listings
            MatchingPlatformUI.render_my_listings_manager()
        
        with main_tabs[1]:  # Create Listing
            MatchingPlatformUI.render_create_listing_form(user_type)
        
        with main_tabs[2]:  # KPIs
            MatchingPlatformUI.render_kpi_dashboard(user_type)
        
        with main_tabs[3]:  # Messages
            st.header("📧 Messages")
            st.info("Bulk messages and inquiries from adopters will appear here.")
    
    else:  # PRIVATE_HOUSEHOLD
        with main_tabs[0]:  # My Listings
            MatchingPlatformUI.render_my_listings_manager()
        
        with main_tabs[1]:  # Create Listing
            MatchingPlatformUI.render_create_listing_form(user_type)
        
        with main_tabs[2]:  # Analytics
            MatchingPlatformUI.render_kpi_dashboard(user_type)
        
        with main_tabs[3]:  # Watchlist
            st.header("❤️ My Watchlist")
            st.info("Save pets you're interested in to your watchlist!")
