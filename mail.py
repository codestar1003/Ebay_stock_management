import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_mail(FROM, PSW, TO, title, text):
    server = smtplib.SMTP(host="smtp.office365.com", port = 587)
    server.starttls()
    server.login(FROM, PSW)

    msg = MIMEMultipart("alternative")
    msg["From"] = FROM
    msg["To"] = TO
    msg["Subject"] = title

    text_part = MIMEText(text, "plain")
    msg.attach(text_part)
    
    server.sendmail(FROM, TO, msg.as_string())
    server.quit()
