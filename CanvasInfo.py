import os
from requests_html import HTMLSession
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import json
from StudentClass import StudentClass, Assignment

# Load environment variables
load_dotenv()
username = os.getenv("USERNAME_CANVAS")
password = os.getenv("PASSWORD_CANVAS")

# Global session object
session = HTMLSession()

def login_to_canvas():
    global session
    login_url = "https://tmcc.instructure.com/login/canvas"
    
    try:
        # Fetch the login page to get any hidden fields
        login_page = session.get(login_url)
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
        
        response = session.post(login_url, data=payload, headers=headers)
        response.raise_for_status()  # Raise exception for bad responses
        
        if "Invalid" in response.text or response.url == login_url:
            raise Exception("Login failed")
        else:
            print("Login successful")
    
    except Exception as e:
        print(f"Error during login: {str(e)}")
        raise  # Rethrow exception to terminate execution or handle as needed

def get_classes():
    global session
    dashboard_url = "https://tmcc.instructure.com/api/v1/users/self/favorites/courses"
    
    try:
        response = session.get(dashboard_url)
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
            student_class = StudentClass(class_name)
            student_classes.append(student_class)
            print(f"Class found: {class_name}")
            get_assignments(student_class, class_url)
        
        return student_classes
    
    except Exception as e:
        print(f"Error fetching classes: {str(e)}")
        raise  # Rethrow exception to terminate execution or handle as needed

def get_assignments(student_class, class_url):
    global session
    assignments_url = class_url + '/assignments?per_page=100'
    
    try:
        response = session.get(assignments_url)
        response.raise_for_status()  # Raise exception for bad responses
        
        assignments_data = json.loads(response.text)
        
        for assignment_data in assignments_data:
            assignment_name = assignment_data.get('name', 'No Title')
            due_date = assignment_data.get('due_at', 'No Due Date')
            
            assignment = Assignment(name=assignment_name, due_date=due_date)
            student_class.assignments.append(assignment)
            print(f"Assignment found: {assignment_name}, Due: {due_date}")
    
    except Exception as e:
        print(f"Error fetching assignments: {str(e)}")
        raise  # Rethrow exception to terminate execution or handle as needed

def main():
    try:
        login_to_canvas()
        student_classes = get_classes()
        print_user_classes(student_classes)
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
