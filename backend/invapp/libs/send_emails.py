from dotenv import load_dotenv
import requests
import os
from typing import List

load_dotenv()

class MailgunException(Exception):
    def __init__(self, message: str):
        super().__init__(message)

class Mailgun:
    DOMAIN_NAME = os.getenv("API_DOMAIN")
    API_KEY = os.getenv("API_KEY")

    @classmethod
    def send_email(cls, email: List[str], subject: str, text: str, html: str):
        if cls.API_KEY is None:
            raise MailgunException("Failed to load mailgun key")

        if cls.DOMAIN_NAME is None:
            raise MailgunException("Failed to load domain name")

        response = requests.post(
            f"https://api.mailgun.net/v3/{cls.DOMAIN_NAME}/messages",
            auth=("api", cls.API_KEY),
            data={"from": "Inventory Admin <kindredsolutions254@gmail.com>",
                  "to": email,
                  "subject": subject,
                  "text": text,
                  "html": html
                  }
        )

        if response.status_code != 200:
            raise MailgunException("Error in sending confirmation, user registration failed")

        return response