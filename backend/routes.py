from flask import Flask, request, redirect, url_for, session, render_template_string
from requests_oauthlib import OAuth2Session
import os
from dotenv import load_dotenv
import requests
from flask import jsonify

load_dotenv()

# Environment variables
microsoft_client_id = os.getenv("MICROSOFT_CLIENT_ID")
microsoft_client_secret = os.getenv("MICROSOFT_CLIENT_SECRET")
microsoft_redirect_uri = os.getenv("MICROSOFT_REDIRECT_URI")
google_client_id = os.getenv("GOOGLE_CLIENT_ID")
google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
google_redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")

# OAuth2 endpoints for Microsoft and Google
microsoft_authorization_base_url = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
microsoft_token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
google_authorization_base_url = "https://accounts.google.com/o/oauth2/auth"
google_token_url = "https://oauth2.googleapis.com/token"

def init_routes(app):

    @app.route('/api/login/canvas', methods=['POST'])
    def login_to_canvas():
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        if email == 'demo@example.com' and password == 'password':
            return jsonify({'message': 'Login successful'}), 200
        else:
            return jsonify({'message': 'Invalid credentials'}), 401
        
    @app.route("/login/microsoft")
    def login_microsoft():
        microsoft = OAuth2Session(microsoft_client_id, redirect_uri=microsoft_redirect_uri, scope=["Tasks.ReadWrite"])
        authorization_url, state = microsoft.authorization_url(microsoft_authorization_base_url)
        session['oauth_state'] = state
        return redirect(authorization_url)

    @app.route("/callback/microsoft")
    def callback_microsoft():
        microsoft = OAuth2Session(microsoft_client_id, state=session['oauth_state'], redirect_uri=microsoft_redirect_uri)
        token = microsoft.fetch_token(microsoft_token_url, client_secret=microsoft_client_secret, authorization_response=request.url)
        session['oauth_token'] = token
        return redirect(url_for('home'))

    @app.route("/login/google")
    def login_google():
        google = OAuth2Session(google_client_id, redirect_uri=google_redirect_uri, scope=["https://www.googleapis.com/auth/calendar.readonly"])
        authorization_url, state = google.authorization_url(google_authorization_base_url, access_type="offline", prompt="consent")
        session['oauth_state'] = state
        return redirect(authorization_url)

    @app.route("/callback/google")
    def callback_google():
        google = OAuth2Session(google_client_id, state=session['oauth_state'], redirect_uri=google_redirect_uri)
        token = google.fetch_token(google_token_url, client_secret=google_client_secret, authorization_response=request.url)
        session['oauth_token'] = token
        return redirect(url_for('home'))

    @app.route("/home")
    def home():
        token = session.get('oauth_token')
        if token:
            list_id = get_todo_list_id(token['access_token'])
            task_response = create_tasks(token['access_token'], list_id, "test")
            return render_template_string("""
                <h1>Home Page</h1>
                <p>Task Created:</p>
                <pre>{{ task_response }}</pre>
            """, task_response=task_response)
        else:
            return "Home Page<br>No valid token found."

def get_todo_list_id(token):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    response = requests.get('https://graph.microsoft.com/v1.0/me/todo/lists', headers=headers)
    lists = response.json().get('value', [])
    if lists:
        return lists[0]['id']  # Use the ID of the first To Do list
    else:
        raise Exception("No To Do lists found")

def create_tasks(token, list_id, title):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    task_data = {
        'title': title,
        'dueDateTime': {
            'dateTime': '2024-06-30T18:00:00.0000000',
            'timeZone': 'UTC'
        },
        'body': {
            'content': 'This is the body of the task.',
            'contentType': 'text'
        }
    }
    response = requests.post(f'https://graph.microsoft.com/v1.0/me/todo/lists/{list_id}/tasks', headers=headers, json=task_data)
    return response.json()
