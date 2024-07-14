import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import json
from supabase import create_client, Client
from requests_html import HTMLSession
from StudentClass import StudentClass, Assignment
from datetime import datetime

# Load environment variables
load_dotenv()
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Initialize Supabase client
supabase: Client = create_client(url, key)

# Global session object
web_session = HTMLSession()


def loginToCanvas(username, password):
    global web_session
    login_url = "https://tmcc.instructure.com/login/canvas"
    
    try:
        # Fetch the login page to get any hidden fields
        login_page = web_session.get(login_url)
        login_page.raise_for_status()  # Raise exception for bad responses
        soup = BeautifulSoup(login_page.text, 'html.parser')
        
        # Extract hidden fields
        hidden_inputs = soup.find_all("input", type="hidden")
        payload = {
            'pseudonym_session[unique_id]': username,
            'pseudonym_session[password]': password
        }
        
        # Add hidden fields to payload
        for hidden_input in hidden_inputs:
            payload[hidden_input['name']] = hidden_input['value']
        
        # Set headers (if necessary)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        
        response = web_session.post(login_url, data=payload, headers=headers)
        response.raise_for_status()  # Raise exception for bad responses
        
        if "Invalid" in response.text or response.url == login_url:
            raise Exception("Login failed")
        else:
            print("Login successful")
    
    except Exception as e:
        print(f"Error during login: {str(e)}")
        raise  # Rethrow exception to terminate execution or handle as needed

def scrape_classes():
    global web_session
    dashboard_url = "https://tmcc.instructure.com/api/v1/users/self/favorites/courses"
    
    try:
        response = web_session.get(dashboard_url)
        response.raise_for_status()  # Raise exception for bad responses
        courses_data = json.loads(response.text)
        
        student_classes = []
        
        if not courses_data:
            print("No classes found or unable to locate classes.")
            return student_classes
        
        for course in courses_data:
            class_name = course.get('short_name') or course.get('name', 'No Name')
            class_id = course.get('id')
            class_url = f"https://tmcc.instructure.com/api/v1/courses/{class_id}"
            student_class = StudentClass(class_name, class_id)  # Pass class_id to constructor
            student_classes.append(student_class)
            print(f"Class found: {class_name}")
            scrape_assignments(student_class, class_url)
        
        return student_classes
    
    except Exception as e:
        print(f"Error fetching classes: {str(e)}")
        raise  # Rethrow exception to terminate execution or handle as needed

def scrape_assignments(student_class, class_url):
    global web_session
    assignments_url = f"{class_url}/assignments?per_page=500"
    
    try:
        response = web_session.get(assignments_url)
        response.raise_for_status()  # Raise exception for bad responses
        
        assignments_data = json.loads(response.text)
        
        for assignment_data in assignments_data:
            assignment_name = assignment_data.get('name', 'No Title')
            due_date = assignment_data.get('due_at', None)
            description = assignment_data.get('description', '')

            # Check if due date is in the past
            if due_date and datetime.strptime(due_date, '%Y-%m-%dT%H:%M:%SZ') < datetime.now():
                print(f"Skipping assignment '{assignment_name}' due to past due date. Due date: {due_date}")
                continue

            # Create Assignment object and append to student_class
            assignment = Assignment(name=assignment_name, due_date=due_date, description=description)
            student_class.assignments.append(assignment)
            print(f"Assignment found: {assignment_name}, Due: {due_date}")
    
    except Exception as e:
        print(f"Error fetching assignments: {str(e)}")
        raise  # Rethrow exception to terminate execution or handle as needed


def add_classes_and_assignments_to_db(user_id, student_classes):
    try:
        for student_class in student_classes:
            # Check if the class already exists for the user_id
            existing_class = supabase.table('classes').select('id', 'class_id').eq('class_id', student_class.class_id).eq('user_id', user_id).execute()
            
            if existing_class.data:
                print(f"Class with class_id {student_class.class_id} already exists for user_id {user_id}. Using existing class.")
                class_db_id = existing_class.data[0]['id']
                actual_class_id = existing_class.data[0]['class_id']
            else:
                # Insert class into database
                class_insert = supabase.table('classes').insert({
                    'class_name': student_class.class_name,
                    'class_id': student_class.class_id,
                    'user_id': user_id
                }).execute()
                class_db_id = class_insert.data[0]['id']
                actual_class_id = student_class.class_id
                print(f"Class {student_class.class_name} added to database.")

            # Retrieve existing assignments for the class
            existing_assignments = supabase.table('assignments').select('assignment_name').eq('class_id', student_class.class_id).execute()
            existing_assignment_names = {assignment['assignment_name'] for assignment in existing_assignments.data}
            
            # Prepare batch insert for assignments
            assignments_to_insert = []
            for assignment in student_class.assignments:
                if assignment.name not in existing_assignment_names:
                    assignments_to_insert.append({
                        'class_id': actual_class_id,  # Use actual_class_id here
                        'assignment_name': assignment.name,
                        'due_date': assignment.due_date,
                        'description': assignment.description,
                        'user_id' : user_id,
                        'class_name' : student_class.class_name
                    })
                else:
                    print(f"{assignment.name} already in assignments. Not inserting. ")
            
            # Insert assignments in batch
            if assignments_to_insert:
                try:
                    insert_result = supabase.table('assignments').insert(assignments_to_insert).execute()
                    print(f"Assignments added for class {student_class.class_name}.")
                except Exception as e:
                    print("Error inserting assignments")
            else:
                print(f"No new assignments to add for class {student_class.class_name}.")
    
    except Exception as e:
        print(f"Error adding classes and assignments to database: {str(e)}")
        raise  # Rethrow exception to terminate execution or handle as needed

def get_assignments_for_user(user_id):
    try:
        # Fetch assignments from the database for the given user_id
        assignments_data = supabase.table('assignments').select('*').eq('user_id', user_id).execute()

        assignments = []
        for assignment in assignments_data.data:
            assignments.append({
                'class_id': assignment['class_id'],
                'assignment_name': assignment['assignment_name'],
                'due_date': assignment['due_date'],
                'description': assignment['description'],
                'class_name' : assignment['class_name']
            })

        return assignments

    except Exception as e:
        print(f"Error fetching assignments for user_id {user_id}: {str(e)}")
        return None  # Handle the error as needed

def main():
    try:
        # Load environment variables
        load_dotenv()
        username = os.getenv("USERNAME_CANVAS")
        password = os.getenv("PASSWORD_CANVAS")
        user_id = os.getenv("USER_ID")

        #get_assignments_for_user(user_id)
        loginToCanvas(username, password)
        student_classes = scrape_classes()
        add_classes_and_assignments_to_db(user_id, student_classes)
      #print_user_classes(student_classes)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        # Handle the error 

def print_user_classes(student_classes):
    for student_class in student_classes:
        print(student_class.class_name)
        for assignment in student_class.assignments:
            print(f" - {assignment.name}, Due: {assignment.due_date}")

if __name__ == "__main__":
    main()
