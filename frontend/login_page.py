"""
Sage - AI Health Assistant
Login Page with Glassmorphism Design
"""

import streamlit as st

st.set_page_config(
    page_title="Sage - Login",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Hide Streamlit elements */
    #MainMenu, footer, header, .stDeployButton {display: none !important;}
    section[data-testid="stSidebar"] {display: none !important;}
    .block-container {padding-top: 0 !important;}
    
    /* Background */
    .stApp {
        background: linear-gradient(135deg, #d4f1ed 0%, #e0f7f4 30%, #d8f3ef 60%, #c8ece6 100%);
        min-height: 100vh;
    }
    
    /* Glass card effect for the form container */
    [data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.35) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
        border-radius: 24px !important;
        padding: 40px 35px !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Input fields - glass style */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.6) !important;
        border-radius: 30px !important;
        padding: 15px 22px !important;
        font-size: 0.95rem !important;
        color: #2c4a4a !important;
        font-family: 'Poppins', sans-serif !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #3dbda7 !important;
        box-shadow: 0 0 0 3px rgba(61, 189, 167, 0.15) !important;
        background: rgba(255, 255, 255, 0.7) !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #6b9a9a !important;
    }
    
    /* Hide input labels */
    .stTextInput > label {
        display: none !important;
    }
    
    /* Login button */
    .stFormSubmitButton > button {
        background: linear-gradient(135deg, #7c4d6e 0%, #9b5a7c 100%) !important;
        border: none !important;
        border-radius: 30px !important;
        padding: 15px 20px !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        color: white !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        width: 100% !important;
        margin-top: 10px !important;
        transition: all 0.3s ease !important;
    }
    
    .stFormSubmitButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(124, 77, 110, 0.4) !important;
    }
    
    /* Regular button (Google) */
    .stButton > button {
        background: rgba(255, 255, 255, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.7) !important;
        border-radius: 30px !important;
        padding: 12px 20px !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        color: #333 !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background: rgba(255, 255, 255, 0.85) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Links styling */
    a {
        color: #5a8a8a !important;
        text-decoration: none !important;
    }
    
    a:hover {
        color: #3dbda7 !important;
    }
</style>
""", unsafe_allow_html=True)

# Add vertical spacing
st.markdown("<br><br><br>", unsafe_allow_html=True)

# Layout - center the form
col1, col2, col3 = st.columns([1.2, 1, 1.2])

with col2:
    # Logo and branding
    st.markdown("""
    <div style="text-align: center; margin-bottom: 5px;">
        <div style="display: inline-flex; align-items: center; gap: 8px;">
            <span style="font-size: 2.2rem; color: #3dbda7;">✚</span>
            <span style="font-size: 2rem; font-weight: 600; color: #2c5f5f;">sage</span>
        </div>
        <div style="font-size: 0.7rem; color: #5a9a9a; letter-spacing: 1px; margin-top: -5px;">
            Healthcare Chatbot System
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Welcome title
    st.markdown("""
    <h1 style="text-align: center; font-size: 1.8rem; font-weight: 500; color: #2c4a4a; margin: 25px 0 30px 0;">
        Welcome
    </h1>
    """, unsafe_allow_html=True)
    
    # Login form
    with st.form("login_form", clear_on_submit=False):
        email = st.text_input("Email", placeholder="Email", label_visibility="collapsed")
        password = st.text_input("Password", placeholder="Password", type="password", label_visibility="collapsed")
        
        login_submitted = st.form_submit_button("LOGIN", use_container_width=True)
        
        if login_submitted:
            if email and password:
                st.session_state['logged_in'] = True
                st.success("✓ Login successful!")
            else:
                st.warning("Please enter email and password")
    
    # Links row
    link_col1, link_col2 = st.columns(2)
    with link_col1:
        st.markdown("<p style='font-size: 0.85rem;'><a href='#'>Forgot Password?</a></p>", unsafe_allow_html=True)
    with link_col2:
        st.markdown("<p style='font-size: 0.85rem; text-align: right;'><a href='#'>Sign Up</a></p>", unsafe_allow_html=True)
    
    # Divider
    st.markdown("""
    <div style="display: flex; align-items: center; margin: 15px 0; color: #6b9a9a; font-size: 0.8rem;">
        <div style="flex: 1; height: 1px; background: rgba(107, 154, 154, 0.4);"></div>
        <span style="padding: 0 15px; font-weight: 500;">OR LOGIN WITH</span>
        <div style="flex: 1; height: 1px; background: rgba(107, 154, 154, 0.4);"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Google login button
    if st.button("G  Continue with Google", use_container_width=True):
        st.info("Google OAuth will redirect to backend")