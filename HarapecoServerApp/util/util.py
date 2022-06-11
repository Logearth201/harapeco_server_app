import random, string
from email.mime.text import MIMEText
from email.utils import formatdate
import smtplib
import re, base64, cv2, io, numpy, traceback, os
from google.cloud import storage as gcs

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


# ラウンジ専用フォルダの作成
def creationFolderList(lounge_id):
    pass


# ファイルを保存(GCP)
def file_save(lounge_id, extension, creation_id, base64string):
    # base64がほとんど空の場合は終わり
    if len(base64string) <= 1:
        return {"result": "OK", "is_saved": False}

    # ファイル名の生成
    def gene_file():
        return randomname(100)

    file_name = gene_file()

    try:
        # 保存先ファイル名の設定
        fname = str(lounge_id) + "/" + str(creation_id) + "/" + file_name + "." + extension
        tmp_file_name = "/Users/iwata/Desktop/develop/tmp/" + str(lounge_id) + "ct" + file_name + "." + extension

        # ファイルのBase64デコード
        img_binary = base64.b64decode(base64string)
        image = numpy.frombuffer(img_binary, dtype=numpy.uint8)

        # ファイルの一時保存
        img = cv2.imdecode(image, cv2.IMREAD_UNCHANGED)
        cv2.imwrite(tmp_file_name, img)

        # GCPにアップロード
        client = gcs.Client.from_service_account_json(gcp_json_pos)
        bucket = client.get_bucket(bucket_name)

        blob = gcs.Blob(fname, bucket)
        res = blob.upload_from_filename(tmp_file_name)

        os.remove(tmp_file_name)

        return {"result": "OK", "is_saved": True, "full_path": fname}
    except:
        print("GCP ERRORS!")
        traceback.print_exc()
        return {"result": "NG", "is_saved": False}


def file_delete(file_path):
    try:
        client = gcs.Client.from_service_account_json(gcp_json_pos)
        bucket = client.get_bucket(bucket_name)

        blob = gcs.Blob(file_path, bucket)
        blob.delete()

        return {"result": "OK"}
    except:
        traceback.print_exc()
        return {"result": "NG"}


# ファイルをサーバー(EC3)から読み込む
def file_load(url_base_path):
    return "https://storage.googleapis.com/kanachan_test/" + url_base_path


# CSVファイルの追加処理（画像用）
def csv_add_file(csv_text, file_path):
    # ファイルはバックスラッシュごとに分割
    csv_text_lines = csv_text.split("\\")

    # アップデート文字列は/ごとに分割（/はここで全てオミット）
    csv_update_line = file_path.replace("\\", "")

    # 要素に含むかどうかを判定
    if csv_text_lines in csv_text_lines:
        return csv_text
    else:
        csv_text_lines.append(csv_update_line)
        return "\\".join(csv_text_lines) #pythonのJOINは他言語のとは引数が逆順であることに注意！


# CSVファイルの削除処理(画像用)
def csv_delete_file(csv_text, file_path):
    # ファイルはバックスラッシュごとに分割
    csv_text_lines = csv_text.split("\\")

    # 要素に含むかどうかを判定
    if not (file_path in csv_text_lines):
        return csv_text
    else:
        csv_text_lines.remove(file_path)
        return "\\".join(csv_text_lines)  # pythonのJOINは他言語のとは引数が逆順であることに注意！



