import os
import requests
import logging
from dotenv import load_dotenv, set_key
import time

def setup_logging():
    if not os.path.exists('logs'):
        os.makedirs('logs')
    logger = logging.getLogger('api_connection')
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler('logs/api_connection.log')
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

# Set up logging
logger = setup_logging()
logger.info("Logging setup complete.")

# Environment variables
load_dotenv()
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
cert_path = os.getenv("CERT_PATH")
base_url = os.getenv('BASE_URL')
auth_url = f"{base_url}/oauth/token"
access_token = os.getenv('ACCESS_TOKEN')
token_expiry = os.getenv('TOKEN_EXPIRY')

# Ensure all required environment variables are set
if not all([client_id, client_secret, cert_path, base_url]):
    logger.error("Missing one or more required environment variables.")
    raise EnvironmentError("Missing one or more required environment variables.")

def get_new_access_token():
    response = requests.post(auth_url, data={
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }, verify=cert_path)

    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data['access_token']
        expires_in = token_data['expires_in']
        token_expiry = str(time.time() + expires_in - 60)  # Subtract 60 seconds to ensure token is refreshed before it expires

        # Update .env file
        set_key('.env', 'ACCESS_TOKEN', access_token)
        set_key('.env', 'TOKEN_EXPIRY', token_expiry)

        logger.info("New access token obtained and stored.")
        return access_token
    else:
        logger.error(f"Failed to obtain access token. Status code: {response.status_code}")
        raise Exception("Failed to obtain access token.")

def get_api_connection():
    global access_token, token_expiry

    if access_token and token_expiry and time.time() < float(token_expiry):
        logger.info("Using stored access token.")
    else:
        logger.info("Stored access token is missing or expired. Requesting a new one.")
        access_token = get_new_access_token()

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    return headers