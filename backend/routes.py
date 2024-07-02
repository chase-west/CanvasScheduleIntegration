from flask import Flask, request, redirect, url_for, session, render_template_string
from requests_oauthlib import OAuth2Session
import os
import bcrypt
from supabase import create_client, Client
from dotenv import load_dotenv
import requests
from flask import jsonify
from CanvasInfo import *

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

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
    
    @app.route('/api/signup', methods=['POST'])
    def signup():
        data = request.json
        website_email = data.get('email')
        website_password = data.get('password')

        try:
            # Check if user already exists
            existing_user = supabase.table('users').select('id').eq('website_email', website_email).execute()
            if existing_user.data:
                return jsonify({'error': 'User already exists'}), 400

            # Hash the password before storing
            hashed_password = bcrypt.hashpw(website_password.encode('utf-8'), bcrypt.gensalt())

            # Store hashed password in your database along with other user data
            user = supabase.table('users').insert({'website_email': website_email, 'website_password': hashed_password.decode('utf-8')}).execute()
            
            session['user_id'] = user.data[0]['id']  # Store user ID in session for future use maybe

            return jsonify({'message': 'User registered successfully'}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @app.route('/api/login', methods=['POST'])
    def login():
        data = request.json
        website_email = data.get('email')
        website_password = data.get('password')

        try:
            # Retrieve user record from database
            user = supabase.table('users').select('*').eq('website_email', website_email).execute()

            if len(user.data) == 1:
                stored_password = user.data[0]['website_password'].encode('utf-8')
                # Check if entered password matches stored hashed password
                if bcrypt.checkpw(website_password.encode('utf-8'), stored_password):
                    session['user_id'] = user.data[0]['id']  # Store user ID in session for future use maybe
                    return jsonify({'message': 'Login successful'}), 200
                else:
                    return jsonify({'error': 'Invalid credentials'}), 401
            else:
                return jsonify({'error': 'User not found'}), 404
        except Exception as e:
            return jsonify({'Error during login': str(e)}), 500
        
    @app.route('/api/logout', methods=['POST'])
    def logout():
        session.pop('user_id', None)
        return jsonify({'message': 'Logged out successfully'}), 200
    
    @app.route('/api/userState', methods=['GET'])
    def check_user_state():
        user_id = session.get('user_id')
        print(user_id)
        if user_id:
            # Check if the user has logged in to Canvas
            canvas_query = supabase.table('canvas_credentials').select('user_id').eq('user_id', user_id).execute()
            canvas_logged_in = len(canvas_query.data) > 0

            if canvas_logged_in:
                return jsonify({'isAuthenticated': True, 'hasLoggedIntoCanvas': True}), 200
            else:
                return jsonify({'isAuthenticated': True, 'hasLoggedIntoCanvas': False}), 200
            
        else:
            return jsonify({'isAuthenticated': False}), 200

    @app.route('/api/login/canvas', methods=['POST'])
    def login_to_canvas():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        try:
            loginToCanvas(username, password)
            return jsonify({'message': 'Login successful'}), 200
        except:
             return jsonify({'message': 'Invalid credentials'}), 401
          
    @app.route("/login/microsoft")
    def login_microsoft():
        microsoft = OAuth2Session(microsoft_client_id, redirect_uri=microsoft_redirect_uri, scope=["Tasks.ReadWrite"])
        authorization_url, state = microsoft.authorization_url(microsoft_authorization_base_url)
        session['microsoft_oauth_state'] = state
        return redirect(authorization_url)

    @app.route("/callback/microsoft")
    def callback_microsoft():
        microsoft = OAuth2Session(microsoft_client_id, state=session.get('microsoft_oauth_state'), redirect_uri=microsoft_redirect_uri)
        token = microsoft.fetch_token(microsoft_token_url, client_secret=microsoft_client_secret, authorization_response=request.url)
        session['oauth_token'] = token
        return redirect(url_for('push_assignments_to_tasks_microsoft'))

    @app.route("/login/google")
    def login_google():
        google = OAuth2Session(google_client_id, redirect_uri=google_redirect_uri, scope=["https://www.googleapis.com/auth/tasks"])
        authorization_url, state = google.authorization_url(google_authorization_base_url, access_type="offline", prompt="consent")
        session['google_oauth_state'] = state
        return redirect(authorization_url)

    @app.route("/callback/google")
    def callback_google():
        google = OAuth2Session(google_client_id, state=session.get('google_oauth_state'), redirect_uri=google_redirect_uri)
        token = google.fetch_token(google_token_url, client_secret=google_client_secret, authorization_response=request.url)
        session['oauth_token'] = token
        return redirect(url_for('push_assignments_to_tasks_google'))
        
    @app.route('/push_assignments_to_tasks_microsoft', methods=['GET'])
    def push_assignments_to_tasks_microsoft():
        try:
            user_id = session.get('user_id')
            if not user_id:
                return jsonify({'error': 'User ID not provided in request body'}), 400
            
            assignments = get_assignments_for_user(user_id)
            if assignments:
                for assignment in assignments:
                    assignment_name = assignment['assignment_name']
                    due_date = assignment['due_date']

                    microsoft_token = session.get('_oauth_token')
                    if microsoft_token:
                        try:
                            list_id = get_todo_list_id(microsoft_token['access_token'])
                            task_response = create_tasks(microsoft_token['access_token'], list_id, assignment_name, due_date)
                            print(f"Task created in Microsoft Tasks for assignment {assignment_name}")
                        except Exception as e:
                            print(f"Error creating task in Microsoft Tasks: {str(e)}")

                return jsonify({'message': 'Assignments pushed to Microsoft Tasks successfully'}), 200

        except Exception as e:
            print(f"Error pushing assignments to Microsoft Tasks: {str(e)}")
            return jsonify({'error': f'Error pushing assignments to Microsoft Tasks: {str(e)}'}), 500

    @app.route('/push_assignments_to_tasks_google', methods=['GET'])
    def push_assignments_to_tasks_google():
        try:
            user_id = session.get('user_id')
            if not user_id:
                return jsonify({'error': 'User ID not provided in request body'}), 400
            
            assignments = get_assignments_for_user(user_id)
            if assignments:
                for assignment in assignments:
                    assignment_name = assignment['assignment_name']
                    due_date = assignment['due_date']

                    google_token = session.get('google_oauth_token')
                    if google_token:
                        try:
                            task_response = create_tasks(google_token['access_token'], "primary", assignment_name, due_date)
                            print(f"Task created in Google Tasks for assignment {assignment_name}")
                        except Exception as e:
                            print(f"Error creating task in Google Tasks: {str(e)}")

                return jsonify({'message': 'Assignments pushed to Google Tasks successfully'}), 200

        except Exception as e:
            print(f"Error pushing assignments to Google Tasks: {str(e)}")
            return jsonify({'error': f'Error pushing assignments to Google Tasks: {str(e)}'}), 500
               
      

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

def create_tasks(token, list_id, title, due_date):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    task_data = {
        'title': title,
        'dueDateTime': {
            'dateTime': due_date.strftime('%Y-%m-%dT%H:%M:%S.0000000'),
            'timeZone': 'UTC'
        },
        'body': {
            'content': 'This is the body of the task.',
            'contentType': 'text'
        }
    }
    
    try:
        response = requests.post(f'https://graph.microsoft.com/v1.0/me/todo/lists/{list_id}/tasks', headers=headers, json=task_data)
        response.raise_for_status()  # Raise an exception for bad response status
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error creating task: {e}")


