"""
AdoptSense Pet Adoption Prediction - Frontend UI
Main Streamlit application
"""
import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Setup paths
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Page configuration
st.set_page_config(
    page_title="AdoptSense - Pet Adoption Predictor",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .css-1d6bido {
        padding: 1rem;
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 1.1em;
        padding: 0.5rem 1rem;
    }
    .streamlit-expanderHeader {
        font-size: 1.1em;
        font-weight: 600;
    }
    .predict-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    """Main application entry point."""
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🐾 AdoptSense")
        st.markdown("### Pet Adoption Speed Predictor")
    with col2:
        st.markdown("")
        st.markdown("")
        st.markdown("![Paws](https://img.icons8.com/color/96/000000/paw.png)")
    
    st.markdown("---")
    
    # Navigation
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Home",
        "📁 Batch Upload (CSV)",
        "📝 Single Pet Form",
        "ℹ️ About"
    ])
    
    with tab1:
        show_home()
    
    with tab2:
        show_csv_upload()
    
    with tab3:
        show_manual_form()
    
    with tab4:
        show_about()


def show_home():
    """Display home/landing page."""
    
    st.markdown("""
    ## Welcome to AdoptSense 👋
    
    **AdoptSense** is an AI-powered tool designed to help predict adoption speed for pets 
    and provide actionable recommendations to improve their chances of finding a loving home.
    
    ### Who is this for?
    
    - 🏥 **Animal Shelters & Rescue Organizations** - Optimize your pet listings
    - 👨‍👩‍👧 **Pet Owners** - Understand adoption prospects before rehoming
    - 💼 **Pet Adoption Businesses** - Data-driven listing optimization
    
    ### How it Works
    
    1. **Input Pet Data** - Upload a CSV with multiple pets or fill a form for a single pet
    2. **AI Analysis** - Our trained model analyzes 20+ pet characteristics
    3. **Get Predictions** - Adoption speed forecast with confidence scores
    4. **Actionable Recommendations** - Specific, prioritized improvement suggestions
    5. **Visualizations** - See rankings and trends (for batch uploads)
    
    ### Key Features
    
    - ⚡ **Real-time Predictions** - Instant adoption speed forecasts
    - 📊 **Comparative Analysis** - Compare multiple pets side-by-side
    - 🎯 **Targeted Recommendations** - Prioritized improvement suggestions
    - 📈 **Performance Ranking** - Visualize relative adoption potential
    - 📱 **User-Friendly Interface** - No coding required
    
    ### Adoption Speed Categories
    
    """)
    
    # Display adoption speed info
    col1, col2, col3, col4, col5 = st.columns(5)
    
    speed_info = [
        ("⭐⭐⭐⭐⭐", "Same Day", "Exceptional appeal"),
        ("⭐⭐⭐⭐", "1-7 Days", "Strong demand"),
        ("⭐⭐⭐", "8-30 Days", "Moderate appeal"),
        ("⭐⭐", "31-90 Days", "Needs improvement"),
        ("⭐", "No Adoption", "Critical intervention")
    ]
    
    with col1:
        with st.container(border=True):
            st.markdown("**Speed 0**")
            st.markdown(speed_info[0][0])
            st.caption(speed_info[0][1])
    
    with col2:
        with st.container(border=True):
            st.markdown("**Speed 1**")
            st.markdown(speed_info[1][0])
            st.caption(speed_info[1][1])
    
    with col3:
        with st.container(border=True):
            st.markdown("**Speed 2**")
            st.markdown(speed_info[2][0])
            st.caption(speed_info[2][1])
    
    with col4:
        with st.container(border=True):
            st.markdown("**Speed 3**")
            st.markdown(speed_info[3][0])
            st.caption(speed_info[3][1])
    
    with col5:
        with st.container(border=True):
            st.markdown("**Speed 4**")
            st.markdown(speed_info[4][0])
            st.caption(speed_info[4][1])
    
    st.markdown("---")
    
    st.markdown("""
    ### Get Started
    
    Choose one of the options above to start:
    
    - **Single Pet**: Fill in the form to analyze one pet at a time
    - **Batch Upload**: Upload a CSV file with multiple pets for comparative analysis
    
    """)


