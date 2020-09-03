import smtplib
import ssl
import os
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from Occupancy_Tracker.constants import ENTER_LOG_FILE_NAME, EXIT_LOG_FILE_NAME
from Occupancy_Tracker.logger import Logger


class EmailSender:
    """
    This class composes and sends an email.
    """

    @classmethod
    def send_email(cls, enter_excel_sheet=ENTER_LOG_FILE_NAME, exit_excel_sheet=EXIT_LOG_FILE_NAME):
        """
        This method sends an email with the provided credentials.
        :param exit_excel_sheet: str
        :param enter_excel_sheet: str
        :return:
        """
        email_sent_status = False

        Logger.logger().debug("Running send_email function")
        enter_excel_sheet = os.path.join(os.path.dirname(__file__), enter_excel_sheet)
        exit_excel_sheet = os.path.join(os.path.dirname(__file__), exit_excel_sheet)
        Logger.logger().debug(enter_excel_sheet)
        Logger.logger().debug(exit_excel_sheet)
        msg = MIMEMultipart()
        sender_email = "maskdetector101@gmail.com"
        receiver_email = "srinivassriram06@gmail.com"
        password = "LearnIOT06!"
        body = 'Here is an excel sheet which contains the attendance sheet for today'
        msg['From'] = 'maskdetector101@gmail.com'
        msg['To'] = 'srinivassriram06@gmail.com'
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = 'Here is the attendance list for today'

        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(enter_excel_sheet, "rb").read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="enter_file.xlsx"')
        part2 = MIMEBase('application', "octet-stream")
        part2.set_payload(open(exit_excel_sheet, "rb").read())
        encoders.encode_base64(part2)
        part2.add_header('Content-Disposition', 'attachment; filename="exit_file.xlsx"')
        msg.attach(part)
        msg.attach(part2)
        msg.attach(MIMEText(body, "plain"))
        context = ssl.create_default_context()
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, msg.as_string())
        except Exception as e:
            print(type(e).__name__ + ': ' + str(e))
        else:
            email_sent_status = True
        finally:
            return email_sent_status
