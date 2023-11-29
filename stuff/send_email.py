import smtplib
import os
import sys
import base64
from email.message import EmailMessage


# USAGE: python send_email.py "recipient@example.com" "Your Subject" "Your email body."

def send_email(subject, body, to, from_email, password, smtp_server, port):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to

    server = smtplib.SMTP(smtp_server, port)
    server.starttls()
    server.login(from_email, password)
    server.send_message(msg)
    server.quit()


def xor_decryption(encrypted_text, key):
    # Decode the encrypted text from Base64
    encrypted_bytes = base64.b64decode(encrypted_text)

    decrypted_text = ""
    for i in range(len(encrypted_bytes)):
        decrypted_text += chr(encrypted_bytes[i] ^ ord(key[i % len(key)]))

    return decrypted_text


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python send_email.py <recipient's email address> <subject> <body>")
        sys.exit(1)

    to = sys.argv[1]
    subject = sys.argv[2]
    body = sys.argv[3]
    from_email = os.environ.get('EMAIL_USER')
    password = xor_decryption(os.environ.get('EMAIL_PASS'), 'key')
    smtp_server = "smtp-mail.outlook.com"  # Change to your SMTP server
    port = 587  # Change to your SMTP server port

    send_email(subject, body, to, from_email, password, smtp_server, port)
