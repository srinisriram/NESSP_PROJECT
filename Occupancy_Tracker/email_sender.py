import datetime
import os
import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

from Occupancy_Tracker.constants import ENTER_LOG_FILE_NAME, WEEKLY_LOG_FILE_NAME, MONTHLY_LOG_FILE_NAME, HOUR, MINUTE, DAY, DATE
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
        receiver_email = "adityaanand.muz@gmail.com, srinivassriram06@gmail.com, raja.muz@gmail.com, abhisar.muz@gmail.com"
        password = "LearnIOT06!"
        msg['From'] = 'maskdetector101@gmail.com'
        msg['To'] = "adityaanand.muz@gmail.com, srinivassriram06@gmail.com, raja.muz@gmail.com, abhisar.muz@gmail.com"
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = 'Here is the Occupancy List for Today'

        body = 'Dear Board Members,\n\nPlease find the attached daily occupancy tracker sheet for your reference.\n\nThe total amount of people that visited today: {}\n\nThanks and regards,\nPI_Defense'.format(
            numofpeo - 1)

        attachmentsList = [enter_excel_sheet]
        if day == DAY:
            attachmentsList.append(weekly_enter_excel)
        if date == DATE:
            attachmentsList.append(monthly_enter_excel)
        for each_file_path in attachmentsList:
            file_name = each_file_path.split("/")[-1]
            part = MIMEBase('application', "octet-stream")
            part.set_payload(open(each_file_path, "rb").read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment', filename=file_name)
            msg.attach(part)

        if len(attachmentsList) == 1:
            body = 'Dear Board Members,\n\nPlease find the attached daily occupancy tracker sheet for your reference.\n\nThe total amount of people that visited today: {}\n\nThanks and regards,\nPI_Defense'.format(
                numofpeo - 1)
        elif len(attachmentsList) == 2:
            body = 'Dear Board Members,\n\nPlease find the attached daily and weekly occupancy tracker sheet for your reference.\n\nThe total amount of people that visited today: {}\n\nThanks and regards,\nPI_Defense'.format(
                numofpeo - 1)
        elif len(attachmentsList) == 3:
            body = 'Dear Board Members,\n\nPlease find the attached daily, weekly and monthly occupancy tracker sheet for your reference.\n\nThe total amount of people that visited today: {}\n\nThanks and regards,\nPI_Defense'.format(
                numofpeo - 1)

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

    @classmethod
    def send_email_with_time(cls, hour=HOUR, minute=MINUTE):
        """
        This methods sends an email on a certain time that is set in constants.
        :param hour:
        :param minute:
        :return:
        """
        emailSent = False
        while True:
            now = datetime.datetime.now().time()
            Logger.logger().debug("Current Time: ", now)
            hr = now.hour
            while hr == hour:
                now = datetime.datetime.now().time()
                min = now.minute
                if min == minute:
                    if emailSent == False:
                        lines = []
                        day = datetime.datetime.now().strftime("%A")
                        with open(ENTER_LOG_FILE_NAME, "r") as dailyfile:
                            for line in dailyfile:
                                lines.append(line)
                        with open(WEEKLY_LOG_FILE_NAME, "a") as weeklyfile:
                            try:
                                lines.pop(0)
                            except:
                                pass
                            for line in lines:
                                weeklyfile.write(line)
                        lines.clear()
                        if day == DAY:
                            with open(WEEKLY_LOG_FILE_NAME, "r") as weeklyfile:
                                for line in weeklyfile:
                                    lines.append(line)
                            with open(MONTHLY_LOG_FILE_NAME, "a") as monthlyfile:
                                lines.pop(0)
                                for line in lines:
                                    monthlyfile.write(line)
                                lines.clear()
                        Logger.logger().info("[INFO] Sending Email...")
                        EmailSender.email_send()
                        Logger.logger().info("[INFO] Email Sent...")
                        Logger.logger().info("[INFO] Clearing file(s)...")
                        EmailSender.clear_all_files()
                        emailSent = True

    @classmethod
    def clear_all_files(self):
        """
        This method clears all the files depending on what day it is.
        :return:
        """
        day = datetime.datetime.now().strftime("%A")
        date = datetime.date.today().day

        file = open(ENTER_LOG_FILE_NAME, "r+")
        file.truncate(0)
        file.close()
        if day == DAY:
            file1 = open(WEEKLY_LOG_FILE_NAME, "r+")
            file1.truncate(0)
            file1.close()
        if date == DATE:
            file2 = open(MONTHLY_LOG_FILE_NAME, "r+")
            file2.truncate(0)
            file2.close()
