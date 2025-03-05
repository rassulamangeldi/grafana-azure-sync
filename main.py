import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Microsoft Graph API and Grafana credentials
tenant_id = os.getenv('TENANT_ID')
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
grafana_api_key = os.getenv('GRAFANA_API_KEY')
grafana_url = os.getenv('GRAFANA_URL')

# Specify the group names or group IDs you want to sync
sync_groups = os.getenv('SYNC_GROUPS', '').split(',')

# Function to get an access token from Microsoft Graph
def get_microsoft_token():
    url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    body = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://graph.microsoft.com/.default'
    }
    response = requests.post(url, data=body, headers=headers)
    if response.status_code != 200:
        print(f"Error getting Microsoft token: {response.text}")
        return None
    print("Successfully obtained Microsoft token.")
    return response.json().get('access_token')

# Function to fetch Azure AD groups
def get_azure_groups(token):
    url = 'https://graph.microsoft.com/v1.0/groups'
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error getting Azure AD groups: {response.text}")
        return []
    print("Successfully fetched Azure AD groups.")
    return response.json().get('value', [])

# Function to fetch members of a specific Azure AD group
def get_group_members(group_id, token):
    url = f'https://graph.microsoft.com/v1.0/groups/{group_id}/members'
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error getting group members for group {group_id}: {response.text}")
        return []
    print(f"Successfully fetched members for group {group_id}.")
    return response.json().get('value', [])

# Function to get Grafana users by email to map userId for adding to teams
def get_grafana_users():
    url = f'{grafana_url}/api/org/users'
    headers = {'Authorization': f'Bearer {grafana_api_key}'}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching Grafana users: {response.text}")
        return []
    return response.json()

# Function to fetch Grafana teams
def get_grafana_teams():
    url = f'{grafana_url}/api/teams/search?perpage=1000&page=1'
    headers = {'Authorization': f'Bearer {grafana_api_key}'}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching Grafana teams: {response.text}")
        return []
    return response.json().get('teams', [])

# Function to update Grafana team members with userId
def update_grafana_team_members(team_id, members, grafana_users):
    url = f'{grafana_url}/api/teams/{team_id}/members'
    headers = {
        'Authorization': f'Bearer {grafana_api_key}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    # Map the emails from Azure AD members to Grafana userIds
    current_members = []
    for member in members:
        email = member.get('email') or member.get('userPrincipalName') 
        if email:
            # Find userId in Grafana for the corresponding email
            grafana_user = next((user for user in grafana_users if user['email'] == email), None)
            if grafana_user:
                current_members.append(grafana_user['userId'])

    # Fetch current team members
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching current team members for team {team_id}: {response.text}")
        return
    
    current_team_members = response.json()
    print(f"Grafana team members before sync for team {team_id}: {current_team_members}")

    # Log the current members of the team
    print(f"Comparing the following members from Azure AD with Grafana team members:")
    print(f"Azure AD group members: {current_members}")
    
    # Add new members (only those who are not already in the team)
    for user_id in current_members:
        if user_id not in [m['userId'] for m in current_team_members]:
            # Add user to Grafana team only if they are not already in the team
            data = {'userId': user_id}
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                print(f"Added userId {user_id} to Grafana team.")
            else:
                print(f"Error adding userId {user_id} to Grafana team: {response.text}")
    
    # Fetch and print the team members after syncing
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        current_team_members_after_sync = response.json()
        print(f"Grafana team members after sync for team {team_id}: {current_team_members_after_sync}")
    else:
        print(f"Error fetching current team members after sync for team {team_id}: {response.text}")


# Main sync function
def sync_teams():
    token = get_microsoft_token()
    if not token:
        return
    
    azure_groups = get_azure_groups(token)
    if not azure_groups:
        print("No Azure AD groups found.")
        return 
    
    grafana_teams = get_grafana_teams()
    if not grafana_teams:
        print("No teams found in Grafana.")
        return 

    # Loop through all the Azure AD groups
    for group in azure_groups:
        group_name = group.get('displayName', 'None')
        
        # Only log and sync specific groups in the sync_groups list
        if group_name in sync_groups:
            print(f"Checking Azure AD group: {group_name}")
            for team in grafana_teams:
                # Log the team name and group name to check if they match
                print(f"Checking if Azure AD group '{group_name}' matches Grafana team '{team['name']}'")
                if team['name'] == group_name:
                    print(f"Syncing group {group_name} with Grafana team {team['name']}.")
                    members = get_group_members(group['id'], token)
                    grafana_users = get_grafana_users()
                    update_grafana_team_members(team['id'], members, grafana_users)
                else:
                    print(f"Skipping sync: Group '{group_name}' does not match Grafana team '{team['name']}'.")
        else:
            # Skip logging for groups not in the sync_groups list
            continue

sync_teams()
