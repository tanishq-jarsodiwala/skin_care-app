import streamlit as st
import requests
import json
from PIL import Image
import io
import base64
import time

# Configure Streamlit page
st.set_page_config(
    page_title="AI Skincare Recommendation System",
    page_icon="🧴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #FF6B6B;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    .sub-header {
        text-align: center;
        color: #4ECDC4;
        font-size: 1.2rem;
        margin-bottom: 3rem;
    }
    .recommendation-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 20px 0;
    }
    .analysis-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 20px 0;
    }
    .success-box {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 20px 0;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: bold;
        width: 100%;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
    }
</style>
""", unsafe_allow_html=True)

# Backend API configuration
API_BASE_URL = "http://localhost:8000"

def check_backend_connection():
    """Check if backend is running"""
    try:
        response = requests.get(f"http://localhost:8000", timeout=5)
        return response.status_code == 200
    except:
        return False

def call_recommendation_api(image_file, goal, history):
    """Call the FastAPI backend for recommendations"""
    try:
        # Prepare the files and data
        files = {
            'image': (image_file.name, image_file.getvalue(), image_file.type)
        }
        
        data = {
            'goal': goal,
            'history': history
        }
        
        # Make API call
        response = requests.post(
            f"{API_BASE_URL}/recommend",
            files=files,
            data=data,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"API Error: {response.status_code} - {response.text}"
            
    except requests.exceptions.ConnectionError:
        return None, "Backend server is not running. Please start the FastAPI server first."
    except requests.exceptions.Timeout:
        return None, "Request timed out. Please try again."
    except Exception as e:
        return None, f"Error: {str(e)}"

def display_results(result):
    """Display the API results in a nice format"""
    
    # Analysis Results
    st.markdown('<div class="analysis-box">', unsafe_allow_html=True)
    st.markdown("### 📊 Image Analysis Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Brightness Score",
            value=f"{result['analysis']['brightness_score']}/255",
            delta=None
        )
    
    with col2:
        st.metric(
            label="Brightness Level",
            value=result['analysis']['brightness_level'],
            delta=None
        )
    
    with col3:
        st.metric(
            label="Processing Status",
            value="✅ Success" if result['analysis']['image_processed'] else "❌ Failed",
            delta=None
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Recommendations
    st.markdown('<div class="recommendation-box">', unsafe_allow_html=True)
    st.markdown("### 💡 AI-Powered Skincare Recommendations")
    
    recommendation = result['recommendation']
    
    if isinstance(recommendation, dict):
        # Structured recommendation
        if 'routine' in recommendation:
            st.markdown(f"**🔄 Recommended Routine:**")
            st.write(recommendation['routine'])
        
        if 'key_ingredients' in recommendation:
            st.markdown(f"**🧪 Key Ingredients to Look For:**")
            st.write(recommendation['key_ingredients'])
        
        if 'avoid' in recommendation:
            st.markdown(f"**⚠️ Products/Ingredients to Avoid:**")
            st.write(recommendation['avoid'])
        
        if 'timeline' in recommendation:
            st.markdown(f"**⏰ Expected Timeline:**")
            st.write(recommendation['timeline'])
        
        if 'recommendation' in recommendation:
            st.markdown(f"**📝 AI Generated Advice:**")
            st.write(recommendation['recommendation'])
    else:
        # Simple text recommendation
        st.write(recommendation)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Additional Info
    st.markdown('<div class="success-box">', unsafe_allow_html=True)
    st.markdown("### 🔗 Additional Resources")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Your Input Summary:**")
        st.write(f"**Goal:** {result['user_input']['goal']}")
        st.write(f"**History:** {result['user_input']['history']}")
    
    with col2:
        st.markdown("**Recommended Products:**")
        if 'mock_collection_link' in result:
            st.markdown(f"[View Recommended Products Collection]({result['mock_collection_link']})")
        
        st.markdown("**📱 Save these recommendations for your skincare journey!**")
    
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🧴 AI Skincare Recommendation System</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Get personalized skincare advice powered by AI and advanced image analysis</p>', unsafe_allow_html=True)
    
    # Check backend connection
    if not check_backend_connection():
        st.error("🚨 **Backend Server Not Running!**")
        st.warning("Please start the FastAPI server first:")
        st.code("python main.py", language="bash")
        st.info("The server should be running on http://localhost:8000")
        st.stop()
    else:
        st.success("✅ Backend server is connected!")
    
    # Sidebar for instructions
    with st.sidebar:
        st.markdown("### 📋 How to Use")
        st.markdown("""
        1. **Upload Your Photo** - Clear face image works best
        2. **Set Your Goal** - What do you want to achieve?
        3. **Add Your History** - Products you've used before
        4. **Get Recommendations** - AI will analyze and suggest
        """)
        
        st.markdown("### 💡 Tips")
        st.markdown("""
        - Use natural lighting for photos
        - Be specific about your skincare goals
        - Include brand names in product history
        - Consider allergies and skin sensitivity
        """)
        
        st.markdown("### 🎯 Popular Goals")
        goals = [
            "Brightening", "Anti-aging", "Acne treatment", 
            "Hydration", "Oil control", "Sensitive skin care"
        ]
        for goal in goals:
            if st.button(f"💡 {goal}", key=f"goal_{goal}"):
                st.session_state.selected_goal = goal
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📸 Upload Your Photo")
        uploaded_file = st.file_uploader(
            "Choose a clear face image",
            type=['png', 'jpg', 'jpeg'],
            help="Upload a clear photo of your face for skin analysis"
        )
        
        if uploaded_file is not None:
            # Display uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_container_width=True)
            
            # Image info
            st.info(f"📏 Image size: {image.size[0]}x{image.size[1]} pixels")
    
    with col2:
        st.markdown("### 🎯 Your Skincare Goals")
        
        # Goal input
        goal_input = st.text_input(
            "What's your main skincare goal?",
            value=st.session_state.get('selected_goal', ''),
            placeholder="e.g., brightening, anti-aging, acne treatment",
            help="Be specific about what you want to achieve"
        )
        
        # History input
        history_input = st.text_area(
            "Previous skincare products used:",
            placeholder="e.g., Vitamin C serum, Niacinamide, Retinol cream, CeraVe cleanser",
            help="List products you've used before, including brands if possible",
            height=100
        )
        
        # Additional options
        st.markdown("### ⚙️ Additional Options")
        
        skin_type = st.selectbox(
            "Skin Type (optional)",
            ["Not specified", "Oily", "Dry", "Combination", "Sensitive", "Normal"]
        )
        
        if skin_type != "Not specified":
            history_input += f" | Skin Type: {skin_type}"
        
        age_range = st.selectbox(
            "Age Range (optional)",
            ["Not specified", "Under 20", "20-30", "30-40", "40-50", "50+"]
        )
        
        if age_range != "Not specified":
            history_input += f" | Age: {age_range}"
    
    # Submit button
    st.markdown("---")
    
    if st.button("🚀 Get AI Skincare Recommendations", type="primary", use_container_width=True):
        
        # Validation
        if uploaded_file is None:
            st.error("❌ Please upload an image first!")
            return
        
        if not goal_input.strip():
            st.error("❌ Please enter your skincare goal!")
            return
        
        if not history_input.strip():
            st.warning("⚠️ Adding product history will improve recommendations!")
        
        # Show loading
        with st.spinner("🔄 Analyzing your image and generating recommendations..."):
            # Simulate processing time
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
            
            # Call API
            result, error = call_recommendation_api(uploaded_file, goal_input, history_input)
        
        # Clear progress bar
        progress_bar.empty()
        
        if error:
            st.error(f"❌ {error}")
        elif result:
            st.success("✅ Analysis complete!")
            display_results(result)
            
            # Download results option
            if st.button("📥 Download Results as JSON"):
                st.download_button(
                    label="Download Recommendations",
                    data=json.dumps(result, indent=2),
                    file_name=f"skincare_recommendations_{int(time.time())}.json",
                    mime="application/json"
                )
        else:
            st.error("❌ Unexpected error occurred. Please try again.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; padding: 20px;'>"
        "💡 This is an AI-powered tool for educational purposes. "
        "Always consult with a dermatologist for serious skin concerns."
        "</div>",
        unsafe_allow_html=True
    )

# Sample data for testing
def show_sample_data():
    st.markdown("### 🧪 Sample Test Data")
    
    with st.expander("Click to see sample inputs for testing"):
        st.markdown("**Sample Goals:**")
        st.code("""
        - "brightening and evening skin tone"
        - "anti-aging and wrinkle reduction"
        - "acne treatment and oil control"
        - "hydration for dry skin"
        - "sensitive skin care routine"
        """)
        
        st.markdown("**Sample Product History:**")
        st.code("""
        - "Vitamin C serum, Niacinamide 10%, CeraVe Hydrating Cleanser, Neutrogena SPF 30"
        - "Retinol cream, Hyaluronic acid serum, The Ordinary products"
        - "Salicylic acid cleanser, Benzoyl peroxide, Tea tree oil treatments"
        """)

# Initialize session state
if 'selected_goal' not in st.session_state:
    st.session_state.selected_goal = ''

# Run the main app
main()

# Show sample data in sidebar
with st.sidebar:
    st.markdown("---")
    show_sample_data()