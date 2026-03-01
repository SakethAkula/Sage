"""
Sage - AI Healthcare Chatbot
Backend: Flask Server with MySQL Authentication & Google OAuth
Updated with Email OTP Verification, Password Reset, and Smart Chat Titles
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import sys
import secrets
import requests
import base64

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import (
    create_user, verify_user, get_user_by_id, get_user_by_email,
    create_google_user, update_user_password, update_user_details,
    save_health_profile, get_health_profile,
    create_chat_session, get_chat_sessions, update_session_title, delete_chat_session,
    save_chat_message, get_chat_history, clear_chat_history
)
from db_config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI
from sage_ai import get_sage_instance, clear_sage_instance, generate_chat_title
from email_utils import send_verification_otp, send_password_reset_otp, verify_otp

app = Flask(
    __name__,
    template_folder='../frontend/templates',
    static_folder='../frontend/static'
)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
CORS(app)

# File upload configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create uploads folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ============== PAGE ROUTES ==============

@app.route('/')
def index():
    """Redirect to login or chat based on session."""
    if session.get('user_id'):
        if session.get('profile_complete'):
            return redirect(url_for('chat'))
        return redirect(url_for('onboarding'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            return render_template('login.html', error="Please fill all fields")
        
        # Verify user credentials
        user = verify_user(email, password)
        
        if user:
            # Set session
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            
            # Check if health profile exists
            profile = get_health_profile(user['id'])
            if profile:
                session['profile_complete'] = True
                return redirect(url_for('chat'))
            else:
                return redirect(url_for('onboarding'))
        else:
            return render_template('login.html', error="Invalid email or password")
    
    # Check for success message from password reset
    success = request.args.get('success')
    return render_template('login.html', success=success)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Signup page - Step 1: Collect info and send OTP."""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        gender = request.form.get('gender')
        dob = request.form.get('dob')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not all([name, email, password, confirm_password]):
            return render_template('signup.html', error="Please fill all required fields")
        
        if password != confirm_password:
            return render_template('signup.html', error="Passwords do not match")
        
        if len(password) < 6:
            return render_template('signup.html', error="Password must be at least 6 characters")
        
        # Check if email already exists
        existing_user = get_user_by_email(email)
        if existing_user:
            return render_template('signup.html', error="Email already registered. Please login.")
        
        # Store signup data in session and send OTP
        session['signup_data'] = {
            'name': name,
            'email': email,
            'gender': gender,
            'dob': dob,
            'password': password
        }
        
        # Send OTP
        success, otp = send_verification_otp(email)
        if success:
            return redirect(url_for('verify_email'))
        else:
            return render_template('signup.html', error="Failed to send verification email. Please try again.")
    
    return render_template('signup.html')


@app.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    """Email verification page."""
    if 'signup_data' not in session:
        return redirect(url_for('signup'))
    
    email = session['signup_data']['email']
    
    if request.method == 'POST':
        otp = request.form.get('otp')
        
        if not otp:
            return render_template('verify_email.html', email=email, error="Please enter the OTP")
        
        # Verify OTP
        valid, message = verify_otp(email, otp, "verification")
        
        if valid:
            # Create user
            data = session['signup_data']
            user_id = create_user(
                data['name'], 
                data['email'], 
                data['password'], 
                data.get('gender'), 
                data.get('dob') if data.get('dob') else None
            )
            
            if user_id:
                # Clear signup data
                session.pop('signup_data', None)
                
                # Set user session
                session['user_id'] = user_id
                session['user_name'] = data['name']
                session['user_email'] = data['email']
                
                return redirect(url_for('onboarding'))
            else:
                return render_template('verify_email.html', email=email, error="Failed to create account")
        else:
            return render_template('verify_email.html', email=email, error=message)
    
    return render_template('verify_email.html', email=email)


