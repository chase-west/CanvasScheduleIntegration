import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import json
from StudentClass import StudentClass, Assignment

# Load environment variables
load_dotenv()
username = os.getenv("USERNAME_CANVAS")
password = os.getenv("PASSWORD_CANVAS")

# Start a session
session = requests.Session()

def login_to_canvas():
    login_url = "https://tmcc.instructure.com/login/canvas"
    
    # Fetch the login page to get any hidden fields
    login_page = session.get(login_url)
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
    
    if "Invalid" in response.text or response.url == login_url:
        raise Exception("Login failed")
    else:
        print("Login successful")

def get_classes():
    dashboard_url = "https://tmcc.instructure.com/api/v1/users/self/favorites/courses"
    response = session.get(dashboard_url)
    courses_data = json.loads(response.text)
    student_classes = []

    if not courses_data:
        print("No classes found or unable to locate classes.")
        return student_classes

    for course in courses_data:
        class_name = course.get('short_name') or course.get('name', 'No Name')
        class_url = f"https://tmcc.instructure.com/courses/{course['id']}"
        student_class = StudentClass(class_name)
        student_classes.append(student_class)
        print(f"Class found: {class_name}")
        get_assignments(student_class, class_url)
        
    return student_classes

def get_assignments(student_class, class_url):
    assignments_url = class_url + '/assignments'
    response = session.get(assignments_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    assignments = soup.find_all('div', class_='ig-row__layout')

    if not assignments:
        print(f"No assignments found for class: {student_class.class_name}")

    for assignment_element in assignments:
        assignment_name_element = assignment_element.find('a', class_='ig-title')
        assignment_name = assignment_name_element.get_text(strip=True) if assignment_name_element else 'No title'
        
        due_date_element = assignment_element.find('div', class_='assignment-date-due')
        assignment_due_date = due_date_element.find('span', {'aria-hidden': 'true'}).get_text(strip=True) if due_date_element else 'No due date'
        
        assignment = Assignment(name=assignment_name, due_date=assignment_due_date)
        student_class.assignments.append(assignment)
        print(f"Assignment found: {assignment_name}, Due: {assignment_due_date}")

def main():
    login_to_canvas()
    student_classes = get_classes()
    print_user_classes(student_classes)

def print_user_classes(student_classes):
    for student_class in student_classes:
        print(student_class.class_name)
        for assignment in student_class.assignments:
            print(f" - {assignment.name}, Due: {assignment.due_date}")

if __name__ == "__main__":
    main()
