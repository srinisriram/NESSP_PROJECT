import datetime
import os
import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

from Occupancy_Tracker.constants import ENTER_LOG_FILE_NAME, WEEKLY_LOG_FILE_NAME, MONTHLY_LOG_FILE_NAME, HOUR, MINUTE
from Occupancy_Tracker.logger import Logger


class EmailSender:
    """
    This class composes and sends an email.
    """

    @classmethod
    def email_send(cls, enter_excel_sheet=ENTER_LOG_FILE_NAME, weekly_enter_excel=WEEKLY_LOG_FILE_NAME,
                   monthly_enter_excel=MONTHLY_LOG_FILE_NAME):
        """
        This method sends an email with the provided credentials.
        :param monthly_enter_excel: str
        :param weekly_enter_excel: str
        :param enter_excel_sheet: str
        :return:
        """
        email_sent_status = False

        file = open("enter_file.csv")
        numofpeo = len(file.readlines())
        file.close()

        day = datetime.datetime.now().strftime("%A")
        date = datetime.date.today().day

        Logger.logger().debug("Running send_email function")
        enter_excel_sheet = os.path.join(os.path.dirname(__file__), enter_excel_sheet)
        weekly_enter_excel = os.path.join(os.path.dirname(__file__), weekly_enter_excel)
        monthly_enter_excel = os.path.join(os.path.dirname(__file__), monthly_enter_excel)
        Logger.logger().debug(enter_excel_sheet)
        Logger.logger().debug(weekly_enter_excel)
        Logger.logger().debug(monthly_enter_excel)
        msg = MIMEMultipart()
        sender_email = "maskdetector101@gmail.com"
        receiver_email = "srinivassriram06@gmail.com"
        password = "LearnIOT06!"
        msg['From'] = 'maskdetector101@gmail.com'
        msg['To'] = ["adityaanand.muz@gmail.com", "srinivassriram06@gmail.com", "raja.muz@gmail.com",
                     "abhisar.muz@gmail.com"]
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = 'Here is the Occupancy List for Today'

        body = 'Dear Board Members,\n\nPlease find the attached daily occupancy tracker sheet for your reference.\n\nThe total amount of people that visited today:{}\n\nThanks and regards,\nPI_Defense'.format(
            numofpeo - 1)

        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(enter_excel_sheet, "rb").read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="{}"'.format(enter_excel_sheet))
        msg.attach(part)

        if day == "Sunday":
            part2 = MIMEBase('application', "octet-stream")
            part2.set_payload(open(weekly_enter_excel, "rb").read())
            encoders.encode_base64(part2)
            part2.add_header('Content-Disposition', 'attachment; filename="{}"'.format(weekly_enter_excel))
            body = 'Dear Board Members,\n\nPlease find the attached daily and weekly occupancy tracker sheet for your reference.\n\nThe total amount of people that visited today:{}\n\nThanks and regards,\nPI_Defense'.format(
                numofpeo - 1)
            msg.attach(part2)

        if date == "1":
            part2 = MIMEBase('application', "octet-stream")
            part2.set_payload(open(weekly_enter_excel, "rb").read())
            encoders.encode_base64(part2)
            part2.add_header('Content-Disposition', 'attachment; filename="{}"'.format(weekly_enter_excel))
            msg.attach(part2)

            part3 = MIMEBase('application', "octet-stream")
            part3.set_payload(open(monthly_enter_excel, "rb").read())
            encoders.encode_base64(part3)
            part3.add_header('Content-Disposition', 'attachment; filename="{}"'.format(monthly_enter_excel))
            body = 'Dear Board Members,\n\nPlease find the attached daily, weekly and monthly occupancy tracker sheet for your reference.\n\nThe total amount of people that visited today:{}\n\nThanks and regards,\nPI_Defense'.format(
                numofpeo - 1)
            msg.attach(part3)

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

    @classmethod
    def send_email_with_time(cls, hour=HOUR, minute=MINUTE):
        while True:
            emailSent = False
            now = datetime.now().time()
            Logger.logger().debug("Current Time: ", now)
            hr = now.hour
            while hr == hour:
                now = datetime.now().time()
                min = now.minute
                if min == minute:
                    if emailSent == False:
                        lines = []
                        day = datetime.datetime.now().strftime("%A")
                        date = datetime.date.today().day
                        with open(ENTER_LOG_FILE_NAME, "r") as dailyfile:
                            for line in dailyfile:
                                lines.append(line)
                        with open(WEEKLY_LOG_FILE_NAME, "a") as weeklyfile:
                            lines.pop(0)
                            for line in lines:
                                weeklyfile.write(line)
                        lines.clear()
                        if day == "Sunday":
                            with open(WEEKLY_LOG_FILE_NAME, "a") as weeklyfile:
                                for line in weeklyfile:
                                    lines.append(line)
                            with open(MONTHLY_LOG_FILE_NAME, "a") as monthlyfile:
                                lines.pop(0)
                                for line in lines:
                                    monthlyfile.write(line)
                                lines.clear()
                        if date == "1":
                            dailyfile.truncate(0)
                            weeklyfile.truncate(0)
                            monthlyfile.truncate(0)
                        Logger.logger().info("[INFO] Sending Email...")
                        EmailSender.email_send()
                        Logger.logger().info("[INFO] Email Sent...")
                        emailSent = True