@app.route('/resend-otp', methods=['POST'])
def resend_otp():
    """Resend OTP for email verification."""
    if 'signup_data' not in session:
        return jsonify({'error': 'No signup in progress'}), 400
    
    email = session['signup_data']['email']
    success, otp = send_verification_otp(email)
    
    if success:
        return jsonify({'success': True, 'message': 'OTP sent successfully'})
    else:
        return jsonify({'error': 'Failed to send OTP'}), 500


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password - Step 1: Enter email."""
    if request.method == 'POST':
        email = request.form.get('email')
        
        if not email:
            return render_template('forgot_password.html', error="Please enter your email")
        
        # Check if user exists
        user = get_user_by_email(email)
        if not user:
            return render_template('forgot_password.html', error="No account found with this email")
        
        # Send OTP
        success, otp = send_password_reset_otp(email)
        if success:
            session['reset_email'] = email
            return redirect(url_for('reset_password'))
        else:
            return render_template('forgot_password.html', error="Failed to send reset email. Please try again.")
    
    return render_template('forgot_password.html')


@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Reset password - Step 2: Enter OTP and new password."""
    if 'reset_email' not in session:
        return redirect(url_for('forgot_password'))
    
    email = session['reset_email']
    
    if request.method == 'POST':
        otp = request.form.get('otp')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not all([otp, new_password, confirm_password]):
            return render_template('reset_password.html', email=email, error="Please fill all fields")
        
        if new_password != confirm_password:
            return render_template('reset_password.html', email=email, error="Passwords do not match")
        
        if len(new_password) < 6:
            return render_template('reset_password.html', email=email, error="Password must be at least 6 characters")
        
        # Verify OTP
        valid, message = verify_otp(email, otp, "reset")
        
        if valid:
            # Update password
            success = update_user_password(email, new_password)
            if success:
                session.pop('reset_email', None)
                return redirect(url_for('login', success="Password reset successful. Please login."))
            else:
                return render_template('reset_password.html', email=email, error="Failed to update password")
        else:
            return render_template('reset_password.html', email=email, error=message)
    
    return render_template('reset_password.html', email=email)


@app.route('/resend-reset-otp', methods=['POST'])
def resend_reset_otp():
    """Resend OTP for password reset."""
    if 'reset_email' not in session:
        return jsonify({'error': 'No reset in progress'}), 400
    
    email = session['reset_email']
    success, otp = send_password_reset_otp(email)
    
    if success:
        return jsonify({'success': True, 'message': 'OTP sent successfully'})
    else:
        return jsonify({'error': 'Failed to send OTP'}), 500


@app.route('/google-complete-profile', methods=['GET', 'POST'])
def google_complete_profile():
    """Complete profile for Google users - collect gender and DOB."""
    if not session.get('google_signup_pending'):
        return redirect(url_for('login'))
    
    name = session.get('google_name', '')
    email = session.get('google_email', '')
    
    if request.method == 'POST':
        gender = request.form.get('gender')
        dob = request.form.get('dob')
        
        if not gender or not dob:
            return render_template('google_complete_profile.html', 
                                   name=name, email=email, 
                                   error="Please fill all fields")
        
        # Create or update user
        user_id = create_google_user(name, email, gender, dob)
        
        if user_id:
            # Clear pending signup
            session.pop('google_signup_pending', None)
            session.pop('google_name', None)
            session.pop('google_email', None)
            
            # Set user session
            session['user_id'] = user_id
            session['user_name'] = name
            session['user_email'] = email
            session['auth_provider'] = 'google'
            
            return redirect(url_for('onboarding'))
        else:
            return render_template('google_complete_profile.html',
                                   name=name, email=email,
                                   error="Failed to create account")
    
    return render_template('google_complete_profile.html', name=name, email=email)


@app.route('/onboarding', methods=['GET', 'POST'])
def onboarding():
    """Onboarding page for health profile."""
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        conditions = request.form.getlist('conditions')
        other_condition = request.form.get('other_condition')
        allergies = request.form.get('allergies')
        medications = request.form.get('medications')
        
        # Add other condition if specified
        if 'Other' in conditions and other_condition:
            conditions.append(other_condition)
        
        # Save health profile
        success = save_health_profile(
            user_id=session['user_id'],
            conditions=conditions if conditions else None,
            allergies=allergies if allergies else None,
            medications=medications if medications else None
        )
        
        if success:
            session['profile_complete'] = True
            return redirect(url_for('chat'))
        else:
            return render_template('onboarding.html', error="Failed to save profile")
    
    return render_template('onboarding.html')


@app.route('/chat')
def chat():
    """Main chat page."""
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    # Get user info and profile
    user = get_user_by_id(session['user_id'])
    profile = get_health_profile(session['user_id'])
    
    # Combine user and profile data
    user_data = {
        'name': user['name'] if user else session.get('user_name', 'User'),
        'email': user['email'] if user else session.get('user_email', ''),
    }
    
    if profile:
        user_data['conditions'] = profile.get('conditions', [])
        user_data['allergies'] = profile.get('allergies', '')
        user_data['medications'] = profile.get('medications', '')
    
    return render_template('chat.html', profile=user_data)


