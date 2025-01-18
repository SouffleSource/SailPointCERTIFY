import requests
import os
import logging
import time
from dotenv import load_dotenv
from api_connection import get_api_connection

def setup_logging():
    if not os.path.exists('logs'):
        os.makedirs('logs')
    logger = logging.getLogger('activate_certifications')
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler('logs/activate_certifications.log')
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

# Set up logging
logger = setup_logging()
logger.info("Logging setup complete.")

# Environment variables
load_dotenv()
base_url = os.getenv('BASE_URL')
cert_path = os.getenv('CERT_PATH')
campaigns_url = f"{base_url}/v3/campaigns"

# Ensure all required environment variables are set
if not all([base_url, cert_path]):
    logger.error("Missing one or more required environment variables.")
    raise EnvironmentError("Missing one or more required environment variables.")

# Obtain API connection headers
headers = get_api_connection()

def list_campaigns(headers):
    response = requests.get(campaigns_url, headers=headers, verify=cert_path)
    if response.status_code == 200:
        logger.info("Successfully listed campaigns.")
        return response.json()
    else:
        logger.error(f"Failed to list campaigns. Status code: {response.status_code}")
        return []

def activate_campaign(base_url, headers, campaign_id, campaign_name):
    activate_url = f"{base_url}/v3/campaigns/{campaign_id}/activate"
    response = requests.post(activate_url, headers=headers, verify=cert_path)
    if response.status_code == 200:
        logger.info(f"Campaign {campaign_name} ID:{campaign_id} activated successfully.")
    elif response.status_code == 202:
        logger.info(f"Activating the Campaign {campaign_name} ID:{campaign_id}.")
    else:
        logger.error(f"Failed to activate Campaign {campaign_name} ID:{campaign_id}. Status code: {response.status_code}")

def check_campaign_status(base_url, headers, campaign_id, campaign_name):
    status_url = f"{base_url}/v3/campaigns/{campaign_id}"
    while True:
        response = requests.get(status_url, headers=headers, verify=cert_path)
        if response.status_code == 200:
            campaign_status = response.json().get('status')
            if campaign_status == 'ACTIVE':
                logger.info(f"Campaign {campaign_name} ID:{campaign_id} is now active.")
                break
            else:
                logger.info(f"Campaign {campaign_name} ID:{campaign_id} status: {campaign_status}. Checking again in 30 seconds.")
                time.sleep(30)
        else:
            logger.error(f"Failed to check status for Campaign {campaign_name} ID:{campaign_id}. Status code: {response.status_code}")
            break

def main():
    campaigns = list_campaigns(headers)
    staged_campaigns = [campaign for campaign in campaigns if campaign.get('status') == 'STAGED']
    
    for campaign in staged_campaigns:
        activate_campaign(base_url, headers, campaign.get('id'), campaign.get('name'))
    
    for campaign in staged_campaigns:
        check_campaign_status(base_url, headers, campaign.get('id'), campaign.get('name'))

if __name__ == "__main__":
    main()