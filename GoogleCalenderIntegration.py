from gcsa.google_calendar import GoogleCalendar
from dotenv import load_dotenv 
import os

# Load environment variables
load_dotenv()

user_email = os.getenv('GOOGLE_CALENDER_EMAIL')

calendar = GoogleCalendar('your_email@gmail.com')
for event in calendar:
    print(event)