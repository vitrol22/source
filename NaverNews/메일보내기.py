import os
import smtplib

from email import encoders
from email.utils import formataddr
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pymysql
import pandas as pd


class NewsMail(object):
    ENCODING = "UTF-8"

    host = None
    port = None
    from_addr = None
    to_addrs = None
    message = None

    debug = False
    _isLogin = False
    _existAttachments = False

    def __init__(self, address: tuple, from_addr: str, to_addrs: list, debug=False, **kwargs):
        self.host, self.port = address
        self.from_addr = from_addr
        self.to_addrs = to_addrs

        # 인증 계정
        if kwargs.get("vitrolee") is not None:
            self.setAuth(kwargs.get("vitrolee"), kwargs.get("yylridasalpqwpmk"))

        # 디버그 모드
        self.debug = debug is not False

        # 첨부파일로 전송 불가능한 확장자
        self.blocked_extensions = (".ade",".adp",".apk",".appx",".appxbundle",".bat",".cab",".chm",".cmd",".com",".cpl",
            ".dll",".dmg",".exe",".hta",".ins",".isp",".iso",".jar",".js",".jse",".lib",".lnk",".mde",".msc",".msi",
            ".msix",".msixbundle",".msp",".mst",".nsh",".pif",".ps1",".scr",".sct",".shb",".sys",".vb",".vbe",".vbs",
            ".vxd",".wsc",".wsf",".wsh",)

    def setAuth(self, username, password):
        self._isLogin = True
        self.username = "vitrolee"  # username
        self.password = "yylridasalpqwpmk"  # password

    def setMail(self, subject, body, body_type="plain", attachments=None):
        """
        Content-Type:
            - multipart/alternative: 평문 텍스트와 HTML과 같이 다른 포맷을 함께 보낸 메시지
            - multipart/mixed: 첨부파일이 포함된 메시지

        REF:
            - https://ko.wikipedia.org/wiki/MIME#Content-Type
        """
        # 첨부파일 여부
        self._existAttachments = attachments is not None
        self.content_sub_type = "mixed" if self._existAttachments else "alternative"

        # 메일 콘텐츠 설정
        self.message = MIMEMultipart(self.content_sub_type)

        # 받는 사람 주소 설정. [( 이름 <이메일> )]
        self.FROM_ADDR_FMT = formataddr(self.from_addr)
        self.TO_ADDRS_FMT = ",".join([formataddr(addr) for addr in self.to_addrs])

        # 메일 헤더 설정
        self.message.set_charset(self.ENCODING)
        self.message["From"] = self.FROM_ADDR_FMT
        self.message["To"] = self.TO_ADDRS_FMT
        self.message["Subject"] = subject

        # 메일 콘텐츠 - 내용
        self.message.attach(MIMEText(body, body_type, self.ENCODING))

        # 메일 콘텐츠 - 첨부파일
        if self._existAttachments:
            self._attach_files(attachments)

        return self

    def _attach_files(self, attachments):
        """
        Content-disposition:
            - 파일명 지정
        MIME type:
            - application/octect-stream: Binary Data
        REF:
            - https://www.freeformatter.com/mime-types-list.html
        """

        for attachment in attachments:
            attach_binary = MIMEBase("application", "octect-stream")
            try:
                binary = open(attachment, "rb").read()  # read file to bytes

                attach_binary.set_payload(binary)
                encoders.encode_base64(
                    attach_binary
                )  # Content-Transfer-Encoding: base64

                filename = os.path.basename(attachment)
                attach_binary.add_header(
                    "Content-Disposition",
                    "attachment",
                    filename=(self.ENCODING, "", filename),
                )

                self.message.attach(attach_binary)
            except Exception as e:
                print(e)

    def send(self):
        session = None
        try:
            # 메일 세션 생성
            session = smtplib.SMTP(self.host, self.port)
            session.set_debuglevel(self.debug)
            session.ehlo()

            # SMTP 서버 계정 인증
            if self._isLogin:
                session.starttls()
                session.login(self.username, self.password)

            # 메일 발송
            session.sendmail(
                self.FROM_ADDR_FMT, self.TO_ADDRS_FMT, self.message.as_string()
            )
            print(to_addrs[0][0] + "(" + to_addrs[0][1] + ") 에게 "  + "Successfully sent the mail!!!" )

        except Exception as e:
            print(e)
        finally:
            if session is not None:
                session.quit()


# https://heodolf.tistory.com/100
# SMTP 서버 정보
smtp_address = ("smtp.gmail.com", 587)  # SMTP 서버 호스트, 포트

# SMTP 계정 정보
username = "vitrolee@gmail.com"
# Gmail 계정
password = "yylridasalpqwpmk"
# Gmail 앱 비밀번호

# 메일 송/수신자 정보
from_addr = ("이정로", "vitrolee@gmail.com")  # 보내는 사람 주소. (이름, 이메일)

# 메일 제목
subject = "Windows News를 전달드립니다."

