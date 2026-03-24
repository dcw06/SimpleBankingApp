#!/usr/bin/env python3
"""
Google OAuth 2.0 authentication for the banking app.
Handles user login via Google accounts.
"""

import os
import json
import webbrowser
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlencode, parse_qs, urlparse
import requests
from storage import save_bank, load_bank
from bank import Bank

# Google OAuth Configuration (load from environment variables)
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
REDIRECT_URI = "http://localhost:8888/callback"
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://www.googleapis.com/oauth2/v4/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

# Validate credentials are set
if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    import sys
    print("ERROR: Google OAuth credentials not found!")
    print("Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables.")
    print("See .env.example for details.")
    sys.exit(1)

# Store the authorization code temporarily
auth_code = None
auth_error = None


class GoogleAuthHandler(BaseHTTPRequestHandler):
    """Handle OAuth callback from Google."""
    
    def do_GET(self):
        global auth_code, auth_error
        
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        
        if 'code' in query_params:
            auth_code = query_params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
            <html>
            <head><title>Authentication Successful</title></head>
            <body style="text-align: center; margin-top: 50px; font-family: Arial;">
            <h2>Authentication Successful!</h2>
            <p>You can now close this window and return to the app.</p>
            </body>
            </html>
            """)
        elif 'error' in query_params:
            auth_error = query_params.get('error_description', ['Unknown error'])[0]
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f"""
            <html>
            <head><title>Authentication Failed</title></head>
            <body style="text-align: center; margin-top: 50px; font-family: Arial;">
            <h2>Authentication Failed</h2>
            <p>{auth_error}</p>
            </body>
            </html>
            """.encode())
    
    def log_message(self, format, *args):
        """Suppress server logs."""
        pass


def get_google_login_url():
    """Generate the Google OAuth login URL."""
    params = {
        'client_id': GOOGLE_CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': 'profile email',
        'access_type': 'offline'
    }
    return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"


def start_local_server():
    """Start a local HTTP server to handle OAuth callback."""
    server = HTTPServer(('localhost', 8888), GoogleAuthHandler)
    thread = threading.Thread(target=server.handle_request, daemon=True)
    thread.start()
    return server


def exchange_code_for_token(code):
    """Exchange authorization code for access token."""
    data = {
        'code': code,
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    
    response = requests.post(GOOGLE_TOKEN_URL, data=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to exchange code: {response.text}")


def get_user_info(access_token):
    """Fetch user info from Google."""
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(GOOGLE_USERINFO_URL, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get user info: {response.text}")


def authenticate_with_google(bank: Bank):
    """
    Authenticate user via Google OAuth.
    Creates or logs in user using their Google account.
    Returns: User object if successful, None otherwise
    """
    global auth_code, auth_error
    
    # Reset globals
    auth_code = None
    auth_error = None
    
    try:
        # Start local server to catch callback
        server = start_local_server()
        
        # Open browser for user to login
        login_url = get_google_login_url()
        webbrowser.open(login_url)
        
        # Wait for callback (max 2 minutes)
        import time
        timeout = 120
        elapsed = 0
        while auth_code is None and auth_error is None and elapsed < timeout:
            time.sleep(0.5)
            elapsed += 0.5
        
        if auth_error:
            return None, f"Authentication failed: {auth_error}"
        
        if auth_code is None:
            return None, "Authentication timeout. Please try again."
        
        # Exchange code for token
        token_response = exchange_code_for_token(auth_code)
        access_token = token_response.get('access_token')
        
        # Get user info
        user_info = get_user_info(access_token)
        
        google_id = user_info.get('id')
        email = user_info.get('email')
        name = user_info.get('name', email.split('@')[0])
        
        # Check if user exists (by email)
        existing_user = None
        for user in bank.list_users():
            if user.username == email:
                existing_user = user
                break
        
        if existing_user:
            # User exists, log them in
            return existing_user, None
        else:
            # Create new user with Google ID as password (they won't need it)
            new_user = bank.create_user(email, google_id)
            save_bank(bank)
            return new_user, None
            
    except Exception as e:
        return None, f"Error during authentication: {str(e)}"
