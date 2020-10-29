import datetime
import os
import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

from constants import ENTER_LOG_FILE_NAME, PEER_ENTER_LOG_FILE_NAME, EXIT_LOG_FILE_NAME, \
    PEER_EXIT_LOG_FILE_NAME, \
    WEEKLY_LOG_FILE_NAME, MONTHLY_LOG_FILE_NAME, DAY, DATE, CLEAR_FILES
from logger import Logger


class EmailSender:
    """
    This class composes and sends an email.
    """

    @classmethod
    def email_send(cls, enter_csv_sheet=ENTER_LOG_FILE_NAME, exit_csv_sheet=EXIT_LOG_FILE_NAME,
                   weekly_enter_csv=WEEKLY_LOG_FILE_NAME,
                   monthly_enter_csv=MONTHLY_LOG_FILE_NAME):
        """
        This method sends an email with the provided credentials.
        :param monthly_enter_csv: str
        :param weekly_enter_csv: str
        :param enter_csv_sheet: str
        :param exit_csv_sheet: str
        :return:
        """
        email_sent_status = False

        day = datetime.datetime.now().strftime("%A")
        date = datetime.date.today().day

        Logger.logger().debug("Running send_email function")
        enter_csv_sheet = os.path.join(os.path.dirname(__file__), enter_csv_sheet)
        exit_csv_sheet = os.path.join(os.path.dirname(__file__), exit_csv_sheet)
        weekly_enter_csv = os.path.join(os.path.dirname(__file__), weekly_enter_csv)
        monthly_enter_csv = os.path.join(os.path.dirname(__file__), monthly_enter_csv)
        Logger.logger().debug(enter_csv_sheet)
        Logger.logger().debug(exit_csv_sheet)
        Logger.logger().debug(weekly_enter_csv)
        Logger.logger().debug(monthly_enter_csv)
        msg = MIMEMultipart()
        sender_email = "maskdetector101@gmail.com"
        receiver_email = "adityaanand.muz@gmail.com, srinivassriram06@gmail.com, raja.muz@gmail.com, abhisar.muz@gmail.com"
        password = "LearnIOT06!"  # keyring.get_password("gmail", "maskdetector101@gmail.com")
        msg['From'] = 'maskdetector101@gmail.com'
        msg['To'] = "adityaanand.muz@gmail.com, srinivassriram06@gmail.com, raja.muz@gmail.com, abhisar.muz@gmail.com"
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = 'Here is the Occupancy List for Today'

        total_count_of_people_entered = cls.get_count_file(enter_csv_sheet)
        total_count_of_people_exited = cls.get_count_file(exit_csv_sheet)
        body = 'Dear Board Members,\n'

        attachmentsList = [enter_csv_sheet, exit_csv_sheet]
        if day == DAY:
            attachmentsList.append(weekly_enter_csv)
        if date == DATE:
            attachmentsList.append(monthly_enter_csv)
        for each_file_path in attachmentsList:
            file_name = each_file_path.split("/")[-1]
            part = MIMEBase('application', "octet-stream")
            part.set_payload(open(each_file_path, "rb").read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment', filename=file_name)
            msg.attach(part)

        if len(attachmentsList) == 1:
            body = body + 'Please find the attached daily occupancy tracker sheet for your reference.\n'
        elif len(attachmentsList) == 2:
            body = body + 'Please find the attached daily and weekly occupancy tracker sheet for your reference.\n'
        elif len(attachmentsList) == 3:
            body = body + 'Please find the attached daily, weekly and monthly occupancy tracker sheet for your reference.\n'

        if total_count_of_people_entered >= total_count_of_people_exited:
            body = body + 'Total People that visited the temple today: {}\n'.format(total_count_of_people_entered)
        else:
            body = body + 'Total People that visited the temple today: {}\n'.format(total_count_of_people_exited)

        number_of_unmonitored_people = total_count_of_people_entered - total_count_of_people_exited

        if number_of_unmonitored_people > 0:
            body = body + 'Approximately {} people exited through unmonitored doors today.\n'.format(
                number_of_unmonitored_people)
        elif number_of_unmonitored_people < 0:
            body = body + 'Approximately {} people entered through unmonitored doors today.\n'.format(
                abs(number_of_unmonitored_people))
        else:
            pass

        body = body + "*Note: The results from the occupancy tracker are 98% accurate as it usually does not count little infants/toddlers.*\n"
        body = body + "\nThanks and regards,\nPI_Defense"

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
    def format_and_send_email(cls, local_enter_csv_sheet=ENTER_LOG_FILE_NAME,
                              peer_enter_csv_sheet=PEER_ENTER_LOG_FILE_NAME, local_exit_csv_sheet=EXIT_LOG_FILE_NAME,
                              peer_exit_csv_sheet=PEER_EXIT_LOG_FILE_NAME, weekly_enter_csv=WEEKLY_LOG_FILE_NAME,
                              monthly_enter_csv=MONTHLY_LOG_FILE_NAME):
        """
        This method combines the local and peer enter and exit csv file to create one pair, enter and exit csv file. 
        Copies the enter csv to the weekly csv and the weekly csv to monthly csv depending what day and day it is.
        :param local_enter_csv_sheet: 
        :param peer_enter_csv_sheet: 
        :param local_exit_csv_sheet: 
        :param peer_exit_csv_sheet: 
        :param weekly_enter_csv: 
        :param monthly_enter_csv: 
        :return: 
        """
        Logger.logger().info("[INFO] Merging Files...")
        cls.merge_files(file1=local_enter_csv_sheet, file2=peer_enter_csv_sheet)
        cls.merge_files(file1=local_exit_csv_sheet, file2=peer_exit_csv_sheet)
        day = datetime.datetime.now().strftime("%A")
        lines = []
        dailyfile = open(local_enter_csv_sheet, "r")
        for line in dailyfile:
            lines.append(line)
        dailyfile.close()
        weeklyfile = open(weekly_enter_csv, "a")
        try:
            lines.pop(0)
        except Exception as e:
            Logger.logger().info(type(e).__name__ + ': ' + str(e))
            pass
        for line in lines:
            weeklyfile.write(line)
        weeklyfile.close()
        lines.clear()
        if day == DAY:
            weeklyfile = open(weekly_enter_csv, "r")
            for line in weeklyfile:
                lines.append(line)
            weeklyfile.close()
            monthlyfile = open(monthly_enter_csv, "a")
            try:
                lines.pop(0)
            except Exception as e:
                Logger.logger().info(type(e).__name__ + ': ' + str(e))
                pass
            for line in lines:
                monthlyfile.write(line)
            lines.clear()
            monthlyfile.close()
        Logger.logger().info("[INFO] Sending Email...")
        cls.email_send()
        Logger.logger().info("[INFO] Email Sent...")
        if CLEAR_FILES:
            Logger.logger().info("[INFO] Clearing file(s)...")
            # cls.clear_all_files()

    @classmethod
    def clear_all_files(cls):
        """
        This method clears all the files depending on what day it is.
        :return:
        """
        day = datetime.datetime.now().strftime("%A")
        date = datetime.date.today().day

        file = open(ENTER_LOG_FILE_NAME, "r+")
        file.truncate(0)
        file.close()
        file = open(EXIT_LOG_FILE_NAME, "r+")
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

    @classmethod
    def merge_files(cls, file1, file2):
        f = open(file1, "r")
        content = f.readlines()
        f.close()
        t = open(file2)
        file_2_content = t.readlines()
        file_2_content = file_2_content[1:]
        for i in file_2_content:
            content.append(str(i))
        t.close()
        f = open(file1, "w")
        for i in content:
            f.write(i)
        f.close()

    @classmethod
    def get_count_file(cls, filename):
        f = open(filename, "r")
        content = f.readlines()
        count = len(content)
        if content[0] == "Year,Month,Day,Time,Direction\n":
            count -= 1
        return count


if __name__ == '__main__':
    EmailSender.format_and_send_email()
