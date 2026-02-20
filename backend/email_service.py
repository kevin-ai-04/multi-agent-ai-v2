import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
import os
from dotenv import load_dotenv
from backend.database import save_emails

# Load environment variables
load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
IMAP_SERVER = "imap.gmail.com"
SMTP_SERVER = "smtp.gmail.com"

class EmailService:
    def __init__(self):
        self.email_user = EMAIL_USER
        self.email_pass = EMAIL_PASS

    def fetch_emails(self, folder="INBOX", limit=20):
        """
        Fetches emails from the specified folder via IMAP.
        Saves them to the database and returns the list.
        """
        try:
            # Connect to IMAP
            mail = imaplib.IMAP4_SSL(IMAP_SERVER)
            mail.login(self.email_user, self.email_pass)
            
            # Select folder
            # Note: Gmail specific folders might need mapping (e.g. "[Gmail]/Sent Mail")
            imap_folder = folder
            if folder.lower() == "sent":
                imap_folder = '"[Gmail]/Sent Mail"'
            elif folder.lower() == "trash":
                 imap_folder = '"[Gmail]/Trash"'
            elif folder.lower() == "drafts":
                 imap_folder = '"[Gmail]/Drafts"'
            
            status, messages = mail.select(imap_folder)
            if status != "OK":
                return []

            # Search for all emails
            # fetch the last N emails
            search_criterion = "ALL"
            status, data = mail.search(None, search_criterion)
            mail_ids = data[0].split()
            
            # Get latest 'limit' emails
            latest_email_ids = mail_ids[-limit:]
            latest_email_ids.reverse() # Newest first

            email_list = []

            for i in latest_email_ids:
                try:
                    status, msg_data = mail.fetch(i, "(RFC822)")
                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part[1])
                            
                            # Decode Subject
                            subject, encoding = decode_header(msg["Subject"])[0]
                            if isinstance(subject, bytes):
                                subject = subject.decode(encoding if encoding else "utf-8")
                            
                            # Decode Sender
                            sender = msg.get("From")
                            
                            # Date
                            date = msg.get("Date")

                            # Body Preview
                            body = ""
                            if msg.is_multipart():
                                for part in msg.walk():
                                    content_type = part.get_content_type()
                                    content_disposition = str(part.get("Content-Disposition"))
                                    try:
                                        payload = part.get_payload(decode=True)
                                        if payload:
                                            decoded_payload = payload.decode(errors="ignore")
                                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                                body += decoded_payload
                                            elif content_type == "text/html" and "attachment" not in content_disposition:
                                                 # Strip HTML tags for preview (rudimentary)
                                                 pass 
                                    except:
                                        pass
                            else:
                                try:
                                    payload = msg.get_payload(decode=True)
                                    if payload:
                                        body = payload.decode(errors="ignore")
                                except:
                                    pass
                            
                            # Fallback if body empty
                            if not body:
                                body = "(No content or HTML only)"

                            email_list.append({
                                "id": str(int(i)), # IMAP ID
                                "subject": subject,
                                "sender": sender,
                                "date": date,
                                "body": body[:500] + "..." if len(body) > 500 else body, # Preview
                                "folder": folder
                            })
                except Exception as e:
                    print(f"Error parsing email {i}: {e}")
                    continue

            mail.close()
            mail.logout()
            
            # Save to database
            save_emails(email_list)
            
            return email_list

        except Exception as e:
            print(f"IMAP Error: {e}")
            return []

    def send_email(self, to_email, subject, body):
        """
        Sends an email via SMTP.
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(SMTP_SERVER, 587)
            server.starttls()
            server.login(self.email_user, self.email_pass)
            text = msg.as_string()
            server.sendmail(self.email_user, to_email, text)
            server.quit()
            return True
        except Exception as e:
            print(f"SMTP Error: {e}")
            return False
