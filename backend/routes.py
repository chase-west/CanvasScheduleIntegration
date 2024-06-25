from flask import request, redirect, url_for
from requests_oauthlib import OAuth2Session
import os
from dotenv import load_dotenv

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
    @app.route("/login/microsoft")
    def login_microsoft():
        microsoft = OAuth2Session(microsoft_client_id, redirect_uri=microsoft_redirect_uri, scope=["Tasks.ReadWrite"])
        authorization_url, state = microsoft.authorization_url(microsoft_authorization_base_url)
        return redirect(authorization_url)

    @app.route("/callback/microsoft")
    def callback_microsoft():
        microsoft = OAuth2Session(microsoft_client_id, redirect_uri=microsoft_redirect_uri)
        token = microsoft.fetch_token(microsoft_token_url, client_secret=microsoft_client_secret, authorization_response=request.url)
        return token

    @app.route("/login/google")
    def login_google():
        google = OAuth2Session(google_client_id, redirect_uri=google_redirect_uri, scope=["https://www.googleapis.com/auth/calendar.readonly"])
        authorization_url, state = google.authorization_url(google_authorization_base_url, access_type="offline", prompt="consent")
        return redirect(authorization_url)

    @app.route("/callback/google")
    def callback_google():
        google = OAuth2Session(google_client_id, redirect_uri=google_redirect_uri)
        token = google.fetch_token(google_token_url, client_secret=google_client_secret, authorization_response=request.url)
        return token
