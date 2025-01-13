import requests
import os
import base64
import jsonify
from requests.auth import HTTPBasicAuth

# Phyllo API base URL
PHYLLO_BASE_URL = os.environ.get('PHYLLO_BASE_URL')

# Phyllo credentials from environment variables or your config file
PHYLLO_CLIENT_ID = os.environ.get('PHYLLO_CLIENT_ID')
PHYLLO_SECRET_ID = os.environ.get('PHYLLO_SECRET_ID')

# Function to generate the Authorization header for Phyllo API
def get_phyllo_auth_headers():
    auth_key = f"{PHYLLO_CLIENT_ID}:{PHYLLO_SECRET_ID}"
    encoded_auth_key = base64.b64encode(auth_key.encode()).decode()
    return {
        "Authorization": f"Basic {encoded_auth_key}",
        "Content-Type": "application/json",
    }

# Helper function to create a user in Phyllo
def create_phyllo_user(headers,name, external_id):
    url = f"{PHYLLO_BASE_URL}/v1/users"
    headers = headers
    payload = {
        "name": name,
        "external_id": external_id
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        print(response)
        response.raise_for_status()  # This will raise an error for bad responses
        print(response.json())
        return response.json()  # This should return the user object with Phyllo user ID
    except requests.exceptions.HTTPError as err:
        print(f"Error creating user in Phyllo: {err}")
        return None

# Helper function to create an SDK token in Phyllo
def create_phyllo_sdk_token(headers,user_id):
    url = f"{PHYLLO_BASE_URL}/v1/sdk-tokens"
    headers = headers
    payload = {
        "user_id": user_id,
        "products": [  
    "IDENTITY",
    "IDENTITY.AUDIENCE",
    "ENGAGEMENT",
    "ENGAGEMENT.AUDIENCE",
    "INCOME",
    "ACTIVITY"
  ] # Modify based on your use case
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()  # This will return the SDK token
    except requests.exceptions.HTTPError as err:
        print(f"Error creating SDK token in Phyllo: {err}")
        return None
    

import time

def letter_to_digit(letter):
    """Convert a letter to a digit (0-25) based on its position in the alphabet."""
    return ord(letter.lower()) - ord('a')

def sum_of_first_name_digits(first_name):
    """Calculate the sum of digits of the first name."""
    return sum(letter_to_digit(letter) for letter in first_name if letter.isalpha())

def generate_random_user_id(last_name, first_name):
    """Generate a random user ID based on the current time and the names provided."""
    # Get current time in seconds since epoch
    current_time = int(time.time())
    
    # Convert current time to a hexadecimal string (base-16)
    time_hex = hex(current_time)[2:]  # Remove the '0x' prefix
    
    # Calculate the sum of digits of the first name
    sum_first_name = sum_of_first_name_digits(first_name)
    
    # Combine both components to create the user ID
    user_id = f"{time_hex}-{sum_first_name}-{current_time}"
    
    return user_id


def get_user_data(user_id):
    """Fetch user data from Phyllo using the user ID."""
    try:
        # Construct the URL to fetch user data
        url = f"{PHYLLO_BASE_URL}/v1/users/{user_id}"
        
        # Make a GET request to the Phyllo API
        response = requests.get(url, auth=HTTPBasicAuth(PHYLLO_CLIENT_ID, PHYLLO_SECRET_ID))
        
        # Check if the request was successful
        if response.status_code == 200:
            return response.json()  # Return the user data as JSON
        else:
            print(f"Error fetching user data: {response.status_code} - {response.json()}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    

def get_platform_id(headers,platformName=None):
    if platformName is None:
        return ''
    # url= f"{PHYLLO_BASE_URL}/v1/work-platforms?name={platformName}"
    # response = requests.get(url, headers=headers)
    # print(response.json())
    # return response.json()['data']['id']


def phylloworkflow(firstname,lastname, platformName):
    phylloautheahers=get_phyllo_auth_headers()
    external_id=generate_random_user_id(firstname,lastname)
    print('external_id',external_id)
    user_id=create_phyllo_user(headers=phylloautheahers,name=f'{firstname} {lastname}',external_id= external_id)['id']
    print('user_id',user_id)
    sdk_token = create_phyllo_sdk_token(headers=phylloautheahers,user_id=user_id)['sdk_token']
    platform_id = get_platform_id(  headers=phylloautheahers, platformName=platformName)
    print('platform_id',platform_id)
    return user_id,sdk_token,platform_id


