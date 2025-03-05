# Grafana Sync - Entra ID Groups to Grafana Teams

This open-source project syncs **Microsoft Entra ID** (formerly Azure Active Directory) groups with **Grafana teams**.

## Features
- Sync users from Microsoft Entra ID groups to Grafana teams.
- Add users based on their group membership in Entra ID.

## Docker Setup

### Prerequisites
- Docker installed on your machine.
- Grafana API Key (with Editor or Admin privileges).
- Microsoft Entra ID API credentials (Client ID, Tenant ID, Client Secret).

### How to Build and Run

You can either build the Docker image from the source or use the pre-built Docker image hosted on DockerHub. Here's how to use both methods.

#### **Option 1: Using Pre-built Docker Image**

You can use the pre-built Docker image directly without building it yourself. All you need to do is set the environment variables.

1. **Set Environment Variables:**

Create a `.env` file with the following variables:

```env
TENANT_ID=your_tenant_id
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
GRAFANA_API_KEY=your_grafana_api_key
GRAFANA_URL=your_grafana_url
SYNC_GROUPS=your_group_1,your_group_2
```

2. **Run the Docker container:**
After setting up the .env file, run the Docker container:

```bash
docker run --env-file .env --rm rassulamanngeldi/grafana-azure-sync:latest
```

This will run the synchronization process, syncing Entra ID groups with Grafana teams.

#### **Option 2: Building Docker Image from Source**
If you prefer to build the Docker image yourself, follow these steps:

1. **Clone this repository:**

```bash
git clone https://github.com/rassulamangeldi/grafana-azure-sync.git
cd grafana-azure-sync
```

2. **Build the Docker Image:**

```bash
docker build -t grafana-azure-sync:latest .
```

3. **Create a .env file:**

```env
TENANT_ID=your_tenant_id
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
GRAFANA_API_KEY=your_grafana_api_key
GRAFANA_URL=your_grafana_url
SYNC_GROUPS=your_group_1,your_group_2
```

4. **Run the Docker container:**
```bash
docker run --env-file .env --rm grafana-azure-sync:latest
```

## How It Works:

- The project fetches Microsoft Entra ID groups using the Microsoft Graph API.
- It fetches Grafana teams using the Grafana API.
- It compares the Azure AD groups with Grafana teams.
- It adds users to the Grafana teams based on their membership in the Azure AD groups.

## Limitations and Considerations:
- Grafana Permissions: To use this script, your Grafana API Key must have sufficient permissions (Editor or Admin level).
- Microsoft Entra ID Permissions: Your Microsoft Entra ID application (using Client ID and Client Secret) needs to have the proper permissions (such as Group.Read.All) to read the groups and members from Azure AD.
- Grafana Team Permissions: The script assumes that teams exist in Grafana and will attempt to sync users accordingly. Ensure teams are created before running the sync.
- Rate Limits: Both Microsoft Graph API and Grafana API have rate limits. If you're working with a large number of users or teams, you might hit those limits. Consider handling API rate limits by adding retry logic.
- Environment Variables: Make sure to set up all the necessary environment variables (TENANT_ID, CLIENT_ID, CLIENT_SECRET, GRAFANA_API_KEY, GRAFANA_URL) before running the container. Incorrect or missing values may cause the script to fail.

## Contributing:
Feel free to fork this project, create issues, and submit pull requests. Contributions are welcome!