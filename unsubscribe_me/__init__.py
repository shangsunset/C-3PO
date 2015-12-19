from flask import Flask
from flask_oauthlib.client import OAuth

app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')


oauth = OAuth(app)

gmail = oauth.remote_app(
    'gmail',
    consumer_key=app.config.get('GOOGLE_ID'),
    consumer_secret=app.config.get('GOOGLE_SECRET'),
    request_token_params={
        'scope': ['https://www.googleapis.com/auth/gmail.readonly', 'email']
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

from unsubscribe_me import views
