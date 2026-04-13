import requests

from config import Settings


class EmailService:
    """
    Uses Resend because that is what you configured.
    WARNING: assignment PDF explicitly says SendGrid or Gmail API.
    Keep this if your instructor allows equivalent providers, otherwise swap this file.
    """

    def __init__(self) -> None:
        self.api_key = Settings.RESEND_API_KEY
        self.from_email = Settings.RESEND_FROM_EMAIL
        self.to_email = Settings.RESEND_TO_EMAIL
        self.url = "https://api.resend.com/emails"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def send_email(self, subject: str, html: str) -> dict:
        payload = {
            "from": self.from_email,
            "to": [self.to_email],
            "subject": subject,
            "html": html,
        }
        response = requests.post(self.url, headers=self.headers, json=payload, timeout=60)
        if response.status_code >= 400:
            raise RuntimeError(f"Resend API error {response.status_code}: {response.text}")
        return response.json()