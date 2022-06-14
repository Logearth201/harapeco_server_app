import random, string, json
from email.mime.text import MIMEText
from email.utils import formatdate
import smtplib
import re, base64, io, traceback, os

# GCPの設定はglobalで保存
bucket_name = "kanachan_test"
gcp_json_pos = "/Users/iwata/Desktop/gcp_secret/kanachan-526d6018653f.json"


# ランダム文字列
def randomname(n):
   randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
   return ''.join(randlst)


# メール転送
def send_mail(body, subject, to_address):
    from_address = "kanatalk@career-world.net"
    password = "Tesgeowqo1!0fe"

    content = MIMEText(body)
    content["Subject"] = subject
    content["From"] = from_address
    content["To"] = to_address
    content["Date"] = formatdate()

    smtpobj = smtplib.SMTP("logweb.sakura.ne.jp", 587)
    smtpobj.ehlo()
    smtpobj.starttls()
    smtpobj.ehlo()
    smtpobj.login(from_address, password)
    smtpobj.sendmail(from_address, to_address, content.as_string())
    smtpobj.close()


# 制御文字形式に
# {1}{2}の中にいろんな制御文を入れること
# 画像編集機能をなめまわすため
def create_message(str, list):
    # listをなめまわす
    order = -1

    for item in list:
        # 数値じゃないなんてこんなの、加奈ちゃんじゃない！
        if not re.match(r'^[0-9]]$', item.number):
            continue

        if item.code == 1:
            # hrefUnit
            if not re.match(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-]+', item.content):
                continue

            str = str.replace("`" + item.number + "`", "<a href='" +
                              item.content + "' target='_blank' onclick='return confirm(" + item.content + ")' ></a>")
        elif item.code == 2:
            # imageUnit
            str = str.replace("`" + item.number + "`", "<a href='" + item.content + "'><img src='" + item.content +
                              "' alt='" + item.content + "' ></a>")
        elif item.code == 3:
            # expressUnit
            str = str.replace("`" + item.number + "`", "<a href='" + item.content +
                              "' target='_blank'></a>")
        else:
            pass
    return str



