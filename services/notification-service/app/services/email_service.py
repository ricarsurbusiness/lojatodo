from typing import Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

from app.core.config import notification_settings


class EmailService:
    def __init__(self):
        self.sg = SendGridAPIClient(api_key=notification_settings.SENDGRID_API_KEY)
        self.from_email = Email(
            email=notification_settings.SENDGRID_FROM_EMAIL,
            name=notification_settings.SENDGRID_FROM_NAME
        )

    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
    ) -> tuple[Optional[str], Optional[str]]:
        message = Mail(
            from_email=self.from_email,
            to_emails=To(to_email),
            subject=subject,
            html_content=Content("text/html", body),
        )

        try:
            response = self.sg.send(message)
            return str(response.headers.get("X-Message-Id", "")), None
        except Exception as e:
            return None, str(e)


email_service = EmailService()
