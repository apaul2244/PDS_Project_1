import os

class Config:
    SECRET_KEY = os.urandom(24)
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = ''
    MYSQL_DB = 'mydb'



# config.py

#import os

# Set secret keys for OAuth
os.environ['GOOGLE_OAUTH_CLIENT_ID'] = 'your_google_client_id'
os.environ['GOOGLE_OAUTH_CLIENT_SECRET'] = 'your_google_client_secret'

os.environ['FACEBOOK_OAUTH_CLIENT_ID'] = 'your_facebook_client_id'
os.environ['FACEBOOK_OAUTH_CLIENT_SECRET'] = 'your_facebook_client_secret'
