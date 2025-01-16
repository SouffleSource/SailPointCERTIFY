import requests
import json
import time
import os
import logging
from collections import defaultdict
from dotenv import load_dotenv
from api_connection import get_api_connection

def setup_logging():
    """Set up logging configuration."""
    if not os.path.exists('logs'):
        os.makedirs('logs')
    timestamp = time.strftime("%Y.%m.%d.%H.%M")
    logger = logging.getLogger('campaigns')
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(f'logs/campaigns_{timestamp}.log')
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

# Set up logging
logger = setup_logging()

# Environment variables
load_dotenv()
base_url = os.getenv('BASE_URL')
cert_path = os.getenv("CERT_PATH")
owner = os.getenv("OWNER")
owner_id = os.getenv("OWNER_ID")
deadline = os.getenv("DEADLINE")
year = deadline[:4]
roles_url = f"{base_url}/v3/roles"
campaigns_url = f"{base_url}/v3/campaigns"
headers = get_api_connection()

# Ensure all required environment variables are set
if not all([base_url, cert_path, owner, owner_id, deadline]):
    logger.error("Missing one or more required environment variables.")
    raise EnvironmentError("Missing one or more required environment variables.")

def fetch_roles(headers: dict, roles_url: str) -> list:
    """Fetch roles from the API."""
    offset = 0
    limit = 100
    roles_data = []

    while True:
        response = requests.get(f"{roles_url}?offset={offset}&limit={limit}", headers=headers, verify=cert_path)
        if response.status_code == 200:
            batch_roles = response.json()
            if not batch_roles:
                break
            roles_data.extend(batch_roles)
            offset += limit
        else:
            logger.error(f"Failed to fetch roles. Status code: {response.status_code}")
            break

    return roles_data

def organise_roles_by_area(roles_data: list) -> dict:
    roles_by_area = defaultdict(list)
    
    for role in roles_data:
        if isinstance(role.get('owner'), dict):  # Ensure owner is a dictionary
            role_owner_id = role['owner'].get('id')
            role_owner_name = role['owner'].get('name')
            role_id = role.get('id')
            role_name = role.get('name', '')
            role_area = role_name.split('- ')[0].split('|')[0].split('-')[0].strip()
            
            if role_owner_id and role_owner_name:
                roles_by_area[(role_area, role_owner_id, role_owner_name)].append((role_id, role_name))
    
    return roles_by_area

def create_role_campaign(headers: dict, campaigns_url: str, role_area: str, role_owner_name: str, role_owner_id: str, roles: list):
    role_names = ', '.join([role_name for _, role_name in roles])
    role_ids = [role_id for role_id, _ in roles]
    campaign_name = f"{role_area} Role Certification's for {role_owner_name} {year}"
    campaign_data = {
        "name": f"{campaign_name}",
        "description": f"Certification campaign for roles in {role_area} owned by {role_owner_name}. Roles: {role_names}",
        "type": "ROLE_COMPOSITION",
        "emailNotificationEnabled": False,
        "deadline": f"{deadline}",
        "roleCompositionCampaignInfo": {
            "remediatorRef": {
                "type": "IDENTITY",
                "id": f"{owner_id}",
                "name": f"{owner}"
            },
            "reviewerId": f"{role_owner_id}",
            "reviewer": {
                "type": "IDENTITY",
                "id": f"{role_owner_id}",
                "name": f"{role_owner_name}",
            },
            "roleIds": role_ids,
        },
        "mandatoryCommentRequirement": "NO_DECISIONS"
    }

    response = requests.post(campaigns_url, headers=headers, data=json.dumps(campaign_data), verify=cert_path)
    time.sleep(1)  # Rate limiting requests

    # Log the campaign details
    logger.info("----")
    logger.info(f"Campaign Name: {campaign_name}")
    logger.info(f"Response Status Code: {response.status_code}")
    logger.info(f"Request Body: {json.dumps(campaign_data, indent=4)}")
    logger.info("----")

    if response.status_code in [200, 201]:
        print(f"{campaign_name} created successfully.")
    else:
        print(f"Failed to create {campaign_name}. Status code: {response.status_code}")

def get_roles_and_create_campaigns(headers: dict, roles_url: str, campaigns_url: str):
    """Fetch roles and create campaigns."""
    roles_data = fetch_roles(headers, roles_url)
    if not roles_data:
        return

    roles_by_area = organise_roles_by_area(roles_data)

    for (role_area, role_owner_id, role_owner_name), roles in roles_by_area.items():
        create_role_campaign(headers, campaigns_url, role_area, role_owner_name, role_owner_id, roles)

def main():
    get_roles_and_create_campaigns(headers, roles_url, campaigns_url)

if __name__ == "__main__":
    main()