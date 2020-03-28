def send_email(to,subject,body): #Send email message
    
    # Import smtplib for the actual sending function
    import smtplib

    # Import the email module
    from email.message import EmailMessage

    #Import email address/password
    f = open('C:/Users/Simon/SkyDrive/Home Stuff/Python/Email Games/Creds.txt')
    creds=f.read().splitlines()
    address=creds[0]
    password=creds[1]
    
    # Create an HTML message
    msg = EmailMessage()
    msg.add_header('Content-Type','text/html')
    msg.set_payload(body)
    msg['Subject']=subject
    msg['From']=address
    msg['To']=to

    #Set up server connection
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    #Login
    server.login(address,password)
    #Send email
    server.send_message(msg)
    server.quit()
