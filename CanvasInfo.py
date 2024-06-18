import os
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv 

# Load environment variables
load_dotenv()
username = os.getenv("USERNAME_CANVAS")
password = os.getenv("PASSWORD_CANVAS")
print(username)

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
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ic-DashboardCard__header_hero")))

    # Find all elements with class 'ic-DashboardCard__header_hero'
    class_elements = driver.find_elements(By.CLASS_NAME, "ic-DashboardCard__header_hero")

    # Create an array of these elements
    classes = [element.get_attribute('outerHTML') for element in class_elements]

    # Print the array of classes (just for demonstration)
    print(classes)

finally:
    # Close the browser session
    driver.quit()
