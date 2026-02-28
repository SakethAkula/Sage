"""
Sage - AI Health Assistant
Premium Frontend with Glassmorphism Design
"""

import streamlit as st
import requests
import time
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai_engine import SageAI

# Configuration
BACKEND_URL = "http://localhost:5000"

st.set_page_config(
    page_title="Sage - AI Health Assistant",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Premium CSS - Glassmorphism Design
st.markdown("""
<style>
    /* ===== IMPORTS & VARIABLES ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --bg-primary: #0f0f1a;
        --bg-secondary: #1a1a2e;
        --bg-glass: rgba(255, 255, 255, 0.1);
        --bg-glass-dark: rgba(0, 0, 0, 0.2);
        --text-primary: #ffffff;
        --text-secondary: rgba(255, 255, 255, 0.7);
        --text-muted: rgba(255, 255, 255, 0.5);
        --accent: #4ade80;
        --accent-secondary: #22d3ee;
        --border-glass: rgba(255, 255, 255, 0.2);
        --shadow-glass: 0 8px 32px rgba(0, 0, 0, 0.3);
        --radius: 16px;
        --radius-lg: 24px;
        --transition: 0.3s ease;
    }

    /* ===== GLOBAL RESET ===== */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    .main {
        background: var(--bg-primary);
    }
    
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    
    /* Hide Streamlit elements */
    #MainMenu, footer, header, .stDeployButton {
        display: none !important;
    }
    
    section[data-testid="stSidebar"] {
        display: none;
    }
    
    /* Hide sidebar toggle */
    button[kind="header"] {
        display: none !important;
    }

    /* ===== ANIMATIONS ===== */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    @keyframes gradientMove {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }

    /* ===== LOGIN PAGE ===== */
    .login-wrapper {
        min-height: 100vh;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        background-size: 400% 400%;
        animation: gradientMove 15s ease infinite;
        position: relative;
        overflow: hidden;
    }
    
    .login-wrapper::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            radial-gradient(circle at 20% 80%, rgba(74, 222, 128, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(34, 211, 238, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 40% 40%, rgba(139, 92, 246, 0.1) 0%, transparent 40%);
        pointer-events: none;
    }
    
    /* Floating particles */
    .particles {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        overflow: hidden;
        pointer-events: none;
    }
    
    .particle {
        position: absolute;
        width: 4px;
        height: 4px;
        background: rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        animation: float 6s ease-in-out infinite;
    }
    
    .login-container {
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 40px 20px;
        position: relative;
        z-index: 10;
    }
    
    .login-card {
        background: var(--bg-glass);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid var(--border-glass);
        border-radius: var(--radius-lg);
        padding: 48px 40px;
        width: 100%;
        max-width: 420px;
        box-shadow: var(--shadow-glass);
        animation: fadeInUp 0.6s ease;
    }
    
    .login-logo {
        width: 70px;
        height: 70px;
        background: linear-gradient(135deg, var(--accent) 0%, var(--accent-secondary) 100%);
        border-radius: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        margin: 0 auto 24px auto;
        box-shadow: 0 8px 24px rgba(74, 222, 128, 0.3);
        animation: float 3s ease-in-out infinite;
    }
    
    .login-title {
        font-size: 2rem;
        font-weight: 600;
        color: var(--text-primary);
        text-align: center;
        margin-bottom: 8px;
    }
    
    .login-subtitle {
        font-size: 0.95rem;
        color: var(--text-secondary);
        text-align: center;
        margin-bottom: 32px;
        line-height: 1.5;
    }
    
    .google-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
        width: 100%;
        padding: 16px 24px;
        background: rgba(255, 255, 255, 0.95);
        border: none;
        border-radius: var(--radius);
        font-size: 1rem;
        font-weight: 500;
        color: #333;
        cursor: pointer;
        transition: all var(--transition);
        text-decoration: none;
        margin-bottom: 24px;
    }
    
    .google-btn:hover {
        background: #ffffff;
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(255, 255, 255, 0.2);
    }
    
    .divider {
        display: flex;
        align-items: center;
        margin: 24px 0;
        color: var(--text-muted);
        font-size: 0.85rem;
    }
    
    .divider::before, .divider::after {
        content: '';
        flex: 1;
        height: 1px;
        background: var(--border-glass);
    }
    
    .divider span {
        padding: 0 16px;
    }
    
    .features-row {
        display: flex;
        justify-content: center;
        gap: 32px;
        margin-top: 32px;
        padding-top: 24px;
        border-top: 1px solid var(--border-glass);
    }
    
    .feature-item {
        text-align: center;
    }
    
    .feature-icon {
        font-size: 1.5rem;
        margin-bottom: 8px;
    }
    
    .feature-text {
        font-size: 0.75rem;
        color: var(--text-muted);
    }

    /* ===== ONBOARDING PAGE ===== */
    .onboarding-wrapper {
        min-height: 100vh;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
    }
    
    .onboarding-card {
        background: var(--bg-glass);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid var(--border-glass);
        border-radius: var(--radius-lg);
        padding: 32px 40px;
        width: 100%;
        max-width: 600px;
        box-shadow: var(--shadow-glass);
        animation: fadeInUp 0.5s ease;
    }
    
    .onboarding-header {
        text-align: center;
        margin-bottom: 24px;
    }
    
    .onboarding-header h2 {
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0 0 8px 0;
    }
    
    .onboarding-header p {
        font-size: 0.9rem;
        color: var(--text-secondary);
        margin: 0;
    }

    /* ===== CHAT PAGE ===== */
    .chat-wrapper {
        min-height: 100vh;
        background: var(--bg-primary);
        display: flex;
        flex-direction: column;
    }
    
    .chat-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px 32px;
        background: var(--bg-secondary);
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    
    .chat-header-left {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .chat-logo {
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, var(--accent) 0%, var(--accent-secondary) 100%);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
    }
    
    .chat-brand {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-primary);
    }
    
    .user-avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--accent) 0%, var(--accent-secondary) 100%);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .chat-main {
        flex: 1;
        display: flex;
        flex-direction: column;
        max-width: 800px;
        margin: 0 auto;
        width: 100%;
        padding: 24px;
    }
    
    .chat-welcome {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 40px 20px;
        animation: fadeInUp 0.6s ease;
    }
    
    .welcome-icon {
        font-size: 4rem;
        margin-bottom: 24px;
        animation: float 3s ease-in-out infinite;
    }
    
    .welcome-title {
        font-size: 2.5rem;
        font-weight: 300;
        color: var(--text-primary);
        margin-bottom: 16px;
    }
    
    .welcome-subtitle {
        font-size: 1rem;
        color: var(--text-secondary);
        max-width: 450px;
        line-height: 1.6;
    }
    
    /* Messages */
    .chat-messages {
        flex: 1;
        padding: 24px 0;
        overflow-y: auto;
    }
    
    .message {
        display: flex;
        gap: 12px;
        margin-bottom: 20px;
        animation: slideIn 0.3s ease;
    }
    
    .message.user {
        flex-direction: row-reverse;
    }
    
    .message-avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        flex-shrink: 0;
    }
    
    .message-avatar.sage {
        background: linear-gradient(135deg, var(--accent) 0%, var(--accent-secondary) 100%);
        color: white;
    }
    
    .message-avatar.user {
        background: rgba(255,255,255,0.2);
        color: white;
    }
    
    .message-content {
        max-width: 70%;
        padding: 14px 18px;
        border-radius: var(--radius);
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    .message.sage .message-content {
        background: var(--bg-glass);
        color: var(--text-primary);
        border: 1px solid var(--border-glass);
        border-bottom-left-radius: 4px;
    }
    
    .message.user .message-content {
        background: linear-gradient(135deg, var(--accent) 0%, var(--accent-secondary) 100%);
        color: #0f0f1a;
        border-bottom-right-radius: 4px;
    }
    
    /* Typing indicator */
    .typing-indicator {
        display: flex;
        gap: 6px;
        padding: 16px 20px;
        background: var(--bg-glass);
        border: 1px solid var(--border-glass);
        border-radius: var(--radius);
        border-bottom-left-radius: 4px;
        width: fit-content;
    }
    
    .typing-dot {
        width: 8px;
        height: 8px;
        background: var(--accent);
        border-radius: 50%;
        animation: pulse 1.4s infinite;
    }
    
    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }
    
    /* Quick suggestions */
    .suggestions {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        justify-content: center;
        margin-top: 24px;
    }
    
    .suggestion-chip {
        background: var(--bg-glass);
        border: 1px solid var(--border-glass);
        border-radius: 20px;
        padding: 10px 18px;
        font-size: 0.85rem;
        color: var(--text-secondary);
        cursor: pointer;
        transition: all var(--transition);
    }
    
    .suggestion-chip:hover {
        background: rgba(74, 222, 128, 0.2);
        border-color: var(--accent);
        color: var(--accent);
    }
    
    /* Disclaimer */
    .disclaimer {
        background: rgba(251, 191, 36, 0.1);
        border-left: 3px solid #fbbf24;
        padding: 12px 16px;
        border-radius: 0 var(--radius) var(--radius) 0;
        margin: 16px 0;
        font-size: 0.8rem;
        color: #fbbf24;
    }

    /* ===== STREAMLIT OVERRIDES ===== */
    .stTextInput > div > div > input {
        background: var(--bg-glass) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: var(--radius) !important;
        color: var(--text-primary) !important;
        padding: 14px 16px !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 2px rgba(74, 222, 128, 0.2) !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: var(--text-muted) !important;
    }
    
    .stSelectbox > div > div {
        background: var(--bg-glass) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: var(--radius) !important;
    }
    
    .stSelectbox > div > div > div {
        color: var(--text-primary) !important;
    }
    
    .stDateInput > div > div > input {
        background: var(--bg-glass) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: var(--radius) !important;
        color: var(--text-primary) !important;
    }
    
    .stCheckbox > label {
        color: var(--text-secondary) !important;
    }
    
    .stCheckbox > label > span {
        color: var(--text-secondary) !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, var(--accent) 0%, var(--accent-secondary) 100%) !important;
        color: #0f0f1a !important;
        border: none !important;
        border-radius: var(--radius) !important;
        padding: 14px 28px !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all var(--transition) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(74, 222, 128, 0.3) !important;
    }
    
    /* Form labels */
    .stTextInput > label, .stSelectbox > label, .stDateInput > label {
        color: var(--text-secondary) !important;
        font-size: 0.85rem !important;
    }
    
    /* Chat input */
    .stChatInput {
        background: var(--bg-glass) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: var(--radius) !important;
    }
    
    .stChatInput > div {
        background: transparent !important;
    }
    
    textarea {
        color: var(--text-primary) !important;
    }

    /* ===== API KEY PAGE ===== */
    .api-wrapper {
        min-height: 100vh;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
    }
    
    .api-card {
        background: var(--bg-glass);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid var(--border-glass);
        border-radius: var(--radius-lg);
        padding: 40px;
        width: 100%;
        max-width: 450px;
        box-shadow: var(--shadow-glass);
        text-align: center;
        animation: fadeInUp 0.5s ease;
    }
    
    .api-icon {
        font-size: 3rem;
        margin-bottom: 20px;
    }
    
    .api-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 8px;
    }
    
    .api-subtitle {
        font-size: 0.9rem;
        color: var(--text-secondary);
        margin-bottom: 24px;
    }
    
    .api-link {
        color: var(--accent) !important;
        text-decoration: none;
    }
    
    .api-link:hover {
        text-decoration: underline;
    }

    /* ===== RESPONSIVE ===== */
    @media (max-width: 768px) {
        .login-card, .onboarding-card, .api-card {
            padding: 32px 24px;
            margin: 16px;
        }
        
        .features-row {
            gap: 16px;
        }
        
        .message-content {
            max-width: 85%;
        }
        
        .chat-header {
            padding: 12px 16px;
        }
        
        .chat-main {
            padding: 16px;
        }
    }
</style>
""", unsafe_allow_html=True)


# ============== SESSION MANAGEMENT ==============

def init_session():
    """Initialize session state."""
    defaults = {
        'authenticated': False,
        'user': None,
        'profile': None,
        'profile_complete': False,
        'messages': [],
        'ai_engine': None,
        'show_splash': True,
        'api_key': None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ============== SCREENS ==============

def show_splash():
    """Display splash screen."""
    st.markdown("""
        <div style="min-height: 100vh; background: #0f0f1a; display: flex; flex-direction: column; align-items: center; justify-content: center;">
            <div style="width: 80px; height: 80px; background: linear-gradient(135deg, #4ade80 0%, #22d3ee 100%); border-radius: 20px; display: flex; align-items: center; justify-content: center; font-size: 2.5rem; animation: pulse 2s infinite;">🌿</div>
            <div style="margin-top: 24px; font-size: 1.5rem; font-weight: 600; color: white;">Sage</div>
        </div>
    """, unsafe_allow_html=True)
    time.sleep(1.5)
    st.session_state.show_splash = False
    st.rerun()


def show_login():
    """Display glassmorphism login screen."""
    
    # Add custom CSS for login
    st.markdown("""
    <style>
        .login-page {
            min-height: 100vh;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 40px 20px;
        }
        .login-box {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 24px;
            padding: 48px 40px;
            width: 100%;
            max-width: 400px;
            text-align: center;
        }
        .login-box .logo {
            width: 70px;
            height: 70px;
            background: linear-gradient(135deg, #4ade80 0%, #22d3ee 100%);
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            margin: 0 auto 24px auto;
        }
        .login-box h1 {
            font-size: 2rem;
            font-weight: 600;
            color: white;
            margin-bottom: 8px;
        }
        .login-box p {
            font-size: 0.95rem;
            color: rgba(255,255,255,0.7);
            margin-bottom: 32px;
            line-height: 1.5;
        }
        .g-btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            width: 100%;
            padding: 16px 24px;
            background: white;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 500;
            color: #333;
            text-decoration: none;
        }
        .g-btn:hover {
            background: #f5f5f5;
        }
        .feat-row {
            display: flex;
            justify-content: center;
            gap: 32px;
            margin-top: 32px;
            padding-top: 24px;
            border-top: 1px solid rgba(255,255,255,0.2);
        }
        .feat-item {
            text-align: center;
        }
        .feat-item .icon {
            font-size: 1.5rem;
            margin-bottom: 8px;
        }
        .feat-item .text {
            font-size: 0.75rem;
            color: rgba(255,255,255,0.5);
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Center content
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 60px 0;">
            <div style="width: 70px; height: 70px; background: linear-gradient(135deg, #4ade80 0%, #22d3ee 100%); border-radius: 20px; display: flex; align-items: center; justify-content: center; font-size: 2rem; margin: 0 auto 24px auto;">🌿</div>
            <h1 style="font-size: 2rem; font-weight: 600; color: white; margin-bottom: 8px;">Welcome</h1>
            <p style="font-size: 0.95rem; color: rgba(255,255,255,0.7); margin-bottom: 32px; line-height: 1.5;">Your personal AI health assistant.<br>Get guidance on symptoms, remedies, and care.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Google login button using Streamlit
        if st.button("🔵 Continue with Google", use_container_width=True, type="primary"):
            # Redirect to backend login
            st.markdown(f'<meta http-equiv="refresh" content="0;url={BACKEND_URL}/login">', unsafe_allow_html=True)
        
        st.markdown("""
        <div style="display: flex; justify-content: center; gap: 40px; margin-top: 48px; padding-top: 24px; border-top: 1px solid rgba(255,255,255,0.2);">
            <div style="text-align: center;">
                <div style="font-size: 1.5rem; margin-bottom: 8px;">🔍</div>
                <div style="font-size: 0.75rem; color: rgba(255,255,255,0.5);">Symptom<br>Analysis</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 1.5rem; margin-bottom: 8px;">💊</div>
                <div style="font-size: 0.75rem; color: rgba(255,255,255,0.5);">Home<br>Remedies</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 1.5rem; margin-bottom: 8px;">🏥</div>
                <div style="font-size: 0.75rem; color: rgba(255,255,255,0.5);">Doctor<br>Guidance</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def show_onboarding():
    """Display compact onboarding form."""
    
    st.markdown("""
        <div class="onboarding-wrapper">
            <div class="onboarding-card">
                <div class="onboarding-header">
                    <h2>🌿 Personalize Your Experience</h2>
                    <p>Help Sage provide better health guidance</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Use columns to create compact layout
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        with st.form("onboarding_form"):
            # Row 1: Name
            name = st.text_input("Full Name", placeholder="Enter your name")
            
            # Row 2: Sex and DOB side by side
            c1, c2 = st.columns(2)
            with c1:
                sex = st.selectbox("Sex", ["Select...", "Male", "Female", "Other"])
            with c2:
                dob = st.date_input("Date of Birth", value=datetime(2000, 1, 1))
            
            # Row 3: Health conditions (compact)
            st.markdown("**Health Conditions** (if any)")
            cc1, cc2, cc3, cc4 = st.columns(4)
            with cc1:
                c_diabetes = st.checkbox("Diabetes")
                c_asthma = st.checkbox("Asthma")
            with cc2:
                c_bp = st.checkbox("Hypertension")
                c_heart = st.checkbox("Heart Disease")
            with cc3:
                c_thyroid = st.checkbox("Thyroid")
                c_arthritis = st.checkbox("Arthritis")
            with cc4:
                c_allergies = st.checkbox("Allergies")
                c_other = st.checkbox("Other")
            
            # Row 4: Allergies and Medications
            c1, c2 = st.columns(2)
            with c1:
                allergies = st.text_input("Known Allergies", placeholder="e.g., Penicillin")
            with c2:
                medications = st.text_input("Current Medications", placeholder="e.g., Aspirin")
            
            # Submit
            submitted = st.form_submit_button("Continue to Sage →", use_container_width=True)
            
            if submitted:
                if not name or sex == "Select...":
                    st.error("Please enter your name and select sex")
                else:
                    conditions = []
                    if c_diabetes: conditions.append("Diabetes")
                    if c_bp: conditions.append("Hypertension")
                    if c_asthma: conditions.append("Asthma")
                    if c_heart: conditions.append("Heart Disease")
                    if c_thyroid: conditions.append("Thyroid")
                    if c_arthritis: conditions.append("Arthritis")
                    if c_allergies: conditions.append("Allergies")
                    if c_other: conditions.append("Other")
                    
                    today = datetime.today()
                    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                    
                    st.session_state.profile = {
                        'name': name,
                        'sex': sex,
                        'dob': str(dob),
                        'age': age,
                        'health_conditions': conditions,
                        'allergies': allergies,
                        'medications': medications
                    }
                    st.session_state.profile_complete = True
                    st.rerun()


def show_api_key_input():
    """Show API key input."""
    
    st.markdown("""
        <div class="api-wrapper">
            <div class="api-card">
                <div class="api-icon">🔑</div>
                <h2 class="api-title">Connect AI</h2>
                <p class="api-subtitle">Enter your Anthropic API key to activate Sage</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("api_form"):
            api_key = st.text_input("API Key", type="password", placeholder="sk-ant-...")
            st.markdown("[Get your API key →](https://console.anthropic.com)")
            
            if st.form_submit_button("Connect", use_container_width=True):
                if api_key:
                    try:
                        st.session_state.ai_engine = SageAI(api_key)
                        st.session_state.api_key = api_key
                        if st.session_state.profile:
                            st.session_state.ai_engine.set_user_profile(st.session_state.profile)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Connection failed: {e}")


def show_chat():
    """Display main chat interface."""
    profile = st.session_state.profile
    user_initial = profile.get('name', 'U')[0].upper() if profile else 'U'
    
    # Header
    st.markdown(f"""
        <div class="chat-header">
            <div class="chat-header-left">
                <div class="chat-logo">🌿</div>
                <span class="chat-brand">Sage</span>
            </div>
            <div class="user-avatar">{user_initial}</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Initialize greeting
    if not st.session_state.messages:
        greeting = st.session_state.ai_engine.get_greeting()
        st.session_state.messages.append({"role": "assistant", "content": greeting})
    
    # Chat container
    st.markdown('<div class="chat-main">', unsafe_allow_html=True)
    
    # Welcome message if just started
    if len(st.session_state.messages) <= 1:
        st.markdown(f"""
            <div class="chat-welcome">
                <div class="welcome-icon">🌿</div>
                <h1 class="welcome-title">Hi, I'm Sage</h1>
                <p class="welcome-subtitle">I'm here to help you understand your health better. Tell me about any symptoms or ask me health questions.</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Display messages
    for msg in st.session_state.messages:
        role = "sage" if msg["role"] == "assistant" else "user"
        avatar = "🌿" if role == "sage" else user_initial
        st.markdown(f"""
            <div class="message {role}">
                <div class="message-avatar {role}">{avatar}</div>
                <div class="message-content">{msg["content"]}</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Disclaimer
    st.markdown("""
        <div class="disclaimer">
            ⚠️ Sage provides general health information only. Always consult a healthcare provider for medical concerns.
        </div>
    """, unsafe_allow_html=True)
    
    # Quick suggestions
    if len(st.session_state.messages) <= 2:
        st.markdown('<div class="suggestions">', unsafe_allow_html=True)
        suggestions = ["I have a headache", "Cold remedies", "Better sleep tips", "Feeling stressed"]
        cols = st.columns(4)
        for i, sug in enumerate(suggestions):
            if cols[i].button(sug, key=f"sug_{i}"):
                st.session_state.pending_message = sug
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input
    if prompt := st.chat_input("Describe your symptoms or ask a health question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        response = st.session_state.ai_engine.chat(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
    
    # Handle pending message
    if "pending_message" in st.session_state:
        msg = st.session_state.pending_message
        del st.session_state.pending_message
        st.session_state.messages.append({"role": "user", "content": msg})
        response = st.session_state.ai_engine.chat(msg)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()


# ============== MAIN ==============

def main():
    init_session()
    
    # Check auth callback
    params = st.query_params
    if params.get('auth') == 'success':
        st.session_state.authenticated = True
        st.query_params.clear()
        st.rerun()
    
    # Splash screen
    if st.session_state.show_splash:
        show_splash()
        return
    
    # Auth check
    if not st.session_state.authenticated:
        try:
            response = requests.get(f"{BACKEND_URL}/api/check-session", timeout=2)
            if response.ok and response.json().get('authenticated'):
                st.session_state.authenticated = True
            else:
                show_login()
                return
        except:
            show_login()
            return
    
    # Onboarding
    if not st.session_state.profile_complete:
        show_onboarding()
        return
    
    # API key
    if not st.session_state.ai_engine:
        show_api_key_input()
        return
    
    # Set profile
    if st.session_state.profile:
        st.session_state.ai_engine.set_user_profile(st.session_state.profile)
    
    # Chat
    show_chat()


if __name__ == "__main__":
    main()