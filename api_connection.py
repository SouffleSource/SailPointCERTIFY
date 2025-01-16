import os
import requests
import logging
from dotenv import load_dotenv

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

# Ensure all required environment variables are set
if not all([client_id, client_secret, cert_path, base_url]):
    logger.error("Missing one or more required environment variables.")
    raise EnvironmentError("Missing one or more required environment variables.")

def get_access_token():
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    }
    try:
        response = requests.post(auth_url, data=data, verify=cert_path)
        if response.status_code == 200:
            logger.info("Successfully obtained access token.")
            return response.json().get('access_token')
        else:
            logger.error(f"Failed to obtain access token. Status code: {response.status_code}")
            logger.error(f"Response content: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Exception occurred while obtaining access token: {e}")
        return None

def get_api_connection():
    access_token = get_access_token()
    if access_token:
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f"Bearer {access_token}",
        }
        logger.info("Successfully created API connection headers.")
        return headers
    else:
        logger.error("Failed to obtain access token.")
        raise ConnectionError("Failed to obtain access token.")