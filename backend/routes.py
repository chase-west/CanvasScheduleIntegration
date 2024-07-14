from flask import Flask, request, redirect, url_for, session, render_template_string
from requests_oauthlib import OAuth2Session
import os
import bcrypt
from supabase import create_client, Client
from dotenv import load_dotenv
import requests
import time
from flask import jsonify
from CanvasScraper import *
from datetime import datetime
from cryptography.fernet import Fernet

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)


def load_key():
    return os.getenv("ENCRYPTION_KEY").encode()

encryption_key = load_key()
fernet = Fernet(encryption_key)

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
        user_id = session.get('user_id')

        try:
            # Attempt to log in to Canvas
            loginToCanvas(username, password)
        except Exception as e:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        else:
            try:
        
                # Encrypt credentials before storing
                encrypted_username = fernet.encrypt(username.encode()).decode()
                encrypted_password = fernet.encrypt(password.encode()).decode()
                
                # Store credentials in database
                supabase.table('canvas_credentials').insert({
                    'user_id': user_id,
                    'canvas_username': encrypted_username,
                    'canvas_password': encrypted_password
                }).execute()

                return jsonify({'message': 'Login successful and credentials stored'}), 200
            
            except Exception as e:
                print(f"Error storing credentials: {str(e)}")
                return jsonify({'error': 'Error storing credentials'}), 500
          
    @app.route("/login/microsoft")
    def login_microsoft():
         # Scrape user classes
        try: 
            user_id = session.get('user_id')
            if not user_id:
                return jsonify({'error': 'No user ID'}), 400
            

            # Get username and password from database
            username, password = get_canvas_credentials(user_id)

            loginToCanvas(username, password)
            student_classes = scrape_classes()
            add_classes_and_assignments_to_db(user_id, student_classes)
        except Exception as e:
            print("Error scrapping classes and assigments. ")

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
            
            microsoft_token = session.get('oauth_token')
            if not microsoft_token:
                return jsonify({'error': 'Microsoft OAuth token not found'}), 400

            list_id, existing_task_names = get_todo_list_id(microsoft_token['access_token'])
            assignments = get_assignments_for_user(user_id)
            if not assignments:
                return jsonify({'message': 'No assignments found for user'}), 200

            for assignment in assignments:
                try:
                    assignment_name = assignment['assignment_name'] + " Class: " + assignment['class_name']
                    due_date_str = assignment.get('due_date')

                    if due_date_str:
                        due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M:%S')
                    else:
                        due_date = None

                    # Check if assignment name already exists in the To Do list
                    if assignment_name not in existing_task_names:
                        task_response = create_tasks_microsoft(microsoft_token['access_token'], list_id, assignment_name, due_date)
                        print(f"Task created in Microsoft Tasks for assignment {assignment_name}")
                        existing_task_names.append(assignment_name)  # Update the list of existing task names

                except ValueError as ve:
                    print(f"Due date format error for assignment {assignment_name}: {ve}")
                    return jsonify({'error': f'Due date format error for assignment {assignment_name}: {ve}'}), 400

                except Exception as e:
                    print(f"Error creating task in Microsoft Tasks: {str(e)}")
                    return jsonify({'error': f'Error creating task in Microsoft Tasks: {str(e)}'}), 500

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
                         #   task_response = create_tasks(google_token['access_token'], "primary", assignment_name, due_date)
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
    
    # First, try to find the list by display name
    response = requests.get('https://graph.microsoft.com/v1.0/me/todo/lists', headers=headers)
    lists = response.json().get('value', [])
    
    list_id = None
    for todo_list in lists:
        if todo_list.get('displayName') == 'Canvas Assignments':
            list_id = todo_list['id']
            break
    
    if not list_id:
        # Create the list if it doesn't exist
        default_list_data = {
            'displayName': 'Canvas Assignments'
        }
        create_list_response = requests.post('https://graph.microsoft.com/v1.0/me/todo/lists', headers=headers, json=default_list_data)
        
        if create_list_response.status_code == 201:
            list_id = create_list_response.json().get('id')
        else:
            raise Exception("Failed to create or find the 'Canvas Assignments' To Do list")
    
    # Fetch existing tasks in the list, handling pagination
    tasks_url = f'https://graph.microsoft.com/v1.0/me/todo/lists/{list_id}/tasks'
    tasks = []
    
    while tasks_url:
        tasks_response = requests.get(tasks_url, headers=headers)
        tasks_data = tasks_response.json()
        tasks.extend(tasks_data.get('value', []))
        tasks_url = tasks_data.get('@odata.nextLink', None)
    
    # Extract existing task names
    existing_task_names = [task.get('title') for task in tasks]
    
    return list_id, existing_task_names
        
def create_tasks_microsoft(token, list_id, title, due_date):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    task_data = {
        'title': title,
        'body': {
            'content': 'This is the body of the task.',
            'contentType': 'text'
        }
    }
    
    if due_date:
        task_data['dueDateTime'] = {
            'dateTime': due_date.strftime('%Y-%m-%dT%H:%M:%S.0000000'),
            'timeZone': 'UTC'
        }
    
    retry_count = 3
    retry_delay = 5  # seconds

    for attempt in range(retry_count):
        try:
            response = requests.post(f'https://graph.microsoft.com/v1.0/me/todo/lists/{list_id}/tasks', headers=headers, json=task_data)
            response.raise_for_status()  # Raise an exception for bad response status
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt < retry_count - 1:
                print(f"Error creating task: {e}. Retrying after {retry_delay} seconds.")
                time.sleep(retry_delay)
            else:
                raise Exception(f"Error creating task: {e}. Maximum retries exceeded.")

    return None

def get_canvas_credentials(user_id):
    try:
        # Retrieve encrypted credentials from the database
        credentials = supabase.table('canvas_credentials').select('canvas_username', 'canvas_password').eq('user_id', user_id).execute()
        
        if len(credentials.data) > 0:
            encrypted_username = credentials.data[0]['canvas_username']
            encrypted_password = credentials.data[0]['canvas_password']

            # Decrypt username and password
            decrypted_username = fernet.decrypt(encrypted_username.encode()).decode()
            decrypted_password = fernet.decrypt(encrypted_password.encode()).decode()

            return decrypted_username, decrypted_password
        else:
            return None, None  

    except Exception as e:
        print(f"Error retrieving credentials: {str(e)}")
        return None, None  



