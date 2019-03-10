import os
import smtplib
import email, smtplib, ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

sender_email = "mail@gmail.com"
password = "password"

class opencsv:
    isEmpty = False
    def __init__(self,filename,email,roll):
        self.filename = filename
        self.file = open(filename,"a+")
        self.email = email
        self.roll = roll

    def append(self,data):
        for entry in data:
            self.file.write(entry)
            if entry is data[-1]:
                self.file.write("\n")
            else:
                self.file.write(",")

    def bulkappend(self,listoflists):
        for roll, lists in listoflists:
            self.append(lists)

    def __del__(self):
        self.file.close()
        if not isEmpty:
            message = MIMEMultipart()
            message["From"] = sender_email
            message["To"] = self.email
            message["Subject"] = "Your result for " + {self.roll}+" is here"
            body = ""
            message.attach(MIMEText(body, "plain"))
            encoders.encode_base64(part)
            with open(self.filename, "rb") as attachment:
                # Add file as application/octet-stream
                # Email client can usually download this automatically as attachment
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
            part.add_header(
                "Content-Disposition",
                "attachment; filename= "+{self.roll}+".csv",
                )
            message.attach(part)
            text = message.as_string()
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, self.email, text)
            os.remove(self.filename)
