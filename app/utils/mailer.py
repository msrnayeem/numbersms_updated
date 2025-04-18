import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


def send_email(subject, recipient, body):
    # Retrieve email credentials and server configurations from .env
    sender = os.getenv("MAIL_DEFAULT_SENDER")
    password = os.getenv("MAIL_PASSWORD")
    mail_server = os.getenv("MAIL_SERVER")
    mail_port = int(os.getenv("MAIL_PORT"))

    # Create the email message
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    try:
        # Try connecting to the SMTP server with TLS
        print("Attempting TLS connection...")
        with smtplib.SMTP(mail_server, mail_port) as server:
            server.set_debuglevel(1)  # Enable detailed SMTP logs for debugging
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
            print("Email sent successfully using TLS!")
            return True
    except smtplib.SMTPAuthenticationError as auth_err:
        print("Authentication failed! Check your username and password.")
        return False
    except smtplib.SMTPException as smtp_err:
        print("TLS failed. Attempting SSL...")
        try:
            # Fallback to SSL if TLS fails
            with smtplib.SMTP_SSL(mail_server, mail_port) as server:
                server.login(sender, password)
                server.send_message(msg)
                print("Email sent successfully using SSL!")
                return True
        except Exception as ssl_err:
            print("Failed to send email using SSL as well.")
            return False
    except Exception as e:
        print("An unexpected error occurred:")
        return False
