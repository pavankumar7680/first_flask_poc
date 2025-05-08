import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_success_email():
    from_email = "pavankumarkandighsl@gmail.com"
    to_email = "pavankumarkandighsl@gmail.com"
    from_password = "xakinxwibvdynqam"  # Gmail App Password

    subject = "Customer Data Insertion Success"
    body = (
    "Hello,\n\n"
    "We’re happy to inform you that the customer data has been successfully inserted into the database.\n\n"
    "Thank you for your continued support.\n\n"
    "Best regards,\n"
    "Pavan Kumar"
)

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(from_email, from_password)
        server.send_message(msg)
        server.quit()
        print("✅ Email sent successfully")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