@app.route('/logout')
def logout():
    """Logout user."""
    session.clear()
    return redirect(url_for('login'))


# ============== API ROUTES ==============

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """Handle chat messages with AI."""
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    message = data.get('message')
    
    if not message:
        return jsonify({'error': 'No message provided'}), 400
    
    # Get or create chat session
    is_new_session = False
    if not session.get('current_session_id'):
        is_new_session = True
        # Create new session with temporary title
        session_id = create_chat_session(session['user_id'], "New Chat")
        session['current_session_id'] = session_id
    else:
        session_id = session['current_session_id']
    
    # Save user message to database
    save_chat_message(session['user_id'], message, 'user', session_id)
    
    # Get user profile for personalized responses
    user_profile = {
        'name': session.get('user_name', 'there')
    }
    profile = get_health_profile(session['user_id'])
    if profile:
        user_profile['conditions'] = profile.get('conditions', [])
        user_profile['allergies'] = profile.get('allergies', '')
        user_profile['medications'] = profile.get('medications', '')
    
    # Get AI instance and response
    sage = get_sage_instance(session['user_id'], user_profile)
    response = sage.chat(message)
    
    # Save AI response to database
    save_chat_message(session['user_id'], response, 'sage', session_id)
    
    # Generate meaningful title for new sessions
    if is_new_session:
        title = generate_chat_title(message)
        update_session_title(session_id, title)
    
    return jsonify({
        'response': response,
        'session_id': session_id
    })


@app.route('/api/profile', methods=['GET', 'POST'])
def api_profile():
    """Get or update user profile."""
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    if request.method == 'POST':
        data = request.json
        success = save_health_profile(
            user_id=session['user_id'],
            conditions=data.get('conditions'),
            allergies=data.get('allergies'),
            medications=data.get('medications')
        )
        if success:
            session['profile_complete'] = True
            return jsonify({'success': True})
        return jsonify({'error': 'Failed to save profile'}), 500
    
    profile = get_health_profile(session['user_id'])
    return jsonify(profile if profile else {})


@app.route('/api/chat-history', methods=['GET', 'DELETE'])
def api_chat_history():
    """Get or clear chat history."""
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    if request.method == 'DELETE':
        # Clear database history
        success = clear_chat_history(session['user_id'])
        # Clear AI conversation memory
        clear_sage_instance(session['user_id'])
        return jsonify({'success': success})
    
    history = get_chat_history(session['user_id'])
    return jsonify(history)


@app.route('/api/new-chat', methods=['POST'])
def api_new_chat():
    """Start a new chat session."""
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Clear current session
    session.pop('current_session_id', None)
    
    # Clear AI conversation memory
    clear_sage_instance(session['user_id'])
    
    return jsonify({'success': True})


@app.route('/api/sessions', methods=['GET'])
def api_get_sessions():
    """Get all chat sessions for current user."""
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    sessions = get_chat_sessions(session['user_id'])
    
    # Convert datetime to string
    for s in sessions:
        s['created_at'] = s['created_at'].isoformat() if s['created_at'] else None
        s['updated_at'] = s['updated_at'].isoformat() if s['updated_at'] else None
    
    return jsonify({
        'sessions': sessions,
        'current_session_id': session.get('current_session_id')
    })


@app.route('/api/sessions/<int:session_id>', methods=['GET', 'DELETE'])
def api_session(session_id):
    """Get or delete a specific chat session."""
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    if request.method == 'DELETE':
        success = delete_chat_session(session_id, session['user_id'])
        if session.get('current_session_id') == session_id:
            session.pop('current_session_id', None)
        return jsonify({'success': success})
    
    # GET - load session messages
    messages = get_chat_history(session['user_id'], session_id)
    
    # Set as current session
    session['current_session_id'] = session_id
    
    # Clear and reload AI memory with this conversation
    clear_sage_instance(session['user_id'])
    sage = get_sage_instance(session['user_id'])
    
    # Rebuild AI conversation history
    for msg in messages:
        sage.conversation_history.append({
            "role": "user" if msg['sender'] == 'user' else "assistant",
            "content": msg['message']
        })
    
    # Convert datetime
    for msg in messages:
        msg['created_at'] = msg['created_at'].isoformat() if msg['created_at'] else None
    
    return jsonify({'messages': messages})


