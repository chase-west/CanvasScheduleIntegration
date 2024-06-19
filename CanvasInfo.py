import os
from dotenv import load_dotenv 
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from StudentClass import StudentClass
from StudentClass import Assignment

# Load environment variables
load_dotenv()
username = os.getenv("USERNAME_CANVAS")
password = os.getenv("PASSWORD_CANVAS")

# Set up the WebDriver
driver = webdriver.Chrome(service=Service('chromedriver.exe'))

try:
    # Open Canvas webpage
    driver.get("https://tmcc.instructure.com/")

    # Wait for username and password elements to appear
    wait = WebDriverWait(driver, 10)
    username_element = wait.until(EC.presence_of_element_located((By.ID, "pseudonym_session_unique_id")))
    password_element = wait.until(EC.presence_of_element_located((By.ID, "pseudonym_session_password")))

    # Input username and password
    username_element.send_keys(username)
    password_element.send_keys(password)
    password_element.send_keys(Keys.RETURN)

    try:
        # Wait for error element (if login fails)
        error_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.ic-flash__icon > i.icon-warning")))
        raise Exception("Error: Login failed or warning icon detected.")

    except TimeoutException:
        # If no error element found, proceed
        print("Login successful. Proceeding...")

    # Wait until the new page loads by waiting for a specific element
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ic-DashboardCard")))

    # Find all elements with class 'ic-DashboardCard__header_hero' (These are the class cards)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    class_elements = soup.find_all('div', class_='ic-DashboardCard__header_content')

    # Create array of student classes
    student_classes = []
    
    # Get name for each class you have
    def storeClassName():
      for class_element in class_elements:
        # Find the h3 tag inside the current div element
        h3_tag = class_element.find('h3', class_='ic-DashboardCard__header-title')
        
        # Check if h3_tag is found
        if h3_tag:
            # Extract the title attribute from the h3 tag
            class_name = h3_tag.get('title', '')
            class_name = class_name.split(' ', 1)
            class_name = class_name[1]
            student_class = StudentClass(class_name)
            student_classes.append(student_class)
        else:
            print("No classes found")
    storeClassName()

    # Print classes user is in 
    def printUserClasses():
        for student_class in student_classes:
            print(student_class.class_name)
            
    printUserClasses()



finally:
    # Close the browser session
    driver.quit()
