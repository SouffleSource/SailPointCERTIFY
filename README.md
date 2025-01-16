# SailPointCERTIFY

Automate the creation and activation of role-based certification campaigns using the SailPoint IdentityNow API.

## Project Structure

- **activate_certifications.py**: Script to activate staged certification campaigns.
- **api_connection.py**: Contains functions to handle API connections and obtain access tokens.
- **create_certifications.py**: Script to create new role-based certification campaigns.
- **.env**: Environment variables for API credentials and base URL.
- **README.md**: Project documentation.

## Setup

1. Clone the repository.
2. Create a virtual environment and activate it.
3. Create a `.env` file in the root directory with the following content:
    ```env
        CLIENT_ID={id}
        CLIENT_SECRET={secret}
        BASE_URL=https://tenantname.api.identitynow.com/
        CERT_PATH=domain.com.ca-bundle
        OWNER=John Doe # Set the name of the remediator
        OWNER_ID=867804d367rd4d72902f85bd5fcfdd32 # Set the ID of the remediator
        DEADLINE=2025-12-25T00:00:00.000Z # Set the deadline for the certifications
    ```
> [!NOTE] 
> You only need to configure CERT_PATH if your organisation uses SSL/TLS inspection on its firewalls.

## Usage
### Create Certifications

#### Configure role areas
The script is currently configured to determine Role Area by splitting the role's name at certain characters (-, |) and taking the first part. This part is then stripped of any leading or trailing whitespace. This works for role name formatting like:
```
Finance - Banking
Finance - Accounts
Finance - Treasury
```
or 
```
Technology | Frontend
Technology | Backend
Technolgy | DevOps
```
If there are multiple role owners in a single area the script will create multiple certifications for the role area - one for each owner with the roles they own from that area. 

To create new role-based certification campaigns, run the following command:
```sh
python create_certifications.py
```

### Activate Certifications

To activate staged certification campaigns, run the following command:
```sh
python activate_certifications.py
```

## Logging

Logs are stored in the `logs` directory. Each script creates its own log file with detailed information about the execution including the POST requests with the request body for each certification request to aid format debugging. 

## License

This project is licensed under the MIT License.

