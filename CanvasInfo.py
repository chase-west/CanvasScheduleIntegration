import os
from dotenv import load_dotenv 
load_dotenv()

canvas_api_key = os.getenv('CANVAS_API_KEY')
print(canvas_api_key)