def show_csv_upload():
    """Display CSV upload page."""
    
    st.header("📁 Batch Upload (CSV)")
    
    st.markdown("""
    Upload a CSV file with multiple pets to get predictions and rankings for all of them.
    """)
    
    # Download template
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### CSV Format")
        st.info("""
        Your CSV file should include these columns:
        - **Type** (1=Dog, 2=Cat)
        - **Name** (pet name, optional)
        - **Age** (in months)
        - **Breed1, Breed2** (breed IDs)
        - **Gender** (1=Male, 2=Female, 3=Mixed)
        - **Color1, Color2, Color3** (color IDs)
        - **MaturitySize** (0=N/A, 1=Small, 2=Medium, 3=Large, 4=XL)
        - **FurLength** (0=N/A, 1=Short, 2=Medium, 3=Long)
        - **Vaccinated, Dewormed, Sterilized** (1=Yes, 2=No, 3=Not Sure)
        - **Health** (1=Healthy, 2=Minor Injury, 3=Serious Injury)
        - **Quantity** (number of pets)
        - **Fee** (adoption fee)
        - **State** (state ID)
        - **VideoAmt** (number of videos, optional)
        - **PhotoAmt** (number of photos)
        - **Description** (pet description)
        """)
    
    with col2:
        st.markdown("### Sample File")
        sample_data = {
            'Type': [2, 2, 1],
            'Name': ['Fluffy', 'Whiskers', 'Rex'],
            'Age': [12, 24, 36],
            'Breed1': [265, 285, 307],
            'Breed2': [0, 264, 0],
            'Gender': [1, 2, 1],
            'Color1': [6, 2, 1],
            'Color2': [7, 4, 5],
            'Color3': [0, 7, 0],
            'MaturitySize': [2, 2, 3],
            'FurLength': [2, 3, 1],
            'Vaccinated': [1, 1, 1],
            'Dewormed': [1, 1, 1],
            'Sterilized': [1, 2, 1],
            'Health': [1, 1, 2],
            'Quantity': [1, 1, 2],
            'Fee': [100, 0, 200],
            'State': [41326, 41326, 41312],
            'PhotoAmt': [3, 1, 2],
            'VideoAmt': [0, 0, 1],
            'Description': ['Fluffy is a friendly kitten', 'Urban rescue cat', 'Energetic dogs'],
        }
        sample_df = pd.DataFrame(sample_data)
        st.download_button(
            label="⬇️ Download Sample CSV",
            data=sample_df.to_csv(index=False),
            file_name="sample_pets.csv",
            mime="text/csv"
        )
    
    st.markdown("---")
    
    # File uploader
    uploaded_file = st.file_uploader("Upload your CSV file", type=['csv'])
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            
            st.success(f"✅ File uploaded successfully! ({len(df)} pets)")
            
            # Show preview
            with st.expander("📋 Preview Data"):
                st.dataframe(df.head(10), use_container_width=True)
            
            # Make predictions
            if st.button("🚀 Run Predictions", key="batch_predict"):
                st.markdown("---")
                
                from frontend.utils.predictions import make_prediction
                from frontend.utils.recommendations import get_adoption_factors, get_description_sentiment
                
                with st.spinner("Analyzing pets and generating predictions..."):
                    results = make_prediction(df)
                
                if results['success']:
                    predictions = results['predictions']
                    
                    # Display results
                    st.markdown("## 📊 Prediction Results")
                    
                    # Summary stats
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Pets", len(predictions))
                    with col2:
                        avg_confidence = sum(p['confidence'] for p in predictions) / len(predictions)
                        st.metric("Avg Confidence", f"{avg_confidence*100:.1f}%")
                    with col3:
                        fast_adopt = len([p for p in predictions if p['prediction'] <= 1])
                        st.metric("Fast Adopters", fast_adopt)
                    with col4:
                        slow_adopt = len([p for p in predictions if p['prediction'] >= 3])
                        st.metric("Slow Adopters", slow_adopt)
                    
                    st.markdown("---")
                    
                    # Results table
                    results_data = []
                    for pred in predictions:
                        results_data.append({
                            'Pet': pred['original_data'].get('Name', f"Pet {pred['pet_index']+1}"),
                            'Adoption Speed': pred['prediction_emoji'],
                            'Category': pred['prediction_label'],
                            'Confidence': f"{pred['confidence']*100:.1f}%",
                        })
                    
                    results_df = pd.DataFrame(results_data)
                    st.markdown("### Individual Predictions")
                    st.dataframe(results_df, use_container_width=True)
                    
                    # Detailed results
                    st.markdown("### Detailed Recommendations")
                    
                    for i, pred in enumerate(predictions):
                        pet_name = pred['original_data'].get('Name', f"Pet {i+1}")
                        
                        with st.expander(f"{pred['prediction_emoji']} {pet_name} - {pred['prediction_label']}", 
                                        expanded=i==0):
                            col1, col_sent, col2 = st.columns([1, 2, 1])

                            with col1:
                                st.markdown(f"**Confidence:** {pred['confidence']*100:.1f}%")

                            with col_sent:
                                sentiment = get_description_sentiment(
                                    pred['original_data'].get('Description', '')
                                )
                                tone_colors = {
                                    'success': '#2e7d32',
                                    'info':    '#1565c0',
                                    'warning': '#e65100',
                                    'error':   '#b71c1c',
                                }
                                bar_colors = {
                                    'success': '#4CAF50',
                                    'info':    '#90A4AE',
                                    'warning': '#FF9800',
                                    'error':   '#F44336',
                                }
                                tone_hex = tone_colors[sentiment['tone_color']]
                                pos_pct = sentiment['pos'] * 100
                                neu_pct = sentiment['neu'] * 100
                                neg_pct = sentiment['neg'] * 100
                                st.markdown(
                                    f"**Description Sentiment** — "
                                    f"<span style='color:{tone_hex}; font-weight:600;'>"
                                    f"{sentiment['tone']}  |  Score: {sentiment['compound']:+.2f}"
                                    f"</span>",
                                    unsafe_allow_html=True
                                )
                                st.markdown(f"""
<div style="font-size:13px; line-height:2;">
  <div style="display:flex; align-items:center; gap:8px;">
    <div style="width:160px; height:13px; background:#e0e0e0; border-radius:3px; overflow:hidden; flex-shrink:0;">
      <div style="width:{pos_pct:.0f}%; height:100%; background:#4CAF50;"></div>
    </div>
    <span style="color:#4CAF50; font-weight:600; min-width:70px;">Positive</span>
    <span>{pos_pct:.0f}%</span>
  </div>
  <div style="display:flex; align-items:center; gap:8px;">
    <div style="width:160px; height:13px; background:#e0e0e0; border-radius:3px; overflow:hidden; flex-shrink:0;">
      <div style="width:{neu_pct:.0f}%; height:100%; background:#90A4AE;"></div>
    </div>
    <span style="color:#607D8B; font-weight:600; min-width:70px;">Neutral</span>
    <span>{neu_pct:.0f}%</span>
  </div>
  <div style="display:flex; align-items:center; gap:8px;">
    <div style="width:160px; height:13px; background:#e0e0e0; border-radius:3px; overflow:hidden; flex-shrink:0;">
      <div style="width:{neg_pct:.0f}%; height:100%; background:#F44336;"></div>
    </div>
    <span style="color:#F44336; font-weight:600; min-width:70px;">Negative</span>
    <span>{neg_pct:.0f}%</span>
  </div>
</div>
""", unsafe_allow_html=True)
                                st.caption(sentiment['advice'])

                            with col2:
                                st.markdown(f"**Probability Breakdown:**")
                                for speed_id, prob in pred['probabilities'].items():
                                    from frontend.utils.predictions import AdoptionPredictor
                                    label = AdoptionPredictor.ADOPTION_SPEED_LABELS[speed_id]
                                    st.caption(f"Speed {speed_id} ({label}): {prob*100:.1f}%")
                            
                            st.markdown("---")

                            pos_factors, neg_factors = get_adoption_factors(pred['original_data'])

                            col_pos, col_neg = st.columns(2)

                            with col_pos:
                                st.markdown("**Top 5 Factors Helping Adoption**")
                                if pos_factors:
                                    for j, f in enumerate(pos_factors, 1):
                                        with st.container(border=True):
                                            st.markdown(f"**{j}. {f['label']}**")
                                            st.caption(f['sentence'])
                                else:
                                    st.info("No strong positive factors identified.")

                            with col_neg:
                                st.markdown("**Top 5 Factors Hindering Adoption**")
                                if neg_factors:
                                    for j, f in enumerate(neg_factors, 1):
                                        with st.container(border=True):
                                            st.markdown(f"**{j}. {f['label']}**")
                                            st.caption(f['sentence'])
                                else:
                                    st.success("No significant hindering factors found!")
                    
                    # Visualization
                    st.markdown("---")
                    st.markdown("### 📈 Rankings & Visualization")
                    
                    import plotly.graph_objects as go
                    
                    # Ranking bar chart
                    ranking_data = []
                    for pred in sorted(predictions, key=lambda x: x['prediction']):
                        ranking_data.append({
                            'name': pred['original_data'].get('Name', f"Pet {pred['pet_index']+1}"),
                            'speed': pred['prediction'],
                            'confidence': pred['confidence']
                        })
                    
                    fig = go.Figure(data=[
                        go.Bar(
                            x=[d['name'] for d in ranking_data],
                            y=[d['speed'] for d in ranking_data],
                            text=[f"Speed {d['speed']}" for d in ranking_data],
                            textposition='auto',
                            marker=dict(
                                color=[d['speed'] for d in ranking_data],
                                colorscale='RdYlGn_r',
                                showscale=True,
                                colorbar=dict(title="Adoption Speed")
                            )
                        )
                    ])
                    
                    fig.update_layout(
                        title="Pet Adoption Speed Ranking (Lower is Better)",
                        xaxis_title="Pet",
                        yaxis_title="Adoption Speed (0=Fast, 4=Slow)",
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                else:
                    st.error(f"❌ Prediction failed: {results.get('error', 'Unknown error')}")
        
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")


def show_manual_form():
    """Display manual pet form input."""
    
    st.header("📝 Single Pet Form")
    
    st.markdown("""
    Fill in the information about a single pet to get adoption speed prediction and recommendations.
    """)
    
    st.markdown("---")
    
    # Form
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🐱 Basic Information")
        
        pet_type = st.selectbox("Pet Type", options=[1, 2], format_func=lambda x: "🐶 Dog" if x == 1 else "🐱 Cat")
        name = st.text_input("Pet Name (optional)", value="")
        age = st.slider("Age (months)", min_value=0, max_value=120, value=12)
        
        st.subheader("🎨 Physical Characteristics")
        
        gender = st.selectbox("Gender", options=[1, 2, 3], format_func=lambda x: {1: "Male", 2: "Female", 3: "Mixed"}[x])
        maturity_size = st.selectbox("Maturity Size", options=[0, 1, 2, 3, 4], 
                                     format_func=lambda x: {0: "N/A", 1: "Small", 2: "Medium", 3: "Large", 4: "Extra Large"}[x])
        fur_length = st.selectbox("Fur Length", options=[0, 1, 2, 3], 
                                 format_func=lambda x: {0: "N/A", 1: "Short", 2: "Medium", 3: "Long"}[x])
        
        color1 = st.number_input("Primary Color ID", min_value=0, value=1)
        color2 = st.number_input("Secondary Color ID (optional)", min_value=0, value=0)
        color3 = st.number_input("Tertiary Color ID (optional)", min_value=0, value=0)
    
    with col2:
        st.subheader("🏥 Health & Care")
        
        health = st.selectbox("Health Status", options=[1, 2, 3], 
                            format_func=lambda x: {1: "Healthy", 2: "Minor Injury", 3: "Serious Injury"}[x])
        vaccinated = st.selectbox("Vaccinated?", options=[1, 2, 3], 
                                format_func=lambda x: {1: "Yes", 2: "No", 3: "Not Sure"}[x])
        dewormed = st.selectbox("Dewormed?", options=[1, 2, 3], 
                              format_func=lambda x: {1: "Yes", 2: "No", 3: "Not Sure"}[x])
        sterilized = st.selectbox("Sterilized?", options=[1, 2, 3], 
                                 format_func=lambda x: {1: "Yes", 2: "No", 3: "Not Sure"}[x])
        
        st.subheader("💰 Listing Information")
        
        fee = st.number_input("Adoption Fee (currency)", min_value=0, value=100)
        quantity = st.number_input("Number of Pets", min_value=1, value=1)
        state = st.number_input("State ID", min_value=0, value=41326)
    
    st.markdown("---")
    
    st.subheader("📸 Media & Description")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        photo_amt = st.number_input("Number of Photos", min_value=0, max_value=50, value=3)
    
    with col2:
        video_amt = st.number_input("Number of Videos", min_value=0, max_value=10, value=0)
    
    with col3:
        st.markdown("")
        st.markdown("")
        st.info("📌 Photos are critical - minimum 3-5 recommended")
    
    description = st.text_area("Pet Description", value="", height=150, 
                              placeholder="Describe the pet's personality, history, and characteristics...\n\n(Minimum 50 words recommended)")
    
    # Breed info
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        breed1 = st.number_input("Primary Breed ID", min_value=0, value=265)
    with col2:
        breed2 = st.number_input("Secondary Breed ID (optional)", min_value=0, value=0)
    
    st.markdown("---")
    
    # Predict button
    if st.button("🚀 Get Prediction & Recommendations", key="single_predict", type="primary"):
        
        # Create DataFrame
        pet_data = pd.DataFrame({
            'Type': [pet_type],
            'Name': [name] if name else [None],
            'Age': [age],
            'Breed1': [breed1],
            'Breed2': [breed2],
            'Gender': [gender],
            'Color1': [color1],
            'Color2': [color2],
            'Color3': [color3],
            'MaturitySize': [maturity_size],
            'FurLength': [fur_length],
            'Vaccinated': [vaccinated],
            'Dewormed': [dewormed],
            'Sterilized': [sterilized],
            'Health': [health],
            'Quantity': [quantity],
            'Fee': [fee],
            'State': [state],
            'PhotoAmt': [photo_amt],
            'VideoAmt': [video_amt],
            'Description': [description],
        })
        
        from frontend.utils.predictions import make_prediction, AdoptionPredictor
        from frontend.utils.recommendations import get_adoption_factors, get_description_sentiment
        
        with st.spinner("Analyzing pet and generating prediction..."):
            results = make_prediction(pet_data)
        
        if results['success']:
            pred = results['predictions'][0]
            
            st.markdown("---")
            st.markdown("## 🎯 Adoption Speed Prediction")
            
            # Large prediction display
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
                st.markdown(f"# {pred['prediction_emoji']}")
                st.markdown(f"### {pred['prediction_label'].upper()}")
                st.markdown(f"**Confidence:** {pred['confidence']*100:.1f}%")
                st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Probability breakdown
            st.markdown("### 📊 Prediction Probabilities")
            
            probs = pred['probabilities']
            prob_df = pd.DataFrame({
                'Adoption Speed': [AdoptionPredictor.ADOPTION_SPEED_LABELS[i] for i in range(5)],
                'Emoji': [AdoptionPredictor.ADOPTION_SPEED_EMOJI[i] for i in range(5)],
                'Probability': [f"{probs[i]*100:.1f}%" for i in range(5)]
            })
            
            st.dataframe(prob_df, use_container_width=True, hide_index=True)
            
            # Visualize probabilities
            import plotly.graph_objects as go
            
            fig = go.Figure(data=[
                go.Bar(
                    x=[f"Speed {i}" for i in range(5)],
                    y=[probs[i]*100 for i in range(5)],
                    text=[f"{probs[i]*100:.1f}%" for i in range(5)],
                    textposition='auto',
                    marker=dict(
                        color=[probs[i]*100 for i in range(5)],
                        colorscale='RdYlGn_r',
                        showscale=False
                    )
                )
            ])
            
            fig.update_layout(
                title="Adoption Speed Probability Distribution",
                xaxis_title="Adoption Speed Category",
                yaxis_title="Probability (%)",
                height=350,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")

            # Description sentiment analysis
            st.markdown("### Description Sentiment Analysis")
            sentiment = get_description_sentiment(pred['original_data'].get('Description', ''))

            tone_colors = {
                'success': '#2e7d32',
                'info':    '#1565c0',
                'warning': '#e65100',
                'error':   '#b71c1c',
            }
            tone_hex = tone_colors[sentiment['tone_color']]
            pos_pct = sentiment['pos'] * 100
            neu_pct = sentiment['neu'] * 100
            neg_pct = sentiment['neg'] * 100

            sent_col1, sent_col2 = st.columns([1, 2])
            with sent_col1:
                st.markdown(
                    f"<span style='color:{tone_hex}; font-weight:600; font-size:15px;'>"
                    f"{sentiment['tone']}  |  Score: {sentiment['compound']:+.2f}</span>",
                    unsafe_allow_html=True
                )
                st.markdown(f"""
<div style="font-size:13px; line-height:2.2; margin-top:6px;">
  <div style="display:flex; align-items:center; gap:8px;">
    <div style="width:180px; height:13px; background:#e0e0e0; border-radius:3px; overflow:hidden; flex-shrink:0;">
      <div style="width:{pos_pct:.0f}%; height:100%; background:#4CAF50;"></div>
    </div>
    <span style="color:#4CAF50; font-weight:600; min-width:70px;">Positive</span>
    <span>{pos_pct:.0f}%</span>
  </div>
  <div style="display:flex; align-items:center; gap:8px;">
    <div style="width:180px; height:13px; background:#e0e0e0; border-radius:3px; overflow:hidden; flex-shrink:0;">
      <div style="width:{neu_pct:.0f}%; height:100%; background:#90A4AE;"></div>
    </div>
    <span style="color:#607D8B; font-weight:600; min-width:70px;">Neutral</span>
    <span>{neu_pct:.0f}%</span>
  </div>
  <div style="display:flex; align-items:center; gap:8px;">
    <div style="width:180px; height:13px; background:#e0e0e0; border-radius:3px; overflow:hidden; flex-shrink:0;">
      <div style="width:{neg_pct:.0f}%; height:100%; background:#F44336;"></div>
    </div>
    <span style="color:#F44336; font-weight:600; min-width:70px;">Negative</span>
    <span>{neg_pct:.0f}%</span>
  </div>
</div>
""", unsafe_allow_html=True)
            with sent_col2:
                st.markdown("")
                st.markdown("")
                st.info(sentiment['advice'])

            st.markdown("---")

            # Adoption factor analysis
            st.markdown("## Adoption Factor Analysis")

            positive_factors, negative_factors = get_adoption_factors(pred['original_data'])

            col_pos, col_neg = st.columns(2)

            with col_pos:
                st.markdown("### Top 5 Factors Helping Adoption")
                if positive_factors:
                    for i, factor in enumerate(positive_factors, 1):
                        with st.container(border=True):
                            st.markdown(f"**{i}. {factor['label']}**")
                            st.caption(factor['sentence'])
                else:
                    st.info("No strong positive factors identified for this pet.")

            with col_neg:
                st.markdown("### Top 5 Factors Hindering Adoption")
                if negative_factors:
                    for i, factor in enumerate(negative_factors, 1):
                        with st.container(border=True):
                            st.markdown(f"**{i}. {factor['label']}**")
                            st.caption(factor['sentence'])
                else:
                    st.success("No significant hindering factors found — great profile!")
        
        else:
            st.error(f"❌ Prediction failed: {results.get('error', 'Unknown error')}")


def show_about():
    """Display about page."""
    
    st.header("ℹ️ About AdoptSense")
    
    st.markdown("""
    ## Project Overview
    
    **AdoptSense** is an intelligent adoption speed prediction system powered by machine learning.
    It analyzes pet characteristics and listing quality to predict how quickly a pet will be adopted.
    
    ### Model Information
    
    - **Model Type:** XGBoost Gradient Boosting Classifier
    - **Training Data:** Petfinder dataset (15,000+ pets)
    - **Features:** 20+ behavioral, physical, and listing characteristics
    - **Accuracy:** Validated on real-world adoption patterns
    - **Metric:** Multi-class classification with class balancing
    
    ### Key Features Analyzed
    
    - 📸 **Photos** - Most critical factor for adoption speed
    - ✍️ **Description Quality** - Sentiment and length matter
    - 🐕 **Pet Characteristics** - Age, breed, size, health
    - 💰 **Pricing** - Adoption fees impact speed
    - 🏥 **Health Status** - Vaccinations, sterilization, injuries
    - 📍 **Geographic Location** - Regional adoption patterns
    
    ### Development Stack
    
    - **Backend:** Python, scikit-learn, XGBoost
    - **Feature Engineering:** Custom tabular and sentiment analysis
    - **Frontend:** Streamlit for interactive UI
    - **Data:** Pandas, NumPy for data processing
    
    ### How to Use
    
    1. **Home Tab** - Get started and understand adoption speed categories
    2. **Batch Upload** - Upload CSV with multiple pets for comparative analysis
    3. **Single Pet Form** - Fill a form for individual pet analysis
    4. **Get Recommendations** - Receive actionable improvement suggestions
    
    ### Recommendations Categories
    
    - **Photography Campaign** - Add 3-5 high-quality photos (CRITICAL)
    - **Description Enhancement** - More detailed, emotion-focused descriptions
    - **Pricing Strategy** - Consider free/reduced-fee adoptions
    - **Age-Targeted Outreach** - Market differently by age group
    - **Health Transparency** - Clearly communicate health status
    - **Sterilization Strategy** - Market sterilization benefits
    
    ### Model Insights
    
    The model reveals several important patterns:
    
    - 🎯 **No photos = 60%+ slow adoption** - Photos are the strongest single factor
    - ⏱️ **Age is crucial** - Puppies/kittens adopt fastest, older pets slower
    - 💵 **Price is a barrier** - Free adoptions significantly faster than paid
    - 📝 **Description matters** - Quality descriptions accelerate adoption
    - 🏥 **Health impacts adoption** - Healthy pets adopt 2-3x faster
    - 🌍 **Geographic variation** - Strong regional adoption patterns
    
    ### Future Enhancements
    
    - Image quality/aesthetic scoring using CNNs
    - Sentiment analysis for descriptions
    - Time-series modeling for seasonality
    - Regional strategy optimization
    - Social media impact analysis
    
    ### Data Privacy
    
    - All predictions are made locally
    - No pet data is stored on servers
    - Processing happens in your browser/local machine
    
    ### Contact & Support
    
    For questions, suggestions, or issues:
    - 📧 Email: support@adoptsense.com
    - 💬 GitHub: [AdoptSense Repository]
    - 🐾 Website: www.adoptsense.com
    
    ---
    
    **Version:** 1.0.0  
    **Last Updated:** February 2026
    """)


if __name__ == "__main__":
    main()