@app.route('/api/upload', methods=['POST'])
def api_upload():
    """Handle file upload and analyze with AI."""
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    message = request.form.get('message', 'Please analyze this image/document.')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed. Use PNG, JPG, GIF, WEBP, or PDF'}), 400
    
    try:
        # Read file content
        file_content = file.read()
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower()
        
        # Save file
        user_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(session['user_id']))
        os.makedirs(user_folder, exist_ok=True)
        
        # Generate unique filename
        unique_filename = f"{secrets.token_hex(8)}_{filename}"
        file_path = os.path.join(user_folder, unique_filename)
        
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # Save user message to database
        save_chat_message(session['user_id'], f"[Uploaded: {filename}] {message}", 'user')
        
        # Get user profile
        user_profile = {'name': session.get('user_name', 'there')}
        profile = get_health_profile(session['user_id'])
        if profile:
            user_profile['conditions'] = profile.get('conditions', [])
            user_profile['allergies'] = profile.get('allergies', '')
            user_profile['medications'] = profile.get('medications', '')
        
        # Get AI instance
        sage = get_sage_instance(session['user_id'], user_profile)
        
        # Analyze based on file type
        if file_ext == 'pdf':
            response = sage.chat(f"[User uploaded a PDF document: {filename}] {message}\n\nNote: I cannot read PDF contents directly. Please describe what's in the document or copy-paste the relevant text, and I'll help you understand it.")
        else:
            # For images, use Claude's vision capability
            response = sage.analyze_image(file_content, file_ext, message)
        
        # Save AI response
        save_chat_message(session['user_id'], response, 'sage')
        
        return jsonify({
            'response': response,
            'filename': unique_filename
        })
        
    except Exception as e:
        print(f"Upload error: {e}")
        return jsonify({'error': 'Failed to process file'}), 500


@app.route('/uploads/<int:user_id>/<filename>')
def serve_upload(user_id, filename):
    """Serve uploaded files (only to the owner)."""
    if not session.get('user_id') or session['user_id'] != user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(user_id))
    return send_from_directory(user_folder, filename)


@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'sage-backend'})


# ============== GOOGLE OAUTH ==============

@app.route('/auth/google')
def google_auth():
    """Initiate Google OAuth - redirect to Google login."""
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={GOOGLE_REDIRECT_URI}"
        "&response_type=code"
        "&scope=openid%20email%20profile"
        "&access_type=offline"
    )
    return redirect(google_auth_url)


@app.route('/auth/google/callback')
def google_callback():
    """Handle Google OAuth callback."""
    code = request.args.get('code')
    error = request.args.get('error')
    
    if error:
        return redirect(url_for('login', error='Google login cancelled'))
    
    if not code:
        return redirect(url_for('login', error='No authorization code received'))
    
    try:
        # Exchange code for tokens
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            'code': code,
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'redirect_uri': GOOGLE_REDIRECT_URI,
            'grant_type': 'authorization_code'
        }
        
        token_response = requests.post(token_url, data=token_data)
        tokens = token_response.json()
        
        if 'error' in tokens:
            return redirect(url_for('login', error='Failed to get access token'))
        
        access_token = tokens.get('access_token')
        
        # Get user info from Google
        userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {'Authorization': f'Bearer {access_token}'}
        userinfo_response = requests.get(userinfo_url, headers=headers)
        userinfo = userinfo_response.json()
        
        if 'error' in userinfo:
            return redirect(url_for('login', error='Failed to get user info'))
        
        # Extract user data
        google_email = userinfo.get('email')
        google_name = userinfo.get('name', google_email.split('@')[0])
        
        # Check if user already exists
        existing_user = get_user_by_email(google_email)
        
        if existing_user:
            # Existing user - log them in
            session['user_id'] = existing_user['id']
            session['user_name'] = existing_user['name']
            session['user_email'] = existing_user['email']
            session['auth_provider'] = 'google'
            
            # Check if health profile exists
            profile = get_health_profile(existing_user['id'])
            if profile:
                session['profile_complete'] = True
                return redirect(url_for('chat'))
            else:
                return redirect(url_for('onboarding'))
        else:
            # New user - need to collect additional info
            session['google_signup_pending'] = True
            session['google_name'] = google_name
            session['google_email'] = google_email
            return redirect(url_for('google_complete_profile'))
            
    except Exception as e:
        print(f"Google OAuth error: {e}")
        return redirect(url_for('login', error='Authentication failed'))


if __name__ == '__main__':
    print("\n" + "="*50)
    print("  🌿 SAGE - AI Healthcare Chatbot")
    print("="*50)
    print("\n  Server: http://localhost:5000")
    print("  Database: MySQL (sage_db)\n")
    app.run(debug=True, port=5000)