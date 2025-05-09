import shutil
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


shutil.rmtree("__pycache__", ignore_errors=True)

#---------------------------------------------------
# success email for Data Insertion
#---------------------------------------------------

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_success_email():
    from_email = "pavankumarkandighsl@gmail.com"
    to_email = "pavankumarkandighsl@gmail.com"
    from_password = "xakinxwibvdynqam" 

    subject = "Customer Data Insertion Success"
    
    # HTML formatted body with bold text and other styling
    body = """
    <html>
    <body>
        <p>Hello,</p>
        <p>We’re happy to inform you that the <strong>customer data</strong> has been successfully inserted into the database.</p>
        <p><strong>Thank you for your continued support.</strong></p>
        <p>Best regards,<br>
        Support Team</p>
    </body>
    </html>
    """

    # Create the message container
    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject

    # Attach the HTML body to the email message
    msg.attach(MIMEText(body, "html"))

    try:
        # Set up the SMTP server and send the email
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(from_email, from_password)
        server.send_message(msg)
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")


#---------------------------------------------------
# success email for update_name
#---------------------------------------------------
def send_name_update_email(old_name, new_name):
    from_email = "pavankumarkandighsl@gmail.com"
    to_email = "pavankumarkandighsl@gmail.com"
    from_password = "xaki nxwi bvdy nqam"  # Use app password

    subject = "Customer Name Updated Successfully"
    
    # HTML formatted body with bold, italics, and other styling
    body = f"""
    <html>
    <body>
        <p>Hello <strong>{old_name}</strong>,</p>
        <p>In our database, your name has been successfully updated to <span style="font-weight: bold; color: #4CAF50;">{new_name}</span>.</p>
        <p>Thank you for keeping your information up to date.</p>
        <br>
        <p><em>Best regards,</em><br><strong>Support Team</strong></p>
    </body>
    </html>
    """
    
    # Create the message container
    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject

    # Attach the HTML body to the email message
    msg.attach(MIMEText(body, "html"))

    try:
        # Set up the SMTP server and send the email
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(from_email, from_password)
        server.send_message(msg)
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")
#---------------------------------------------------
# success email for address_update
#---------------------------------------------------
        
def send_address_update_email(
        old_street_1, old_street_2, old_city, old_state, old_pincode,
        new_street_1, new_street_2, new_city, new_state, new_pincode,
        updated_street_1, updated_street_2, updated_city, updated_state, updated_pincode,
        customer_id_fk):
    from_email = "pavankumarkandighsl@gmail.com"
    to_email = "pavankumarkandighsl@gmail.com"  # You can adjust this as needed
    from_password = "xaki nxwi bvdy nqam"  # Be cautious with hardcoding passwords

    subject = "Customer Address Updated Successfully"
    
    # HTML formatted body with a table for the address details
    body = f"""
    <html>
    <body>
        <p>Hello,</p>
        <p>The customer's address has been successfully updated in the database.</p>
        
        <h3>Old Address:</h3>
        <table border="1" cellpadding="5" cellspacing="0">
            <tr>
                <th>Street 1</th>
                <th>Street 2</th>
                <th>City</th>
                <th>State</th>
                <th>Pincode</th>
            </tr>
            <tr>
                <td>{old_street_1}</td>
                <td>{old_street_2}</td>
                <td>{old_city}</td>
                <td>{old_state}</td>
                <td>{old_pincode}</td>
            </tr>
        </table>

        <h3>Updated Address:</h3>
        <table border="1" cellpadding="5" cellspacing="0">
            <tr>
                <th>Street 1</th>
                <th>Street 2</th>
                <th>City</th>
                <th>State</th>
                <th>Pincode</th>
            </tr>
            <tr>
                <td>{updated_street_1}</td>
                <td>{updated_street_2}</td>
                <td>{updated_city}</td>
                <td>{updated_state}</td>
                <td>{updated_pincode}</td>
            </tr>
        </table>

        <p>Thank you for keeping the records up to date.</p>
        <br>
        <p><em>Best regards,</em><br><strong>Support Team</strong></p>
    </body>
    </html>
    """
    
    # Create the message container
    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject

    # Attach the HTML body to the email message
    msg.attach(MIMEText(body, "html"))

    try:
        # Set up the SMTP server and send the email
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(from_email, from_password)
        server.send_message(msg)
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")