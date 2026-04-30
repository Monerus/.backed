import smtplib 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sender_email = "monerus2020@gmail.com"
app_password = "vxej kyzc fbmg jkrd"
receiver_email = "recipient@example.com"


message = MIMEMultipart()
message["FROM"] = sender_email
message["TO"] = receiver_email
message["Subject"] = "Тестовое письмо через Gmail SMTP"


body = "Hello! you code: .."
message.attach(MIMEText(body, "plain"))