import os
import requests
import smtplib
from email.message import EmailMessage

def check_website_status(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            send_email_notification(f"Website Up: {url} returned status code {response.status_code}")
        else:
            send_email_notification(f"Website Down: {url} returned status code {response.status_code}")
    except requests.exceptions.RequestException as e:
        send_email_notification(f"Website Down: {url} is unreachable. Error: {e}")

def send_email_notification(subject):
    sender_email = os.environ.get("SENDER_EMAIL")
    receiver_email = os.environ.get("RECEIVER_EMAIL")
    password = os.environ.get("EMAIL_PASSWORD")

    if not all([sender_email, receiver_email, password]):
        print("Email credentials are not set as environment variables.")
        return

    msg = EmailMessage()
    msg.set_content(subject)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, password)
        server.send_message(msg)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

check_website_status("https://www.weitzman.info")
