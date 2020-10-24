import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

from Occupancy_Tracker.constants import OCCUPATION_LOG


class CrashReport:
    """
        This class composes and sends an email when the occupancy crashes.
    """

    @classmethod
    def email_send(cls, occupation_log=OCCUPATION_LOG):
        """
        This method sends an email 
        :param occupation_log: 
        :return: 
        """
        msg = MIMEMultipart()
        sender_email = "maskdetector101@gmail.com"
        receiver_email = "adityaanand.muz@gmail.com, srinivassriram06@gmail.com, raja.muz@gmail.com, abhisar.muz@gmail.com"
        password = "LearnIOT06!"
        msg['From'] = 'maskdetector101@gmail.com'
        msg['To'] = "adityaanand.muz@gmail.com, srinivassriram06@gmail.com, raja.muz@gmail.com, abhisar.muz@gmail.com"
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = 'The Occupancy Tracker has crashed!'

        body = "The Occupancy Tracker has crashed and the occupation log is attached below."

        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(occupation_log, "rb").read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment', filename=occupation_log)
        msg.attach(part)

        msg.attach(MIMEText(body, "plain"))
        context = ssl.create_default_context()
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email.split(","), msg.as_string())
        except Exception as e:
            print(type(e).__name__ + ': ' + str(e))
        else:
            email_sent_status = True
        finally:
            return email_sent_status


if __name__ == '__main__':
    CrashReport.email_send()
