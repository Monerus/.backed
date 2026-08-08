from aiosmtplib import SMTP
from email.message import EmailMessage
from core.config import settings


async def send_email_code(email: str, code: int):
    message = EmailMessage()
    message["From"] = settings.SMTP_FROM
    message["To"] = email
    message["Subject"] = "Ваш код подтверждения"
    message.set_content(f"Ваш код для входа: {code}. Он действителен 3 минуты.")


    smtp = SMTP(
    hostname=settings.SMTP_HOST,
    port=settings.SMTP_PORT,
    use_tls=True,

)

    await smtp.connect()
    print("connected")

    await smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
    print("logged in")

    await smtp.send_message(message)
    await smtp.quit()