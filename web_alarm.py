import os
import requests
import json
from msal import ConfidentialClientApplication

def check_website_status(url):
    """
    Checks the status of a given website URL.
    Sends an email notification with the result.
    """
    try:
        # Use a timeout to prevent the script from hanging indefinitely
        response = requests.get(url, timeout=10, verify=False)
        
        # Check for a successful status code (e.g., 200 OK)
        if response.status_code >= 200 and response.status_code < 300:
            print(f"Success: {url} returned status code {response.status_code}")
            # Optional: You could choose not to send an email on success
            # send_email_notification(f"Website Up: {url} is online.")
        else:
            print(f"Failure: {url} returned status code {response.status_code}")
            send_email_notification(f"Website Alert: {url} returned status code {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error: Could not connect to {url}. Error: {e}")
        send_email_notification(f"Website Alert: {url} is unreachable.")

def send_email_notification(subject):
    """
    Authenticates with Microsoft Graph API and sends an email notification.
    """
    # Credentials from your Azure App Registration
    tenant_id = os.environ.get("TENANT_ID")
    client_id = os.environ.get("CLIENT_ID")
    client_secret = os.environ.get("CLIENT_SECRET")
    
    # Email details
    sender_email = os.environ.get("SENDER_EMAIL")
    receiver_email = os.environ.get("RECEIVER_EMAIL")

    if not all([tenant_id, client_id, client_secret, sender_email, receiver_email]):
        print("Error: Required environment variables for sending email are not set.")
        return

    # 1. Authenticate and acquire an access token from Microsoft Entra
    authority = f"https://login.microsoftonline.com/{tenant_id}"
    app = ConfidentialClientApplication(
        client_id,
        authority=authority,
        client_credential=client_secret
    )
    
    scopes = ["https://graph.microsoft.com/.default"]
    token_result = app.acquire_token_silent(scopes=scopes, account=None)
    
    if not token_result:
        token_result = app.acquire_token_for_client(scopes=scopes)

    if "access_token" not in token_result:
        print("Error: Failed to acquire access token.")
        print(f"Description: {token_result.get('error_description')}")
        return

    # 2. Prepare the email message for the Graph API
    graph_api_endpoint = f"https://graph.microsoft.com/v1.0/users/{sender_email}/sendMail"
    
    headers = {
        'Authorization': f'Bearer {token_result["access_token"]}',
        'Content-Type': 'application/json'
    }

    email_payload = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "Text",
                "content": f"This is an automated alert from your website monitoring script.\n\nDetails: {subject}"
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": receiver_email
                    }
                }
            ]
        },
        "saveToSentItems": "true"
    }

    # 3. Send the email using a POST request
    try:
        response = requests.post(
            graph_api_endpoint, 
            headers=headers, 
            data=json.dumps(email_payload)
        )
        
        # A 202 'Accepted' status code means the request was successful
        if response.status_code == 202:
            print("Email notification sent successfully via Graph API!")
        else:
            print(f"Error sending email: {response.status_code}")
            print(response.json()) # Print the error response from the API
            
    except Exception as e:
        print(f"An exception occurred while sending the email: {e}")

if __name__ == "__main__":
    # Get the URL to check from an environment variable
    website_to_check = os.environ.get("WEBSITE_URL")
    
    if website_to_check:
        print(f"Starting check for {website_to_check}...")
        check_website_status(website_to_check)
    else:
        print("Error: WEBSITE_URL environment variable is not set.")
