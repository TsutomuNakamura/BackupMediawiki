import smtplib

class Mail:

    def __init__(self, config):
        self.recipient_address      = config['mail_recipient_address']
        self.recipient_name         = config['mail_recipient_name'] or ""
        self.sender_address         = config['mail_sender_address']
        self.sender_name            = config['mail_sender_name'] or ""
        self.mta_host               = config['mail_mta_host']
        self.mta_port               = config['mail_mta_port']
        self.sender_auth_password   = config['mail_sender_auth_password']

        self.smtp                   = smtplib.SMTP(self.mta_host, self.mta_port)


    def send(self, subject, message):
        mail_body = "From: " + self.sender_name + "<" + self.sender_address + ">\r\n" \
                + "To: " + self.recipient_name + "<" + self.recipient_address + ">\r\n" \
                + "Subject: " + subject + "\r\n" \
                + "\r\n" \
                + "An error message is as below." \
                + "\r\n\r\n" \
                + message

        self.smtp.sendmail(self.sender_address, self.recipient_address, mail_body)

