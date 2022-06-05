
import datetime
import smtplib


from email import encoders
from email.utils import formataddr
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def sendEmailfunc():
    id = 'vitrolee'
    password = 'GlassWorld2020@'
    sendEmail = 'vitrolee@naver.com'
    today = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    #today=datetime.datetime.now().strftime("%Y%m%d")
    subject = '[' + today + ' 주식추천 종목]-' + str(2) + '개 회사'
    addrs = ['vitrolee@gmail.com']  # send mail list

    # login
    smtp = smtplib.SMTP('smtp.naver.com', 587)
    smtp.ehlo()
    smtp.starttls()
    smtp.login(id, password)

    for addr in addrs:
        # message
        message = MIMEMultipart()
        text="test2"
        message.attach(MIMEText(text, 'html'))

        # Send
        message["From"] = sendEmail
        message["To"] = addr
        message['Subject'] = subject
        smtp.sendmail(sendEmail, addr, message.as_string())

    smtp.quit()

 

 
 
 
if __name__ == "__main__":
    sendEmailfunc()
    #app = QApplication(sys.argv)
    #demo = AppDemo()
    #demo.show()

    try:
        #sys.exit(app.exec_())
        print('예외가 발생했습니다.')
        #Continue
    except SystemExit:
        print("Closing")