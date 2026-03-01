"""
Sage - Database Helper
Handles all database operations for users, profiles, and chat history
Updated with password reset and user details update
"""

import mysql.connector
from mysql.connector import Error
import bcrypt
import json
import secrets
import os

# Get DB config from environment
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'database': os.environ.get('DB_NAME', 'sage_db'),
    'charset': 'utf8mb4',
    'autocommit': True,
    'connect_timeout': 10
}

# Cloud SQL Unix Socket (if provided)
CLOUD_SQL_CONNECTION_NAME = os.environ.get('CLOUD_SQL_CONNECTION_NAME', None)


def get_connection():
    """Create and return a database connection."""
    try:
        config = DB_CONFIG.copy()
        
        # If running on Cloud Run with Cloud SQL, use Unix socket
        if CLOUD_SQL_CONNECTION_NAME:
            config['unix_socket'] = f'/cloudsql/{CLOUD_SQL_CONNECTION_NAME}'
            config.pop('host', None)  # Remove host when using socket
        
        connection = mysql.connector.connect(**config)
        return connection
    except Error as e:
        print(f"Database connection error: {e}")
        print(f"Config used: host={config.get('host')}, user={config.get('user')}, database={config.get('database')}")
        return None


# ============== USER OPERATIONS ==============

def create_user(name, email, password, gender=None, dob=None):
    """
    Create a new user with hashed password.
    Returns user_id if successful, None if email exists.
    """
    connection = get_connection()
    if not connection:
        print("Failed to get database connection in create_user")
        return None
    
    try:
        cursor = connection.cursor()
        
        # Check if email already exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return None  # Email already exists
        
        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Insert user
        query = """
            INSERT INTO users (name, email, password, gender, dob)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (name, email, hashed_password.decode('utf-8'), gender, dob))
        connection.commit()
        
        user_id = cursor.lastrowid
        return user_id
        
    except Error as e:
        print(f"Error creating user: {e}")
        return None
    finally:
        cursor.close()
        connection.close()


def create_google_user(name, email, gender=None, dob=None):
    """
    Create a new user from Google OAuth (no password).
    Returns user_id if successful, existing user_id if email exists.
    """
    connection = get_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor()
        
        # Check if email already exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        existing = cursor.fetchone()
        if existing:
            # Update existing user's gender and dob if provided
            if gender or dob:
                update_query = "UPDATE users SET "
                update_values = []
                if gender:
                    update_query += "gender = %s, "
                    update_values.append(gender)
                if dob:
                    update_query += "dob = %s, "
                    update_values.append(dob)
                update_query = update_query.rstrip(', ') + " WHERE id = %s"
                update_values.append(existing[0])
                cursor.execute(update_query, tuple(update_values))
                connection.commit()
            return existing[0]  # Return existing user_id
        
        # Create random password for Google users (they won't use it)
        random_password = bcrypt.hashpw(secrets.token_hex(16).encode('utf-8'), bcrypt.gensalt())
        
        # Insert user
        query = """
            INSERT INTO users (name, email, password, gender, dob)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (name, email, random_password.decode('utf-8'), gender, dob))
        connection.commit()
        
        user_id = cursor.lastrowid
        return user_id
        
    except Error as e:
        print(f"Error creating Google user: {e}")
        return None
    finally:
        cursor.close()
        connection.close()


def verify_user(email, password):
    """
    Verify user credentials.
    Returns user dict if valid, None if invalid.
    """
    connection = get_connection()
    if not connection:
        print("Failed to get database connection in verify_user")
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            # Remove password from returned data
            del user['password']
            return user
        
        return None
        
    except Error as e:
        print(f"Error verifying user: {e}")
        return None
    finally:
        cursor.close()
        connection.close()


def update_user_password(email, new_password):
    """Update user's password."""
    connection = get_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        # Hash the new password
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        
        query = "UPDATE users SET password = %s WHERE email = %s"
        cursor.execute(query, (hashed_password.decode('utf-8'), email))
        connection.commit()
        
        return cursor.rowcount > 0
        
    except Error as e:
        print(f"Error updating password: {e}")
        return False
    finally:
        cursor.close()
        connection.close()


def update_user_details(user_id, gender=None, dob=None):
    """Update user's gender and/or date of birth."""
    connection = get_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        updates = []
        values = []
        
        if gender:
            updates.append("gender = %s")
            values.append(gender)
        if dob:
            updates.append("dob = %s")
            values.append(dob)
        
        if not updates:
            return True  # Nothing to update
        
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
        values.append(user_id)
        
        cursor.execute(query, tuple(values))
        connection.commit()
        
        return True
        
    except Error as e:
        print(f"Error updating user details: {e}")
        return False
    finally:
        cursor.close()
        connection.close()


def get_user_by_id(user_id):
    """Get user by ID."""
    connection = get_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT id, name, email, gender, dob, created_at FROM users WHERE id = %s"
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()
        
        return user
        
    except Error as e:
        print(f"Error getting user: {e}")
        return None
    finally:
        cursor.close()
        connection.close()


