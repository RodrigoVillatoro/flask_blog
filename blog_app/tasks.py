import email
import email.mime.application
import email.mime.multipart
import email.mime.text
import smtplib

from config_secret import *


def send_password_verification(recovery_email, verification_code):
    body = 'Your password verification code is: {}'.format(verification_code)

    msg = email.mime.multipart.MIMEMultipart()
    msg['From'] = MAIL_USERNAME
    msg['Subject'] = 'Forgotten password'
    msg['To'] = ', '.join(recovery_email)
    body = email.mime.text.MIMEText(body)
    msg.attach(body)

    # SMTP
    smtp_obj = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)
    smtp_obj.ehlo()
    smtp_obj.starttls()
    smtp_obj.login(MAIL_USERNAME, MAIL_PASSWORD)
    smtp_obj.sendmail(MAIL_USERNAME, recovery_email, msg.as_string())
    smtp_obj.quit()