# 메일 내용
sql0 ='' 
# # "<!DOCTYPE html></p><h3>새해 복 많이 받으시기 바랍니다.</h3></p><br>한 해동안 보내주신 성원에 감사드립니다. 한 해를 마무하면서 올해에 창호업계에 있었던 뉴스를 정리하였습니다.<br> 본 메일은 창호업계의 원활한 정보제공을 위하여 일정기간동안의 뉴스를 보내는 서비스입니다. 현재는 시범적인 서비스입니다. <br> <br> 기사제목을 누르면 바로 기사내용을 확인할 수 있습니다. <br> <br>사용 중에 불편한 사항과 개선할 필요성이 있는 부분에 대한 의견을 요청드립니다. 아울러 다른 뉴스 서비스도 필요할까요.<br> 불필요한 내용이라면 발송을 중지하겠습니다.<br><br>"
sql1 = "<html><head><title>Windows News</title></head><body><!-- 헤더 부분 --><header><center><h1><p style='line-height: 1px;'>Windows News</p></h1><h3><p style='line-height: 1x;'>한국창호협회</p></h3></center><hr align='center' width=20%></hr></header><br><br><!-- 본문 부분 --><section><article><center>"

sql2 = "<style type='text/css'>.tg  {border-collapse:collapse;border-color:#9ABAD9;border-spacing:0;}.tg td{background-color:#EBF5FF;border-color:#9ABAD9;border-style:solid;border-width:1px;color:#444;  font-family:Arial, sans-serif;font-size:14px;overflow:hidden;padding:1px 20px;word-break:normal;}.tg th{background-color:#409cff;border-color:#9ABAD9;border-style:solid;border-width:1px;color:#fff;  font-family:Arial, sans-serif;font-size:14px;font-weight:normal;overflow:hidden;padding:1px 20px;word-break:normal;}.tg .tg-r8mc{background-color:#D2E4FC;border-color:inherit;color:#00F;text-align:left;text-decoration:underline;vertical-align:top}.tg .tg-c3ow{border-color:inherit;text-align:left;vertical-align:top}.tg .tg-jn94{background-color:#D2E4FC;border-color:inherit;text-align:left;vertical-align:bottom}.tg .tg-za14{border-color:inherit;text-align:left;vertical-align:bottom}.tg .tg-wucc{border-color:inherit;color:#00F;text-align:left;text-decoration:underline;vertical-align:top}</style>"

sql3 = "<table class='tg'>"
sql4 = "<thead><tr><th class='tg-c3ow'>날자</th><th class='tg-c3ow'>언론사</th><th class='tg-c3ow'>기사제목</th></tr></thead>"

sql5 = "<tbody>"
sql6 = ""  # <tr><td class='tg-jn94'>2021-12-20</td><td class='tg-jn94'><center>헤럴드경제</center></td>    <td class='tg-r8mc'><a href='http://news.heraldcorp.com/view.php?ud=20211220000456'><span style='text-decoration:underline;color:blue'>LX하우시스, 종합 실내리모델링 ‘성큼’</span></a></td></tr>"

conn = pymysql.connect(host="127.0.0.1", user="root", passwd="JRLEE", db="wnews")

cur = conn.cursor()
cur.execute("use wnews")
#############################################################################################################
sql = 'select cnews_date, info_press, naver_link, news_title from wwindows'
sql+= ' where news_link is not null and related="1" '
sql+= ' and cnews_date >= "2022-01-01" order by cnews_date desc'
#############################################################################################################
# 기간설정이 필요
cur.execute(sql)
rs = cur.fetchall()
result = pd.DataFrame(rs)

tablebody = ""
for kk in range(len(result)):
    cnewsdate = result.iat[kk, 0]
    infopress = result.iat[kk, 1]
    naverlink = result.iat[kk, 2]
    newstitle = result.iat[kk, 3]
    # cnewslink=result.iat[kk,2]

    tablebody += f"<tr><td class='tg-jn94'>{cnewsdate}</td><td class='tg-jn94'><center>{infopress}</center></td>    <td class='tg-r8mc'><a href='{naverlink}'><span style='text-decoration:underline;color:blue'><left>{newstitle}</left></span></a></td></tr>"

    # ttablebody=ttablebody+tablebody
sql7 = "</tbody></table></center><br><br><hr size='10' align='center' width=55% noshade='noshade'></hr><!-- 사이트 정보 부분 --><footer><center><small>한국창호협회 vitrolee@gmail.com : 협회밴드 <em class='bandAddressText'> https://band.us/@kwindows</small></center> </footer></body></html>"

# <!-- <small> https://band.us/plugin/share?body=<band.us/@kwindows>

body = sql0 + sql1 + sql2 + sql3 + sql4 + sql5 + sql6 + tablebody + sql7


# 첨부파일
attachments = [
    # os.path.join( os.getcwd(), 'storage', 'example.py' )
    # os.path.join(os.chdir(r'C:\Users\JRLee\Downloads\source\report', 'storage', 'WWindows.xlsx' ))
]

if __name__ == "__main__":

    conn = pymysql.connect(host="127.0.0.1", user="root", passwd="JRLEE", db="wnews")

    cur = conn.cursor()
    cur.execute("use wnews")
    #############################################################################################################
    #sql="select 이름, 메일주소 from email_address" #  where 분류='beta'""
    sql = "select 이름, 메일주소 from email_address where 이름='이정로'"
    #############################################################################################################
    cur.execute(sql)

    rs = cur.fetchall()
    result = pd.DataFrame(rs)
    to_addrs = ""  # ('이정로', 'vitrolee@naver.com')

    for kk in range(0, len(result)):
        to_addrs = [("존경하는 " + result.iat[kk, 0] + "님", result.iat[kk, 1])]
        mail = NewsMail(smtp_address, from_addr, to_addrs, debug=False)
        mail.setAuth(username, password)
        mail.setMail(subject, body, "html", attachments=attachments)
        mail.send()