def get_user_by_email(email):
    """Get user by email."""
    connection = get_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT id, name, email, gender, dob, created_at FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        
        return user
        
    except Error as e:
        print(f"Error getting user: {e}")
        return None
    finally:
        cursor.close()
        connection.close()


# ============== HEALTH PROFILE OPERATIONS ==============

def save_health_profile(user_id, conditions=None, allergies=None, medications=None):
    """
    Save or update health profile for a user.
    Returns True if successful.
    """
    connection = get_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        # Check if profile exists
        cursor.execute("SELECT id FROM health_profiles WHERE user_id = %s", (user_id,))
        existing = cursor.fetchone()
        
        conditions_json = json.dumps(conditions) if conditions else None
        
        if existing:
            # Update existing profile
            query = """
                UPDATE health_profiles 
                SET conditions = %s, allergies = %s, medications = %s
                WHERE user_id = %s
            """
            cursor.execute(query, (conditions_json, allergies, medications, user_id))
        else:
            # Create new profile
            query = """
                INSERT INTO health_profiles (user_id, conditions, allergies, medications)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (user_id, conditions_json, allergies, medications))
        
        connection.commit()
        return True
        
    except Error as e:
        print(f"Error saving health profile: {e}")
        return False
    finally:
        cursor.close()
        connection.close()


def get_health_profile(user_id):
    """Get health profile for a user."""
    connection = get_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT * FROM health_profiles WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        profile = cursor.fetchone()
        
        if profile and profile['conditions']:
            profile['conditions'] = json.loads(profile['conditions'])
        
        return profile
        
    except Error as e:
        print(f"Error getting health profile: {e}")
        return None
    finally:
        cursor.close()
        connection.close()


# ============== CHAT HISTORY OPERATIONS ==============

def create_chat_session(user_id, title="New Chat"):
    """Create a new chat session."""
    connection = get_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor()
        
        query = "INSERT INTO chat_sessions (user_id, title) VALUES (%s, %s)"
        cursor.execute(query, (user_id, title))
        connection.commit()
        
        return cursor.lastrowid
        
    except Error as e:
        print(f"Error creating chat session: {e}")
        return None
    finally:
        cursor.close()
        connection.close()


def get_chat_sessions(user_id, limit=20):
    """Get all chat sessions for a user."""
    connection = get_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        query = """
            SELECT id, title, created_at, updated_at 
            FROM chat_sessions 
            WHERE user_id = %s 
            ORDER BY updated_at DESC 
            LIMIT %s
        """
        cursor.execute(query, (user_id, limit))
        sessions = cursor.fetchall()
        
        return sessions
        
    except Error as e:
        print(f"Error getting chat sessions: {e}")
        return []
    finally:
        cursor.close()
        connection.close()


def update_session_title(session_id, title):
    """Update the title of a chat session."""
    connection = get_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        query = "UPDATE chat_sessions SET title = %s WHERE id = %s"
        cursor.execute(query, (title[:100], session_id))  # Limit to 100 chars
        connection.commit()
        return True
        
    except Error as e:
        print(f"Error updating session title: {e}")
        return False
    finally:
        cursor.close()
        connection.close()


def delete_chat_session(session_id, user_id):
    """Delete a chat session (only if owned by user)."""
    connection = get_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        query = "DELETE FROM chat_sessions WHERE id = %s AND user_id = %s"
        cursor.execute(query, (session_id, user_id))
        connection.commit()
        return cursor.rowcount > 0
        
    except Error as e:
        print(f"Error deleting chat session: {e}")
        return False
    finally:
        cursor.close()
        connection.close()


def save_chat_message(user_id, message, sender, session_id=None):
    """
    Save a chat message.
    sender: 'user' or 'sage'
    """
    connection = get_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        query = """
            INSERT INTO chat_history (user_id, message, sender, session_id)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (user_id, message, sender, session_id))
        connection.commit()
        return True
        
    except Error as e:
        print(f"Error saving chat message: {e}")
        return False
    finally:
        cursor.close()
        connection.close()


def get_chat_history(user_id, session_id=None, limit=50):
    """Get chat history for a user, optionally filtered by session."""
    connection = get_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        if session_id:
            query = """
                SELECT message, sender, created_at 
                FROM chat_history 
                WHERE user_id = %s AND session_id = %s
                ORDER BY created_at ASC 
                LIMIT %s
            """
            cursor.execute(query, (user_id, session_id, limit))
        else:
            query = """
                SELECT message, sender, created_at 
                FROM chat_history 
                WHERE user_id = %s 
                ORDER BY created_at DESC 
                LIMIT %s
            """
            cursor.execute(query, (user_id, limit))
        
        messages = cursor.fetchall()
        
        # If not filtering by session, reverse for chronological order
        if not session_id:
            messages = list(reversed(messages))
        
        return messages
        
    except Error as e:
        print(f"Error getting chat history: {e}")
        return []
    finally:
        cursor.close()
        connection.close()


def clear_chat_history(user_id):
    """Clear all chat history for a user."""
    connection = get_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        query = "DELETE FROM chat_history WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        connection.commit()
        return True
        
    except Error as e:
        print(f"Error clearing chat history: {e}")
        return False
    finally:
        cursor.close()
        connection.close()